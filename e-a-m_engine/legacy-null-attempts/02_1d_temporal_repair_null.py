"""
DUAL-OUTCOME MEMORY + REPAIR ACTION + MULTI-HORIZON TEST.

Prior versions of A could only ever DESTABILIZE (force a neighbor to 0),
so no experiment using them could show homeostasis -- the action itself
had no capacity to restore anything. This version gives A a real repair
option and tests whether targeted use of it outperforms matched-rate
random use of it.

EXPLICIT CHOICES FLAGGED (not discovered facts):
  - "repair" = overwrite the local window with the most recent window
    this ring position held while NOT flagged as a boundary site.
    This is one reasonable definition of repair. If the result only
    holds for this specific rule, that's a warning sign, not proof.
  - "restabilized" = local entropy at t+K_LONG is within BASELINE_TOLERANCE
    of the pre-boundary baseline entropy at that position.
  - Memory learns BOTH a destabilization tag (short horizon, as before)
    and a restabilization tag (long horizon, new) from the SAME
    unperturbed baseline runs -- nothing is injected to favor either.

Two conditions, matched intervention RATE (same structure validated
in the prior experiment):
  - REPAIR-TARGETED: repairs at signatures whose memory says restabilize
    is the historically likely outcome
  - REPAIR-SHUFFLED: same repair action, same per-step intervention
    count, decorrelated signature lookup

If TARGETED reliably lands closer to the pre-boundary baseline at
K_LONG than SHUFFLED does, that's real evidence for a homeostatic
targeting effect. If not, repair-targeting is decorative -- same
lesson as the destabilization experiment, just tested honestly.
"""

import random
import statistics
import math
from collections import defaultdict, Counter

N = 300
STEPS = 200
RULE = 110
N_SEEDS = 30
WINDOW = 6
K_SHORT = 5
K_LONG = 25
BASELINE_TOLERANCE = 0.05   # tightened after diagnostic: natural entropy mean=0.19, std=0.37;
                             # 0.15 made "restabilized" true ~77% of the time regardless of
                             # intervention -- not discriminative. 0.05 demands an actual
                             # close return, not just "still in the normal low range."
RESTABILIZE_THRESHOLD = 0.55

def rule_table(rule_number):
    bits = [(rule_number >> i) & 1 for i in range(8)]
    table = {}
    for i in range(8):
        left, center, right = (i >> 2) & 1, (i >> 1) & 1, i & 1
        table[(left, center, right)] = bits[i]
    return table

TABLE = rule_table(RULE)

def is_trivial(S):
    return all(b == 0 for b in S) or all(b == 1 for b in S)

def D(S, rng=None):
    if all(b == 0 for b in S):
        S = S.copy()
        pos = rng.randrange(len(S)) if rng is not None else len(S) // 2
        S[pos] = 1
        return S
    return S

def T(S):
    n = len(S)
    return [TABLE[(S[(i-1) % n], S[i], S[(i+1) % n])] for i in range(n)]

def E(S):
    n = len(S)
    return [i for i in range(n) if S[i] == 1 and S[(i+1) % n] == 0]

def P(S):
    return not is_trivial(S)

def local_entropy(S, center, window=WINDOW):
    n = len(S)
    bits = [S[(center + k) % n] for k in range(-window, window + 1)]
    c = Counter(bits)
    total = len(bits)
    ent = 0.0
    for v in c.values():
        p = v / total
        ent -= p * math.log2(p) if p > 0 else 0
    return ent

def signature(S, center, window=WINDOW):
    n = len(S)
    return tuple(S[(center + k) % n] for k in range(-window, window + 1))

def get_window_values(S, center, window=WINDOW):
    """Return the actual bit VALUES in the window (a snapshot), not indices."""
    n = len(S)
    return [S[(center + k) % n] for k in range(-window, window + 1)]

def apply_window_values(S, center, values, window=WINDOW):
    n = len(S)
    for k, v in zip(range(-window, window + 1), values):
        S[(center + k) % n] = v


