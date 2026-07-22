"""
STAGE 3: sharper heredity test.

The original test (mutation_std=0.05) found real heredity (parent-
average + mutation) statistically indistinguishable from a random-
reassignment control (fresh uniform trait at every birth, no
connection to parents) -- both showed ~15/15 survival and similar
trait drift under stress.

This test asks: is that because heredity genuinely doesn't matter here,
or because mutation_std=0.05 was large enough to wash out any
transgenerational signal? Sweep mutation size DOWN (heredity condition
only -- the random control has no mutation parameter, it always draws
fresh) and see whether the heredity-vs-random gap widens as mutation
shrinks, which is what should happen if heredity is doing real,
detectable work distinct from "selection on whatever variation exists."

Also: directly measure parent-offspring trait correlation under the
real-heredity condition, as a mechanistic check independent of survival
outcomes -- confirms whether inheritance is functioning as intended and
shows how quickly (if at all) that correlation decays under selection
and population turnover.
"""

import numpy as np
import statistics
from stage1_energy_baseline import N
from stage1_heredity_mechanism import step_with_heredity
from stage1b_robustness_check import random_soup_seed

EQUILIBRIUM_STEPS = 1000
SHOCK_METABOLIC = 0.09
SHOCK_STEPS = 500
N_SEEDS = 15


def run_stress_test(seed, mutation_std, random_control):
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.15, rng)
    trait = rng.random((N, N))  # random founder variation in both conditions

    for i in range(EQUILIBRIUM_STEPS):
        life, energy, trait = step_with_heredity(life, energy, trait, rng,
                                                    metabolic_cost=0.04, heritable=True,
                                                    mutation_std=mutation_std, random_control=random_control)
        if life.sum() == 0:
            return {'survived_shock': False}

    extinct = False
    for i in range(SHOCK_STEPS):
        life, energy, trait = step_with_heredity(life, energy, trait, rng,
                                                    metabolic_cost=SHOCK_METABOLIC, heritable=True,
                                                    mutation_std=mutation_std, random_control=random_control)
        if life.sum() == 0:
            extinct = True
            break

    return {'survived_shock': not extinct}


def measure_parent_offspring_correlation(seed, mutation_std, n_steps=500):
    """
    Directly measures correlation between a newborn's trait and the
    average trait of its 3 parents, sampled across many birth events
    over a run. High correlation confirms inheritance is functioning;
    tracks how that correlation holds up under selection + turnover.
    """
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.15, rng)
    trait = rng.random((N, N))

    parent_vals = []
    offspring_vals = []

    for step in range(n_steps):
        # capture birth events BEFORE the step overwrites trait,
        # by replicating the relevant piece of step_with_heredity's logic
        from stage1_heredity_mechanism import gol_neighbor_count
        neighbor_count = gol_neighbor_count(life)
        born = (life == 0) & (neighbor_count == 3)

        if born.any():
            trait_sum_alive_neighbors = np.zeros_like(trait)
            for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                shifted_life = np.roll(np.roll(life, dr, axis=0), dc, axis=1)
                shifted_trait = np.roll(np.roll(trait, dr, axis=0), dc, axis=1)
                trait_sum_alive_neighbors += shifted_life * shifted_trait
            avg_parent_trait = trait_sum_alive_neighbors / 3.0

            rows, cols = np.where(born)
            for r, c in zip(rows.tolist(), cols.tolist()):
                parent_vals.append(avg_parent_trait[r, c])

        life, energy, trait_next = step_with_heredity(life, energy, trait, rng,
                                                         metabolic_cost=0.04, heritable=True,
                                                         mutation_std=mutation_std, random_control=False)

        if born.any():
            rows, cols = np.where(born & (life == 1))
            for r, c in zip(rows.tolist(), cols.tolist()):
                offspring_vals.append(trait_next[r, c])

        trait = trait_next
        if life.sum() == 0:
            break

    n = min(len(parent_vals), len(offspring_vals))
    if n < 10:
        return None
    parent_vals = np.array(parent_vals[:n])
    offspring_vals = np.array(offspring_vals[:n])
    if parent_vals.std() == 0 or offspring_vals.std() == 0:
        return None
    corr = np.corrcoef(parent_vals, offspring_vals)[0, 1]
    return corr, n


if __name__ == "__main__":
    print("PART 1: parent-offspring trait correlation (mechanistic sanity check)")
    for mutation_std in [0.005, 0.02, 0.05, 0.15]:
        corrs = []
        for seed in range(5):
            result = measure_parent_offspring_correlation(seed, mutation_std, n_steps=500)
            if result is not None:
                corrs.append(result[0])
        if corrs:
            print(f"  mutation_std={mutation_std}: mean parent-offspring correlation = {statistics.mean(corrs):.4f} "
                  f"(n_seeds={len(corrs)})")
        else:
            print(f"  mutation_std={mutation_std}: no valid data")

    print("\nPART 2: mutation-size sweep, real heredity vs random-control survival")
    print(f"{'mutation_std':>14} {'heredity_survival':>18} {'random_ctrl_survival':>20}")

    # random control doesn't depend on mutation_std, compute once
    random_control_survivals = sum(
        run_stress_test(seed, mutation_std=0.05, random_control=True)['survived_shock']
        for seed in range(N_SEEDS)
    )

    for mutation_std in [0.005, 0.01, 0.02, 0.05, 0.10, 0.20]:
        heredity_survivals = sum(
            run_stress_test(seed, mutation_std=mutation_std, random_control=False)['survived_shock']
            for seed in range(N_SEEDS)
        )
        print(f"{mutation_std:>14} {heredity_survivals:>15}/{N_SEEDS} {random_control_survivals:>17}/{N_SEEDS}")
