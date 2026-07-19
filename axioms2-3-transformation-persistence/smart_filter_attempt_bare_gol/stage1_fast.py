"""
STAGE 1 (FAST): coherence memory builder using vectorized signature
encoding/lookup, replacing the slow per-cell nested-loop version.
"""

import numpy as np
from scipy import ndimage
from collections import defaultdict
import statistics
from vectorized_signature import encode_signature_grid, pattern_reappears_nearby_vectorized

N = 50
WINDOW = 1
K_LONG = 8
MAX_SPEED = 1
SEARCH_RADIUS = K_LONG * MAX_SPEED
BASELINE_STEPS = 1500
SOUP_DENSITY = 0.25

KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


def conway_step(grid):
    neighbors = ndimage.convolve(grid, KERNEL, mode='wrap')
    next_grid = np.zeros_like(grid)
    next_grid[(grid == 1) & ((neighbors == 2) | (neighbors == 3))] = 1
    next_grid[(grid == 0) & (neighbors == 3)] = 1
    return next_grid


def neighbor_count_grid(grid):
    return ndimage.convolve(grid, KERNEL, mode='wrap')


def build_coherence_memory(n_seeds=20, baseline_steps=BASELINE_STEPS, density=SOUP_DENSITY, k_long=K_LONG):
    memory = defaultdict(lambda: [0, 0])
    search_radius = k_long * MAX_SPEED
    total_candidates = 0

    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        grid = (rng.random((N, N)) < density).astype(int)
        trace = []
        sig_grids = []
        t = 0
        while t < baseline_steps:
            trace.append(grid.copy())
            sig_grids.append(encode_signature_grid(grid, WINDOW))
            grid = conway_step(grid)
            if grid.sum() == 0 or grid.sum() == grid.size:
                break
            t += 1

        n_steps = len(trace)
        for t_idx in range(n_steps - k_long):
            Gt = trace[t_idx]
            sig_grid_t = sig_grids[t_idx]
            nbr_count = neighbor_count_grid(Gt)
            candidates = (Gt == 1) & (nbr_count < 2)
            rs, cs = np.where(candidates)
            total_candidates += len(rs)

            future_sig_grid = sig_grids[t_idx + k_long]
            for r, c in zip(rs.tolist(), cs.tolist()):
                target_sig_int = int(sig_grid_t[r, c])
                if pattern_reappears_nearby_vectorized(future_sig_grid, r, c, target_sig_int, search_radius):
                    memory[target_sig_int][0] += 1
                else:
                    memory[target_sig_int][1] += 1

    return memory, total_candidates


if __name__ == "__main__":
    import time

    print("Diagnostic: candidate availability check (1 seed, before full run)")
    t0 = time.time()
    memory, total_candidates = build_coherence_memory(n_seeds=1)
    t1 = time.time()
    print(f"  1 seed: {t1-t0:.1f}s, {total_candidates} candidates observed, {len(memory)} distinct signatures\n")

    print(f"Estimated time for 20 seeds: {(t1-t0)*20:.1f}s")
