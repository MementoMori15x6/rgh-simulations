"""
STAGE 2: heredity/variation stress test.

Same protocol validated in the E/A work: reach equilibrium under normal
metabolic cost, then apply a metabolic shock, and measure survival.

CONTROL: fixed trait (0.5) for every cell, forever -- no inheritance,
  no mutation, no variation. Equivalent to the earlier "memoryless
  50/50" condition, but now framed as the true no-heredity baseline.
TREATMENT: heritable, mutating trait, founder population seeded with
  random variation -- real Darwinian selection, zero individual
  learning.

Tracks both survival (as in every prior stress test) AND mean
population trait over time, to see whether real selection on heritable
variation produces adaptive drift (e.g. toward higher cooperation
under stress, if that's advantageous, matching the direction the E/A
learning result found).
"""

import numpy as np
import statistics
from stage1_energy_baseline import N
from stage1_heredity_mechanism import step_with_heredity, MUTATION_STD
from stage1b_robustness_check import random_soup_seed

EQUILIBRIUM_STEPS = 1000
SHOCK_METABOLIC = 0.09
SHOCK_STEPS = 500


def run_stress_test(heritable, seed, mutation_std=MUTATION_STD, random_control=False):
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.15, rng)
    if heritable or random_control:
        trait = rng.random((N, N))  # random founder variation
    else:
        trait = np.full((N, N), 0.5)  # fixed baseline

    trait_trace = []

    for i in range(EQUILIBRIUM_STEPS):
        life, energy, trait = step_with_heredity(life, energy, trait, rng,
                                                    metabolic_cost=0.04, heritable=heritable,
                                                    mutation_std=mutation_std, random_control=random_control)
        if life.sum() == 0:
            return {'pre_shock_live': 0, 'survived_shock': False, 'post_shock_live': 0,
                    'pre_shock_trait': None, 'post_shock_trait': None}
        if i % 100 == 0:
            live_mask = life == 1
            if live_mask.any():
                trait_trace.append(trait[live_mask].mean())

    pre_shock_live = int(life.sum())
    pre_shock_trait = trait[life == 1].mean() if (life == 1).any() else None

    extinct = False
    for i in range(SHOCK_STEPS):
        life, energy, trait = step_with_heredity(life, energy, trait, rng,
                                                    metabolic_cost=SHOCK_METABOLIC, heritable=heritable,
                                                    mutation_std=mutation_std, random_control=random_control)
        if life.sum() == 0:
            extinct = True
            break

    post_shock_trait = trait[life == 1].mean() if (not extinct and (life == 1).any()) else None

    return {
        'pre_shock_live': pre_shock_live,
        'survived_shock': not extinct,
        'post_shock_live': int(life.sum()) if not extinct else 0,
        'pre_shock_trait': pre_shock_trait,
        'post_shock_trait': post_shock_trait,
    }


if __name__ == "__main__":
    N_SEEDS = 15

    print(f"FIXED-TRAIT CONTROL (no heredity, no variation), {N_SEEDS} seeds")
    print(f"{'seed':>5} {'pre_shock':>10} {'survived?':>10} {'post_shock':>11}")
    control_results = []
    for seed in range(N_SEEDS):
        r = run_stress_test(heritable=False, seed=seed)
        control_results.append(r)
        print(f"{seed:>5} {r['pre_shock_live']:>10} {str(r['survived_shock']):>10} {r['post_shock_live']:>11}")

    print(f"\nHERITABLE + MUTATING TRAIT (real selection), {N_SEEDS} seeds")
    print(f"{'seed':>5} {'pre_shock':>10} {'survived?':>10} {'post_shock':>11} {'pre_trait':>10} {'post_trait':>10}")
    treatment_results = []
    for seed in range(N_SEEDS):
        r = run_stress_test(heritable=True, seed=seed)
        treatment_results.append(r)
        pt = f"{r['pre_shock_trait']:.3f}" if r['pre_shock_trait'] is not None else "N/A"
        pot = f"{r['post_shock_trait']:.3f}" if r['post_shock_trait'] is not None else "N/A"
        print(f"{seed:>5} {r['pre_shock_live']:>10} {str(r['survived_shock']):>10} {r['post_shock_live']:>11} {pt:>10} {pot:>10}")

    control_survived = sum(r['survived_shock'] for r in control_results)
    treatment_survived = sum(r['survived_shock'] for r in treatment_results)

    print(f"\n{'='*60}")
    print(f"Fixed-trait control survival: {control_survived}/{N_SEEDS}")
    print(f"Heritable+mutating survival: {treatment_survived}/{N_SEEDS}")

    pre_traits = [r['pre_shock_trait'] for r in treatment_results if r['pre_shock_trait'] is not None]
    post_traits = [r['post_shock_trait'] for r in treatment_results if r['post_shock_trait'] is not None]
    if pre_traits:
        print(f"\nMean trait BEFORE shock (heritable condition): {statistics.mean(pre_traits):.4f}")
    if post_traits:
        print(f"Mean trait AFTER shock, among survivors (heritable condition): {statistics.mean(post_traits):.4f}")
