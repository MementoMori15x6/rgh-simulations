"""
STAGE 3C/4 FAST: same logic as before, but with local_entropy_grid
(vectorized, verified exact match) replacing the per-cell Python loops
that made the full run intractable within a reasonable time budget.

No logic has changed -- only how entropy is computed. Signature lookup,
settlement filter definition, pattern-persistence restab criterion,
targeted vs exact-rate-matched shuffled null: all identical to the
validated design.
"""

import numpy as np
import random
import statistics
import math
from collections import defaultdict, Counter

N_ROWS, N_COLS = 40, 40
STEPS = 150
N_SEEDS = 30
WINDOW = 1
K_SHORT = 3
K_LONG = 15
MAX_SPEED = 1
SEARCH_RADIUS = K_LONG * MAX_SPEED
INTERVENE_THRESHOLD = 0.55
SOUP_DENSITY = 0.35
LOCAL_SETTLE_WINDOW = 8
LOCAL_SETTLE_TOLERANCE = 0.15

def step(grid):
    neighbor_count = sum(
        np.roll(np.roll(grid, dx, axis=0), dy, axis=1)
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        if (dx, dy) != (0, 0)
    )
    return (((grid == 1) & ((neighbor_count == 2) | (neighbor_count == 3))) |
            ((grid == 0) & (neighbor_count == 3))).astype(int)

def is_trivial(grid):
    return grid.sum() == 0 or grid.sum() == grid.size

def random_soup(rng, density=SOUP_DENSITY):
    return np.array([[1 if rng.random() < density else 0 for _ in range(N_COLS)] for _ in range(N_ROWS)])

def local_entropy_grid(grid, window=WINDOW):
    win_size = (2 * window + 1) ** 2
    count_ones = np.zeros_like(grid, dtype=float)
    for dr in range(-window, window + 1):
        for dc in range(-window, window + 1):
            count_ones += np.roll(np.roll(grid, dr, axis=0), dc, axis=1)
    p1 = count_ones / win_size
    p0 = 1.0 - p1
    with np.errstate(divide='ignore', invalid='ignore'):
        term1 = np.where(p1 > 0, -p1 * np.log2(p1), 0.0)
        term0 = np.where(p0 > 0, -p0 * np.log2(p0), 0.0)
    return term1 + term0

def signature(grid, r, c, window=WINDOW):
    n_rows, n_cols = grid.shape
    vals = []
    for dr in range(-window, window+1):
        for dc in range(-window, window+1):
            vals.append(int(grid[(r+dr) % n_rows, (c+dc) % n_cols]))
    return tuple(vals)

def E_mask(grid):
    neighbor_count = sum(
        np.roll(np.roll(grid, dx, axis=0), dy, axis=1)
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        if (dx, dy) != (0, 0)
    )
    return (grid == 1) & (neighbor_count > 0) & (neighbor_count < 8)

def pattern_reappears_nearby(grid, center_r, center_c, target_pattern, radius, window=WINDOW):
    n_rows, n_cols = grid.shape
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            rr = (center_r + dr) % n_rows
            cc = (center_c + dc) % n_cols
            if signature(grid, rr, cc, window) == target_pattern:
                return True
    return False

def reversed_signature(sig):
    return tuple(reversed(sig))


def build_dual_memory(n_obs_seeds=30):
    memory = defaultdict(lambda: {"destab": [0, 0], "restab": [0, 0]})

    for seed in range(n_obs_seeds):
        rng = random.Random(seed)
        grid = random_soup(rng)
        trace = []
        entropy_trace = []
        t = 0
        alive = True
        while t < STEPS and alive:
            trace.append(grid.copy())
            entropy_trace.append(local_entropy_grid(grid))
            grid = step(grid)
            alive = not is_trivial(grid)
            t += 1

        n_steps = len(trace)
        entropy_stack = np.stack(entropy_trace)

        for t_idx in range(n_steps):
            if t_idx < LOCAL_SETTLE_WINDOW or t_idx + K_LONG >= n_steps:
                continue

            Gt = trace[t_idx]
            boundary_mask = E_mask(Gt)

            window_slice = entropy_stack[t_idx - LOCAL_SETTLE_WINDOW:t_idx]
            spread = window_slice.max(axis=0) - window_slice.min(axis=0)
            settled_mask = spread <= LOCAL_SETTLE_TOLERANCE

            tag_mask = boundary_mask & settled_mask
            rs, cs = np.where(tag_mask)

            future_grid = trace[t_idx + K_LONG]
            h_now_grid = entropy_stack[t_idx]
            h_short_grid = entropy_stack[t_idx + K_SHORT]

            for r, c in zip(rs.tolist(), cs.tolist()):
                sig = signature(Gt, r, c)
                h_now = h_now_grid[r, c]
                h_short = h_short_grid[r, c]

                if h_short > h_now:
                    memory[sig]["destab"][1] += 1
                else:
                    memory[sig]["destab"][0] += 1

                if pattern_reappears_nearby(future_grid, r, c, sig, SEARCH_RADIUS):
                    memory[sig]["restab"][0] += 1
                else:
                    memory[sig]["restab"][1] += 1

    return memory


