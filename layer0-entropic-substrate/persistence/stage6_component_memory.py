"""
STAGE 6: component-size-based (higher-level) salvageability memory.

Same persistence criterion as the local-signature memory (does a
matching pattern reappear nearby after K_LONG steps), but tagged by
CONNECTED-COMPONENT SIZE at time of tagging, not local 3x3 pattern.

Rationale: a cell deep inside a glider and a cell in a random noise
blob can have IDENTICAL local 3x3 signatures while belonging to very
different larger structures. Component size is a genuinely different,
higher-level feature -- this isolates whether the local-signature null
result was about local information being insufficient (this test could
still show a real effect) vs. targeting quality being uninformative in
general (this test would also come back null).
"""

import numpy as np
from scipy import ndimage
from collections import defaultdict
import statistics
from vectorized_signature import encode_signature_grid, pattern_reappears_nearby_vectorized
from stage1_salvageability_memory import (
    gol_neighbor_count, N, WINDOW, K_LONG, MAX_SPEED, SEARCH_RADIUS,
    BASELINE_STEPS, SOUP_DENSITY, BACKGROUND_INFLOW, BACKGROUND_DECAY,
    BIRTH_ENERGY_FRACTION, METABOLIC_COST, energy_step
)

MAX_COMPONENT_SIZE_BUCKET = 30  # component sizes above this are bucketed together
LABEL_STRUCTURE = np.array([[1,1,1],[1,1,1],[1,1,1]])  # 8-connectivity, consistent
                                                          # with GoL's own Moore neighborhood


def component_size_grid(life):
    """Returns an array, same shape as life, where each live cell's value
    is the size (cell count) of its connected component. Dead cells: 0."""
    labeled, n_components = ndimage.label(life, structure=LABEL_STRUCTURE)
    if n_components == 0:
        return np.zeros_like(life)
    sizes = ndimage.sum(life, labeled, index=np.arange(1, n_components + 1))
    size_map = np.zeros(n_components + 1)
    size_map[1:] = sizes
    return size_map[labeled].astype(int)


def bucket_size(size):
    return min(size, MAX_COMPONENT_SIZE_BUCKET)


def build_component_memory(n_seeds=20, baseline_steps=BASELINE_STEPS, k_long=K_LONG):
    memory = defaultdict(lambda: [0, 0])
    search_radius = k_long * MAX_SPEED
    total_tagged = 0

    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
        energy = np.full((N, N), 1.0)

        trace = []
        sig_grids = []
        comp_size_grids = []
        t = 0
        while t < baseline_steps:
            trace.append(life.copy())
            sig_grids.append(encode_signature_grid(life, WINDOW))
            comp_size_grids.append(component_size_grid(life))
            life, energy = energy_step(life, energy)
            if life.sum() == 0 or life.sum() == life.size:
                break
            t += 1

        n_steps = len(trace)
        for t_idx in range(n_steps - k_long):
            Lt = trace[t_idx]
            sig_grid_t = sig_grids[t_idx]
            comp_grid_t = comp_size_grids[t_idx]
            rs, cs = np.where(Lt == 1)
            total_tagged += len(rs)

            future_sig_grid = sig_grids[t_idx + k_long]
            for r, c in zip(rs.tolist(), cs.tolist()):
                target_sig_int = int(sig_grid_t[r, c])
                comp_size = bucket_size(int(comp_grid_t[r, c]))
                if pattern_reappears_nearby_vectorized(future_sig_grid, r, c, target_sig_int, search_radius):
                    memory[comp_size][0] += 1
                else:
                    memory[comp_size][1] += 1

    return memory, total_tagged


if __name__ == "__main__":
    print("Diagnostic: 1-seed timing check")
    import time
    t0 = time.time()
    memory, total = build_component_memory(n_seeds=1)
    t1 = time.time()
    print(f"  1 seed: {t1-t0:.1f}s, {total} cells tagged, {len(memory)} distinct component-size buckets")
    print(f"  Estimated 20 seeds: {(t1-t0)*20:.1f}s\n")

    for size in sorted(memory.keys()):
        p, v = memory[size]
        tot = p + v
        conf = p / tot if tot > 0 else 0
        print(f"  component_size={size:>3}: n={tot:>6} confidence={conf:.3f}")