# ---------- Phase 1: dual-outcome memory from unperturbed baselines ----------
def build_memory(n_obs_seeds=30):
    memory = defaultdict(lambda: {"destab": [0, 0], "restab": [0, 0]})

    for seed in range(n_obs_seeds):
        rng = random.Random(seed)
        S = [0] * N
        trace = []
        t = 0
        alive = True
        while t < STEPS and alive:
            S = D(S, rng=rng)
            S_next = T(S)
            alive = P(S_next)
            S = S_next
            trace.append(S.copy())
            t += 1

        n_steps = len(trace)
        last_nonboundary_entropy = [None] * N

        for t_idx in range(n_steps):
            St = trace[t_idx]
            boundary_sites = set(E(St))
            for pos in range(N):
                if pos not in boundary_sites:
                    last_nonboundary_entropy[pos] = local_entropy(St, pos)

            if t_idx + K_LONG >= n_steps:
                continue

            for site in boundary_sites:
                sig = signature(St, site)
                baseline = last_nonboundary_entropy[site]
                if baseline is None:
                    continue

                h_now = local_entropy(St, site)
                h_short = local_entropy(trace[t_idx + K_SHORT], site)
                h_long = local_entropy(trace[t_idx + K_LONG], site)

                if h_short > h_now:
                    memory[sig]["destab"][0] += 1
                else:
                    memory[sig]["destab"][1] += 1

                if abs(h_long - baseline) <= BASELINE_TOLERANCE:
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


# ---------- Phase 2: repair runs, targeted vs exact-rate-matched shuffled ----------
def run_seed_pair(memory, seed):
    # ===== PASS 1: REPAIR-TARGETED =====
    rng_t = random.Random(seed + 10000)
    S = [0] * N
    last_stable_window = {}   # pos -> list of bit VALUES (snapshot), refreshed each non-boundary step
    last_nonboundary_entropy = [None] * N

    t = 0
    alive = True
    intervention_history = []
    baselines_at_intervention = []   # per step: list of (site, baseline_entropy)
    states_trace = []

    while t < STEPS and alive:
        S = D(S, rng=rng_t)
        boundary_sites = set(E(S))

        # refresh stable-window snapshots BEFORE transform, for non-boundary sites
        for pos in range(N):
            if pos not in boundary_sites:
                last_stable_window[pos] = get_window_values(S, pos)
                last_nonboundary_entropy[pos] = local_entropy(S, pos)

        S_next = T(S)
        step_count = 0
        step_baselines = []

        for i in boundary_sites:
            sig = signature(S, i)
            conf = restab_confidence(memory, sig)
            if conf > RESTABILIZE_THRESHOLD and rng_t.random() < conf:
                baseline = last_nonboundary_entropy[i]
                if baseline is None:
                    continue
                if i in last_stable_window:
                    apply_window_values(S_next, i, last_stable_window[i])
                step_count += 1
                step_baselines.append((i, baseline))

        alive = P(S_next)
        S = S_next
        intervention_history.append(step_count)
        baselines_at_intervention.append(step_baselines)
        states_trace.append(S.copy())
        t += 1

    # measure |h_long - baseline| for each intervention made
    targeted_gaps = []
    for step_idx, records in enumerate(baselines_at_intervention):
        future_idx = step_idx + K_LONG
        if future_idx < len(states_trace):
            for site, baseline in records:
                h_long = local_entropy(states_trace[future_idx], site)
                targeted_gaps.append(abs(h_long - baseline))

    # ===== PASS 2: REPAIR-SHUFFLED (exact-rate matched) =====
    rng_s = random.Random(seed + 10000)
    S_s = [0] * N
    last_stable_window_s = {}
    last_nonboundary_entropy_s = [None] * N

    t = 0
    alive_s = True
    baselines_at_intervention_s = []
    states_trace_s = []

    while t < STEPS and alive_s:
        S_s = D(S_s, rng=rng_s)
        boundary_sites_s = list(E(S_s))
        boundary_set_s = set(boundary_sites_s)

        for pos in range(N):
            if pos not in boundary_set_s:
                last_stable_window_s[pos] = get_window_values(S_s, pos)
                last_nonboundary_entropy_s[pos] = local_entropy(S_s, pos)

        S_next_s = T(S_s)
        target_budget = intervention_history[t] if t < len(intervention_history) else 0

        # find which sites the (decorrelated) memory would trigger on
        triggered = []
        for i in boundary_sites_s:
            sig = signature(S_s, i)
            lookup_sig = tuple(reversed(sig))
            lookup_sig = lookup_sig[2:] + lookup_sig[:2]
            conf = restab_confidence(memory, lookup_sig)
            if conf > RESTABILIZE_THRESHOLD and rng_s.random() < conf:
                triggered.append(i)

        selected = triggered[:target_budget]
        if len(selected) < target_budget:
            remaining = [s for s in boundary_sites_s if s not in selected]
            extra = rng_s.sample(remaining, min(target_budget - len(selected), len(remaining)))
            selected.extend(extra)

        step_baselines_s = []
        for i in selected:
            baseline = last_nonboundary_entropy_s[i]
            if baseline is None:
                continue
            if i in last_stable_window_s:
                apply_window_values(S_next_s, i, last_stable_window_s[i])
            step_baselines_s.append((i, baseline))

        alive_s = P(S_next_s)
        S_s = S_next_s
        baselines_at_intervention_s.append(step_baselines_s)
        states_trace_s.append(S_s.copy())
        t += 1

    shuffled_gaps = []
    for step_idx, records in enumerate(baselines_at_intervention_s):
        future_idx = step_idx + K_LONG
        if future_idx < len(states_trace_s):
            for site, baseline in records:
                h_long = local_entropy(states_trace_s[future_idx], site)
                shuffled_gaps.append(abs(h_long - baseline))

    return {
        "targeted_mean_gap": statistics.mean(targeted_gaps) if targeted_gaps else None,
        "shuffled_mean_gap": statistics.mean(shuffled_gaps) if shuffled_gaps else None,
        "n_targeted": len(targeted_gaps),
        "n_shuffled": len(shuffled_gaps),
    }


