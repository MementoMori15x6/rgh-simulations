"""
STAGE 1: salvageability memory for damage-repair testing.

Built from UNDAMAGED baseline runs of the validated energy-conservation
GoL substrate (metabolic_cost=0.04, confirmed to actually constrain
survival in prior work). For every alive cell at every recorded step,
tag its full 3x3 signature (not restricted to low-neighbor-count this
time, since damage can strike any live cell) with whether a matching
local pattern reappears nearby after K_LONG steps -- the same
pattern-persistence criterion validated in the 2D E/A and P-filter work.

This is a genuinely different, larger signature space than the P-filter
attempt (up to 2^9=512 possible signatures here, vs. exactly 9 for the
"low-neighbor-count candidates only" restriction used there) -- diagnostic
checks below confirm whether this space is well-populated before trusting it.
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
METABOLIC_COST = 0.04
BACKGROUND_INFLOW = 0.015
BACKGROUND_DECAY = 0.02
BIRTH_ENERGY_FRACTION = 0.3

KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


def gol_neighbor_count(life):
    return ndimage.convolve(life, KERNEL, mode='wrap')


def energy_step(life, energy, metabolic_cost=METABOLIC_COST):
    """Standard validated energy-CA step: GoL rule + metabolic cost +
    background inflow/decay + birth cost. No damage, no repair -- this
    is the clean baseline used to BUILD the memory."""
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    neighbor_avg = (
        np.roll(energy, 1, 0) + np.roll(energy, -1, 0) +
        np.roll(energy, 1, 1) + np.roll(energy, -1, 1)
    ) / 4.0
    energy = energy + 0.1 * (neighbor_avg - energy)  # simple diffusion
    energy = energy + BACKGROUND_INFLOW
    energy = energy * (1 - BACKGROUND_DECAY)
    energy = np.where(life == 1, energy - metabolic_cost, energy)

    birth_cost = BIRTH_ENERGY_FRACTION * neighbor_avg
    energy = np.where(born, energy + birth_cost, energy)
    cost_share = np.zeros_like(energy)
    if born.any():
        rows, cols = np.where(born)
        for r, c in zip(rows.tolist(), cols.tolist()):
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                rr, cc = (r + dr) % n_rows, (c + dc) % n_cols
                cost_share[rr, cc] += birth_cost[r, c] / 4.0
    energy = energy - cost_share

    life_next = np.zeros_like(life)
    life_next[survives & (energy > 0)] = 1
    life_next[born & (energy > 0)] = 1
    energy = np.clip(energy, 0, None)

    return life_next, energy


def build_salvageability_memory(n_seeds=20, baseline_steps=BASELINE_STEPS, k_long=K_LONG):
    memory = defaultdict(lambda: [0, 0])
    search_radius = k_long * MAX_SPEED
    total_tagged = 0

    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
        energy = np.full((N, N), 1.0)

        trace = []
        sig_grids = []
        t = 0
        while t < baseline_steps:
            trace.append(life.copy())
            sig_grids.append(encode_signature_grid(life, WINDOW))
            life, energy = energy_step(life, energy)
            if life.sum() == 0 or life.sum() == life.size:
                break
            t += 1

        n_steps = len(trace)
        for t_idx in range(n_steps - k_long):
            Lt = trace[t_idx]
            sig_grid_t = sig_grids[t_idx]
            rs, cs = np.where(Lt == 1)
            total_tagged += len(rs)

            future_sig_grid = sig_grids[t_idx + k_long]
            for r, c in zip(rs.tolist(), cs.tolist()):
                target_sig_int = int(sig_grid_t[r, c])
                if pattern_reappears_nearby_vectorized(future_sig_grid, r, c, target_sig_int, search_radius):
                    memory[target_sig_int][0] += 1
                else:
                    memory[target_sig_int][1] += 1

    return memory, total_tagged


if __name__ == "__main__":
    print("Diagnostic: 1-seed timing and coverage check before full run")
    import time
    t0 = time.time()
    memory, total_tagged = build_salvageability_memory(n_seeds=1)
    t1 = time.time()
    print(f"  1 seed: {t1-t0:.1f}s, {total_tagged} cells tagged, {len(memory)} distinct signatures")
    print(f"  Estimated time for 20 seeds: {(t1-t0)*20:.1f}s")
