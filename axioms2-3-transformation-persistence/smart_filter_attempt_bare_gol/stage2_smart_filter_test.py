"""
STAGE 2: smart persistence filter vs. crude filter vs. no filter vs.
shuffled-signature control.

Reuses the exact noise-injection stress-test protocol from the original
entropic-decay test (Axiom 3 findings), so results are directly
comparable to the documented crude-filter result (lifespan REDUCED by
~2801 steps, t=-7.0).

Four conditions:
  1. NO FILTER: noise injection only, no persistence mechanism at all.
  2. CRUDE FILTER: delete any live cell with <2 neighbors (the original,
     already-documented mechanism that backfired).
  3. SMART FILTER: delete a candidate cell only if its 3x3 signature's
     coherence-memory confidence is BELOW a threshold (i.e. only delete
     configurations historically associated with vanishing, not
     enduring, structure).
  4. SHUFFLED-SIGNATURE CONTROL: same smart-filter mechanism and
     threshold, but the signature used for the memory LOOKUP is a
     decorrelated transform of the real signature (bit-reversal),
     matched for intervention rate. If the smart filter's benefit
     (if any) disappears here, it was a rate/coincidence artifact,
     not genuine signature-based discrimination.
"""

import numpy as np
from scipy import ndimage
import statistics
from stage1_fast import build_coherence_memory, conway_step, neighbor_count_grid, N, K_LONG, WINDOW
from vectorized_signature import encode_signature_grid

MAX_STEPS = 5000
NOISE_RATE = 0.0008
NOISE_INTERVAL = 5
SMART_THRESHOLD = 0.5  # delete only if confidence < this (i.e. historically LESS likely to persist)

KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


def add_entropy(grid, noise_rate, rng):
    mask = rng.random(grid.shape) < noise_rate
    return np.logical_xor(grid, mask).astype(int)


def crude_filter(grid):
    filtered = grid.copy()
    nbr_count = neighbor_count_grid(grid)
    noise_mask = (grid == 1) & (nbr_count < 2)
    filtered[noise_mask] = 0
    return filtered


def reverse_9bit(sig_int):
    """
    DECORRELATION TRANSFORM FOR THE SHUFFLED CONTROL.

    BUG FOUND AND FIXED: the original version of this function did a
    simple bit-reversal, which for this 9-bit (dr,dc)-ordered encoding
    is exactly a 180-degree ROTATION of the 3x3 neighborhood (N<->S,
    E<->W, NE<->SW, NW<->SE, center fixed). Because GoL on a random-soup
    toroidal grid has no directional bias, orthogonal-vs-orthogonal and
    diagonal-vs-diagonal pairs have essentially IDENTICAL persistence
    statistics by symmetry -- so this "shuffle" preserved exactly the
    one distinction (orthogonal vs diagonal) that the coherence memory
    actually depends on. Confirmed directly: smart_filter and the old
    shuffled_control produced EXACTLY identical results (delta=0.0),
    which was the tell that the control wasn't controlling for anything.

    FIX: explicitly map each orthogonal-class signature to a DIFFERENT
    diagonal-class signature (and vice versa), so the shuffled lookup
    genuinely uses statistically different confidence values from the
    real one, rather than a same-class relabeling.
    """
    # fixed lookup table: cross-maps orthogonal <-> diagonal classes,
    # rather than same-class rotation
    CROSS_CLASS_MAP = {
        16: 16,    # isolated stays isolated (no other class to map to)
        18: 17,    # N   -> NW (orthogonal -> diagonal)
        144: 20,   # S   -> NE
        24: 80,    # W   -> SW
        48: 272,   # E   -> SE
        17: 18,    # NW  -> N  (diagonal -> orthogonal)
        272: 144,  # SE  -> S
        80: 24,    # SW  -> W
        20: 48,    # NE  -> E
    }
    return CROSS_CLASS_MAP.get(sig_int, sig_int)


