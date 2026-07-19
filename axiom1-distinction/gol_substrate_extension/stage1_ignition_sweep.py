"""
STAGE 1: GoL ignition threshold sweep.

Direct analog of the Gray-Scott noise-amplitude test from Axiom 1: start
from the substrate's own trivial/undifferentiated state (all cells dead
-- the discrete equivalent of Gray-Scott's uniform U=1,V=0 baseline),
perturb with sparse random noise (a small density of live cells), and
find the real threshold between "everything dies back to nothing" and
"structure persists."

This is the first, minimal check: does GoL even have a meaningful
ignition threshold to characterize, the way Gray-Scott did? If density
sweeps show no real transition (e.g. everything either always dies or
always persists regardless of density), that would be an early signal
this line isn't going to produce a clean result, and we should know
that before investing in the harder causal-insulation test.
"""

import numpy as np
from scipy import ndimage

N = 50
MAX_STEPS = 2000
KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


def gol_step(grid):
    neighbors = ndimage.convolve(grid, KERNEL, mode='wrap')
    next_grid = np.zeros_like(grid)
    next_grid[(grid == 1) & ((neighbors == 2) | (neighbors == 3))] = 1
    next_grid[(grid == 0) & (neighbors == 3)] = 1
    return next_grid


def run_from_density(density, seed, max_steps=MAX_STEPS):
    """Start from all-dead grid + sparse random perturbation at given
    density. Returns (final_live_count, survived_to_max_steps)."""
    rng = np.random.default_rng(seed)
    grid = (rng.random((N, N)) < density).astype(int)

    for step in range(max_steps):
        grid = gol_step(grid)
        if grid.sum() == 0:
            return 0, False
    return int(grid.sum()), True


if __name__ == "__main__":
    print("GoL ignition threshold sweep: sparse random perturbation from all-dead state\n")
    print(f"{'density':>8} {'seed0':>18} {'seed1':>18} {'seed2':>18}")
    print("-" * 66)

    densities = [0.01, 0.02, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30]

    for density in densities:
        results = []
        for seed in range(3):
            final_count, survived = run_from_density(density, seed)
            results.append(f"{'survived' if survived else 'died'}({final_count})")
        print(f"{density:>8.2f} {results[0]:>18} {results[1]:>18} {results[2]:>18}")