def restab_confidence(memory, sig):
    d = memory.get(sig)
    if d is None:
        return 0.0
    ret, off = d["restab"]
    total = ret + off
    return (ret / total) if total > 0 else 0.0


def run_experiment_pair(memory, seed):
    # TARGETED pass
    rng_t = random.Random(seed + 50000)
    grid = random_soup(rng_t)
    entropy_trace = []
    last_settled_value = {}
    t_history = []
    t_records = []
    t_trace = []

    t = 0
    alive = True
    while t < STEPS and alive:
        t_trace.append(grid.copy())
        ent_now = local_entropy_grid(grid)
        entropy_trace.append(ent_now)

        if t >= LOCAL_SETTLE_WINDOW:
            window_arr = np.stack(entropy_trace[t - LOCAL_SETTLE_WINDOW:t])
            spread = window_arr.max(axis=0) - window_arr.min(axis=0)
            settled_mask = spread <= LOCAL_SETTLE_TOLERANCE
        else:
            settled_mask = np.zeros_like(grid, dtype=bool)

        settled_rs, settled_cs = np.where(settled_mask)
        for r, c in zip(settled_rs.tolist(), settled_cs.tolist()):
            last_settled_value[(r, c)] = grid[r, c]

        boundary_mask = E_mask(grid)
        tag_mask = boundary_mask & settled_mask
        rs, cs = np.where(tag_mask)

        grid_next = step(grid)
        step_count = 0
        step_records = []

        for r, c in zip(rs.tolist(), cs.tolist()):
            sig = signature(grid, r, c)
            conf = restab_confidence(memory, sig)
            if conf > INTERVENE_THRESHOLD and rng_t.random() < conf:
                if (r, c) in last_settled_value:
                    grid_next[r, c] = last_settled_value[(r, c)]
                step_records.append(((r, c), sig))
                step_count += 1

        alive = not is_trivial(grid_next)
        grid = grid_next
        t_history.append(step_count)
        t_records.append(step_records)
        t += 1

    # SHUFFLED pass (same seed for base dynamics, decorrelated lookup, rate-matched)
    rng_s = random.Random(seed + 50000)
    grid = random_soup(rng_s)
    entropy_trace = []
    last_settled_value = {}
    s_records = []
    s_trace = []

    t = 0
    alive = True
    while t < STEPS and alive:
        s_trace.append(grid.copy())
        ent_now = local_entropy_grid(grid)
        entropy_trace.append(ent_now)

        if t >= LOCAL_SETTLE_WINDOW:
            window_arr = np.stack(entropy_trace[t - LOCAL_SETTLE_WINDOW:t])
            spread = window_arr.max(axis=0) - window_arr.min(axis=0)
            settled_mask = spread <= LOCAL_SETTLE_TOLERANCE
        else:
            settled_mask = np.zeros_like(grid, dtype=bool)

        settled_rs, settled_cs = np.where(settled_mask)
        for r, c in zip(settled_rs.tolist(), settled_cs.tolist()):
            last_settled_value[(r, c)] = grid[r, c]

        boundary_mask = E_mask(grid)
        tag_mask = boundary_mask & settled_mask
        rs, cs = np.where(tag_mask)

        grid_next = step(grid)
        target_budget = t_history[t] if t < len(t_history) else 0

        triggered = []
        for r, c in zip(rs.tolist(), cs.tolist()):
            sig = signature(grid, r, c)
            lookup_sig = reversed_signature(sig)
            conf = restab_confidence(memory, lookup_sig)
            if conf > INTERVENE_THRESHOLD and rng_s.random() < conf:
                triggered.append(((r, c), sig))

        selected = triggered[:target_budget]
        if len(selected) < target_budget:
            chosen_positions = {s[0] for s in selected}
            eligible = [(r, c) for r, c in zip(rs.tolist(), cs.tolist()) if (r, c) not in chosen_positions]
            needed = target_budget - len(selected)
            if eligible and needed > 0:
                idxs = rng_s.sample(range(len(eligible)), min(needed, len(eligible)))
                for i in idxs:
                    r, c = eligible[i]
                    selected.append(((r, c), signature(grid, r, c)))

        step_records_s = []
        for (r, c), sig in selected:
            if (r, c) in last_settled_value:
                grid_next[r, c] = last_settled_value[(r, c)]
            step_records_s.append(((r, c), sig))

        alive = not is_trivial(grid_next)
        grid = grid_next
        s_records.append(step_records_s)
        t += 1

    def measure_restab_rate(records, trace):
        hits, total = 0, 0
        by_density = defaultdict(lambda: [0, 0])  # density -> [hits, total]
        for step_idx, recs in enumerate(records):
            future_idx = step_idx + K_LONG
            if future_idx < len(trace):
                for (r, c), sig in recs:
                    total += 1
                    density = sum(sig)
                    is_hit = pattern_reappears_nearby(trace[future_idx], r, c, sig, SEARCH_RADIUS)
                    by_density[density][1] += 1
                    if is_hit:
                        hits += 1
                        by_density[density][0] += 1
        return hits, total, dict(by_density)

    t_hits, t_total, t_by_density = measure_restab_rate(t_records, t_trace)
    s_hits, s_total, s_by_density = measure_restab_rate(s_records, s_trace)

    return {
        "targeted_rate": (t_hits / t_total) if t_total > 0 else None,
        "shuffled_rate": (s_hits / s_total) if s_total > 0 else None,
        "targeted_n": t_total,
        "shuffled_n": s_total,
        "targeted_by_density": t_by_density,
        "shuffled_by_density": s_by_density,
    }