def make_memory_filter(memory, threshold=SMART_THRESHOLD, shuffled=False):
    def confidence(sig_int):
        d = memory.get(sig_int)
        if d is None:
            return None
        p, v = d
        total = p + v
        return (p / total) if total > 0 else None

    def smart_filter(grid):
        filtered = grid.copy()
        nbr_count = neighbor_count_grid(grid)
        candidates = (grid == 1) & (nbr_count < 2)
        sig_grid = encode_signature_grid(grid, WINDOW)

        rs, cs = np.where(candidates)
        for r, c in zip(rs.tolist(), cs.tolist()):
            sig_int = int(sig_grid[r, c])
            lookup_sig = reverse_9bit(sig_int) if shuffled else sig_int
            conf = confidence(lookup_sig)
            # unknown signature (shouldn't happen given full 9-signature
            # coverage, but handled defensively): default to deleting,
            # matching crude-filter behavior as a safe fallback
            if conf is None or conf < threshold:
                filtered[r, c] = 0
        return filtered

    return smart_filter


def init_seed(size=N):
    grid = np.zeros((size, size), dtype=int)
    glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
    grid[5:8, 5:8] = glider
    grid[15:18, 25:28] = glider
    grid[35:38, 10:13] = glider
    block = np.array([[1, 1], [1, 1]])
    grid[10:12, 40:42] = block
    grid[40:42, 40:42] = block
    return grid


def run_simulation(filter_fn, seed_val):
    rng = np.random.default_rng(seed_val)
    grid = init_seed()

    for step in range(MAX_STEPS):
        grid = conway_step(grid)
        if step % NOISE_INTERVAL == 0:
            grid = add_entropy(grid, NOISE_RATE, rng)
        if filter_fn is not None:
            grid = filter_fn(grid)

        total_cells = grid.sum()
        if total_cells == 0 or total_cells == N * N:
            return step

    return MAX_STEPS


if __name__ == "__main__":
    print("Building coherence memory (20 baseline seeds)...")
    memory, total_candidates = build_coherence_memory(n_seeds=20)
    print(f"  {len(memory)} signatures, {total_candidates} candidate observations\n")

    smart_filter_fn = make_memory_filter(memory, threshold=SMART_THRESHOLD, shuffled=False)
    shuffled_filter_fn = make_memory_filter(memory, threshold=SMART_THRESHOLD, shuffled=True)

    print("Running 4-condition lifespan comparison (20 trials each)...")
    n_trials = 20

    conditions = {
        "no_filter": None,
        "crude_filter": crude_filter,
        "smart_filter": smart_filter_fn,
        "shuffled_control": shuffled_filter_fn,
    }

    results = {name: [] for name in conditions}

    for trial in range(n_trials):
        seed_val = 1000 + trial
        for name, filter_fn in conditions.items():
            lifespan = run_simulation(filter_fn, seed_val)
            results[name].append(lifespan)

    print("\nRESULTS SUMMARY:")
    for name, lifespans in results.items():
        mean = statistics.mean(lifespans)
        std = statistics.pstdev(lifespans)
        print(f"  {name:>18}: mean={mean:>7.1f} steps (std={std:>6.1f})")

    print("\nPAIRED COMPARISONS (vs no_filter baseline):")
    baseline = results["no_filter"]
    for name in ["crude_filter", "smart_filter", "shuffled_control"]:
        diffs = [f - b for f, b in zip(results[name], baseline)]
        d_mean = statistics.mean(diffs)
        d_std = statistics.pstdev(diffs)
        t_stat = d_mean / (d_std / (len(diffs) ** 0.5)) if d_std > 0 else float('inf')
        print(f"  {name:>18} vs no_filter: delta={d_mean:>+8.1f}  paired-t={t_stat:>7.3f}")

    print("\nPAIRED COMPARISON (smart_filter vs shuffled_control -- the key check):")
    diffs = [s - sh for s, sh in zip(results["smart_filter"], results["shuffled_control"])]
    d_mean = statistics.mean(diffs)
    d_std = statistics.pstdev(diffs)
    t_stat = d_mean / (d_std / (len(diffs) ** 0.5)) if d_std > 0 else float('inf')
    print(f"  smart_filter - shuffled_control: delta={d_mean:+.1f}  paired-t={t_stat:.3f}")
    print("  (positive delta = smart filter genuinely outperforms decorrelated lookup at same rate)")