if __name__ == "__main__":
    print("Phase 1: building dual-outcome memory from unperturbed baseline runs...")
    memory = build_memory(n_obs_seeds=30)
    print(f"  Learned {len(memory)} distinct signatures.\n")

    print("Phase 2: running REPAIR-TARGETED vs REPAIR-SHUFFLED (exact-rate matched), 30 seeds...")
    results = [run_seed_pair(memory, seed) for seed in range(N_SEEDS)]

    valid = [r for r in results if r["targeted_mean_gap"] is not None and r["shuffled_mean_gap"] is not None]
    print(f"  Valid seed pairs (both conditions had >=1 intervention with lookback available): {len(valid)}/{N_SEEDS}\n")

    if not valid:
        print("No valid comparisons -- interventions never fired. Check thresholds/memory.")
    else:
        t_gaps = [r["targeted_mean_gap"] for r in valid]
        s_gaps = [r["shuffled_mean_gap"] for r in valid]
        t_mean, t_std = statistics.mean(t_gaps), statistics.pstdev(t_gaps) if len(t_gaps) > 1 else 0.0
        s_mean, s_std = statistics.mean(s_gaps), statistics.pstdev(s_gaps) if len(s_gaps) > 1 else 0.0

        n_int_targeted = statistics.mean(r["n_targeted"] for r in valid)
        n_int_shuffled = statistics.mean(r["n_shuffled"] for r in valid)

        print("=" * 60)
        print("HOMEOSTASIS TEST: |entropy at t+K_LONG - pre-boundary baseline|")
        print("(LOWER is better -- means it actually returned toward baseline)")
        print("=" * 60)
        print(f"REPAIR-TARGETED: mean gap = {t_mean:.4f} (std {t_std:.4f}), n={len(t_gaps)} seeds, "
              f"avg {n_int_targeted:.1f} interventions measured/seed")
        print(f"REPAIR-SHUFFLED: mean gap = {s_mean:.4f} (std {s_std:.4f}), n={len(s_gaps)} seeds, "
              f"avg {n_int_shuffled:.1f} interventions measured/seed")

        diffs = [t - s for t, s in zip(t_gaps, s_gaps)]
        d_mean = statistics.mean(diffs)
        d_std = statistics.pstdev(diffs) if len(diffs) > 1 else 0.0
        if d_std > 0:
            paired_t = d_mean / (d_std / (len(diffs) ** 0.5))
        else:
            paired_t = float('inf') if d_mean != 0 else 0.0
        print(f"\nPaired difference (targeted - shuffled): {d_mean:+.4f} (std {d_std:.4f})")
        print(f"Paired t-stat: {paired_t:.3f}  (negative diff = targeted got CLOSER to baseline, i.e. better)")
        print("(|t| > ~2 roughly suggestive at n~30; not a rigorous p-value)")