if __name__ == "__main__":
    import time
    print("Building 2D dual-tail memory (vectorized, pattern-persistence restab)...")
    t0 = time.time()
    memory = build_dual_memory(n_obs_seeds=N_SEEDS)
    print(f"  Done in {time.time()-t0:.1f}s. {len(memory)} signatures learned.\n")

    print(f"Running TARGETED vs SHUFFLED (exact-rate matched), {N_SEEDS} seeds...")
    t0 = time.time()
    results = [run_experiment_pair(memory, seed) for seed in range(N_SEEDS)]
    print(f"  Done in {time.time()-t0:.1f}s.\n")

    valid = [r for r in results if r["targeted_rate"] is not None and r["shuffled_rate"] is not None]
    print(f"Valid seeds: {len(valid)}/{N_SEEDS}\n")

    if not valid:
        print("No valid comparisons -- interventions never fired.")
    else:
        t_rates = [r["targeted_rate"] for r in valid]
        s_rates = [r["shuffled_rate"] for r in valid]
        t_mean, t_std = statistics.mean(t_rates), statistics.pstdev(t_rates) if len(t_rates) > 1 else 0
        s_mean, s_std = statistics.mean(s_rates), statistics.pstdev(s_rates) if len(s_rates) > 1 else 0

        total_t_n = sum(r["targeted_n"] for r in valid)
        total_s_n = sum(r["shuffled_n"] for r in valid)

        print("=" * 60)
        print("RESTABILIZATION RATE (fraction of interventions where pattern")
        print("reappeared nearby at t+K_LONG)")
        print("=" * 60)
        print(f"TARGETED: mean rate = {t_mean:.4f} (std {t_std:.4f}), n_interventions={total_t_n}")
        print(f"SHUFFLED: mean rate = {s_mean:.4f} (std {s_std:.4f}), n_interventions={total_s_n}")

        diffs = [t - s for t, s in zip(t_rates, s_rates)]
        d_mean = statistics.mean(diffs)
        d_std = statistics.pstdev(diffs) if len(diffs) > 1 else 0.0
        paired_t = d_mean / (d_std / (len(diffs) ** 0.5)) if d_std > 0 else (float('inf') if d_mean != 0 else 0.0)
        print(f"\nPaired diff (targeted-shuffled): {d_mean:+.4f} (std {d_std:.4f})  paired-t={paired_t:.3f}")
        print("(positive = targeted MORE likely to restabilize; |t|>~2 roughly suggestive at n~30)")
