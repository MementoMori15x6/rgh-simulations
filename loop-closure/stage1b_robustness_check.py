"""
STAGE 1B: robustness check across multiple seed layouts.

The single hand-placed seed (3 gliders + 2 blocks at fixed positions)
gave a clean, sensible result (1 block + 1 glider survived, energy
reached stable equilibrium). But one seed proves nothing about whether
this is a robust property of the dynamics vs. a lucky/unlucky placement.

This runs the same baseline energy-CA across many DIFFERENT random
initial layouts (random soup, same style as our GoL work) and checks:
  1. Does energy reliably reach a stable equilibrium (not blow up, not
     collapse to zero) across different starting conditions?
  2. Does SOME structure reliably survive, or does survival rate vary
     wildly / depend on exact placement?
  3. Is the equilibrium energy level consistent across seeds, or wildly
     different (which would suggest something fragile/seed-dependent)?
"""

import numpy as np
from stage1_energy_baseline import step, N, METABOLIC_COST, BACKGROUND_INFLOW, BACKGROUND_DECAY

def random_soup_seed(size, density, rng, initial_energy=1.0):
    life = (rng.random((size, size)) < density).astype(int)
    energy = np.full((size, size), initial_energy, dtype=float)
    return life, energy

if __name__ == "__main__":
    N_SEEDS = 20
    STEPS = 2000
    DENSITY = 0.15

    print(f"Testing baseline energy-CA robustness across {N_SEEDS} random seeds")
    print(f"(density={DENSITY}, {STEPS} steps each)\n")

    results = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        life, energy = random_soup_seed(N, DENSITY, rng)

        extinct_at = None
        for step_num in range(STEPS):
            life, energy = step(life, energy)
            if life.sum() == 0 and extinct_at is None:
                extinct_at = step_num
                break

        final_live = int(life.sum())
        final_energy_mean = float(energy.mean())
        final_energy_std = float(energy.std())

        results.append({
            "seed": seed,
            "extinct_at": extinct_at,
            "final_live": final_live,
            "final_energy_mean": final_energy_mean,
            "final_energy_std": final_energy_std,
        })

        status = f"EXTINCT@{extinct_at}" if extinct_at is not None else f"SURVIVED({final_live} cells)"
        print(f"  seed {seed:>2}: {status:>20}  energy_mean={final_energy_mean:.4f} "
              f"energy_std={final_energy_std:.4f}")

    n_survived = sum(1 for r in results if r["extinct_at"] is None)
    n_extinct = N_SEEDS - n_survived
    print(f"\n{'='*50}")
    print(f"Survived: {n_survived}/{N_SEEDS}, Extinct: {n_extinct}/{N_SEEDS}")

    survived_results = [r for r in results if r["extinct_at"] is None]
    if survived_results:
        energies = [r["final_energy_mean"] for r in survived_results]
        live_counts = [r["final_live"] for r in survived_results]
        print(f"Among survivors: energy_mean range [{min(energies):.4f}, {max(energies):.4f}], "
              f"live_cell range [{min(live_counts)}, {max(live_counts)}]")

    if n_extinct > 0:
        extinct_times = [r["extinct_at"] for r in results if r["extinct_at"] is not None]
        print(f"Among extinctions: extinction step range [{min(extinct_times)}, {max(extinct_times)}]")
