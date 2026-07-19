"""
STAGE 3: full stress test. Runs all four repair conditions (none, random,
smart, shuffled) across many seeds under repeated structural + energy-drain
damage, measuring:
  - survival rate (extinction vs. not, over a fixed step budget)
  - complexity preservation (mean live-cell count among survivors, and
    total repair "spend" -- energy diverted to repair actions -- as a
    cost check)

RANDOM_REPAIR is rate-matched to SMART_REPAIR's per-step intervention
count, same discipline as every rate-matched control in this project.
"""

import numpy as np
import statistics
from stage1_salvageability_memory import (
    gol_neighbor_count, N, BACKGROUND_INFLOW, BACKGROUND_DECAY,
    BIRTH_ENERGY_FRACTION, METABOLIC_COST, build_salvageability_memory
)
from stage2_damage_repair import (
    apply_damage, repair_cells, repair_cells_shuffled_matched, build_shuffle_map, DAMAGE_INTERVAL
)

MAX_STEPS = 3000
SOUP_DENSITY = 0.25


def energy_step_with_damage_and_repair(life, energy, rng, step_num, mode, memory, shuffle_map):
    """One full timestep: normal GoL+energy update, then (on damage
    intervals) damage + repair, in the precise order that makes
    'damaged_mask' well-defined (see stage2 docstring)."""
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    neighbor_avg = (
        np.roll(energy, 1, 0) + np.roll(energy, -1, 0) +
        np.roll(energy, 1, 1) + np.roll(energy, -1, 1)
    ) / 4.0
    energy = energy + 0.1 * (neighbor_avg - energy)
    energy = energy + BACKGROUND_INFLOW
    energy = energy * (1 - BACKGROUND_DECAY)
    energy = np.where(life == 1, energy - METABOLIC_COST, energy)

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
    energy_next = np.clip(energy, 0, None)

    n_repaired = 0
    if step_num % DAMAGE_INTERVAL == 0:
        pre_damage_life = life_next.copy()
        life_next, energy_next, damaged_mask = apply_damage(life_next, energy_next, rng)

        if mode in ('random', 'shuffled_matched'):
            # first compute what SMART would do this step, to get the
            # matched repair-rate target -- applies to BOTH random and
            # shuffled controls, so all three non-smart conditions are
            # compared at the SAME intervention rate as smart, isolating
            # targeting quality as the only remaining difference.
            _, _, n_smart = repair_cells(life_next, energy_next, pre_damage_life,
                                           damaged_mask, 'smart', memory, rng)
            n_damaged = damaged_mask.sum()
            rate_target = (n_smart / n_damaged) if n_damaged > 0 else 0.0

            if mode == 'random':
                life_next, energy_next, n_repaired = repair_cells(
                    life_next, energy_next, pre_damage_life, damaged_mask,
                    'random', memory, rng, repair_rate_target=rate_target)
            else:  # shuffled_matched: use shuffled targeting, but only
                   # up to the SAME COUNT smart would have repaired --
                   # picks the highest-shuffled-confidence damaged cells
                   # first, capped at n_smart, so rate is truly matched.
                life_next, energy_next, n_repaired = repair_cells_shuffled_matched(
                    life_next, energy_next, pre_damage_life, damaged_mask,
                    memory, shuffle_map, n_cap=n_smart)
        elif mode == 'smart':
            life_next, energy_next, n_repaired = repair_cells(
                life_next, energy_next, pre_damage_life, damaged_mask,
                'smart', memory, rng, shuffle_map=shuffle_map)

    return life_next, energy_next, n_repaired


def run_trial(mode, seed, memory, shuffle_map, max_steps=MAX_STEPS):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.full((N, N), 1.0)

    total_repaired = 0
    for step in range(max_steps):
        life, energy, n_repaired = energy_step_with_damage_and_repair(
            life, energy, rng, step, mode, memory, shuffle_map)
        total_repaired += n_repaired
        if life.sum() == 0:
            return {'survived': False, 'final_live': 0, 'steps_survived': step, 'total_repaired': total_repaired}
        if life.sum() == life.size:
            return {'survived': False, 'final_live': int(life.sum()), 'steps_survived': step, 'total_repaired': total_repaired}

    return {'survived': True, 'final_live': int(life.sum()), 'steps_survived': max_steps, 'total_repaired': total_repaired}


if __name__ == "__main__":
    print("Building salvageability memory (20 seeds)...")
    memory, total = build_salvageability_memory(n_seeds=20)
    print(f"  {len(memory)} signatures\n")

    print("Validating shuffle map...")
    shuffle_map, corr = build_shuffle_map(memory, seed=0)
    print(f"  correlation={corr:.4f} (near zero = valid decorrelated control)\n")

    N_TRIALS = 15
    modes = ['none', 'random', 'smart', 'shuffled_matched']
    results = {m: [] for m in modes}

    print(f"Running {N_TRIALS} trials per condition...")
    for seed in range(N_TRIALS):
        for mode in modes:
            r = run_trial(mode, seed, memory, shuffle_map)
            results[mode].append(r)
        print(f"  seed {seed} done")

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    for mode in modes:
        survived = [r['survived'] for r in results[mode]]
        final_live = [r['final_live'] for r in results[mode] if r['survived']]
        total_repaired = [r['total_repaired'] for r in results[mode]]
        n_survived = sum(survived)
        mean_live = statistics.mean(final_live) if final_live else 0
        mean_repaired = statistics.mean(total_repaired)
        print(f"{mode:>10}: survived {n_survived}/{N_TRIALS}, "
              f"mean final live (among survivors)={mean_live:.1f}, "
              f"mean total repairs attempted={mean_repaired:.1f}")
