"""
STAGE 4: gradual environmental ramp (the flip side of the bet-hedging finding).

The original test found that under a SUDDEN, unpredictable shock, real
heredity (parent-average + mutation) was statistically indistinguishable
from random reassignment at moderate mutation, and at LOW mutation
(more faithful heredity) actually UNDERPERFORMED random reassignment --
attributed to bet-hedging: standing variation matters more than lineage
transmission when a population cannot anticipate what's coming.

Bet-hedging theory predicts the flip side: under GRADUAL, PREDICTABLE
change, heredity should do BETTER than random reassignment, since
inherited, accumulated adaptation has time to track a slow, foreseeable
shift -- while random reassignment discards any such tracking every
single generation, drawing a fresh, unrelated trait value regardless of
what the environment currently favors.

Method: identical mechanism and conditions to the original stress test,
but METABOLIC_COST rises gradually and continuously (linear ramp) rather
than jumping abruptly, over a long period -- a genuinely predictable,
trackable change a population COULD adapt to over many generations if
heredity is doing real work.
"""

import numpy as np
import statistics
from stage1_energy_baseline import N
from stage1_heredity_mechanism import step_with_heredity, MUTATION_STD
from stage1b_robustness_check import random_soup_seed

EQUILIBRIUM_STEPS = 1000
RAMP_STEPS = 4000            # long, gradual ramp -- genuinely slow relative to
                              # population turnover, giving heredity real time to track
RAMP_START_COST = 0.04
RAMP_END_COST = 0.09          # same endpoint as the original sudden-shock test,
                              # for direct comparability
N_SEEDS = 15


def run_ramp_test(heritable, seed, mutation_std=MUTATION_STD, random_control=False):
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.15, rng)
    trait = rng.random((N, N)) if (heritable or random_control) else np.full((N, N), 0.5)

    for i in range(EQUILIBRIUM_STEPS):
        life, energy, trait = step_with_heredity(life, energy, trait, rng,
                                                    metabolic_cost=RAMP_START_COST, heritable=heritable,
                                                    mutation_std=mutation_std, random_control=random_control)
        if life.sum() == 0:
            return {'survived_ramp': False, 'final_live': 0}

    # gradual, linear ramp from RAMP_START_COST to RAMP_END_COST over RAMP_STEPS
    for i in range(RAMP_STEPS):
        current_cost = RAMP_START_COST + (RAMP_END_COST - RAMP_START_COST) * (i / RAMP_STEPS)
        life, energy, trait = step_with_heredity(life, energy, trait, rng,
                                                    metabolic_cost=current_cost, heritable=heritable,
                                                    mutation_std=mutation_std, random_control=random_control)
        if life.sum() == 0:
            return {'survived_ramp': False, 'final_live': 0}

    return {'survived_ramp': True, 'final_live': int(life.sum())}


if __name__ == "__main__":
    print(f"Gradual ramp test: metabolic cost {RAMP_START_COST} -> {RAMP_END_COST} over {RAMP_STEPS} steps "
          f"(vs. original sudden jump to {RAMP_END_COST})\n")

    print(f"FIXED-TRAIT CONTROL (no heredity, no variation), {N_SEEDS} seeds")
    control_results = [run_ramp_test(heritable=False, seed=s) for s in range(N_SEEDS)]
    control_survived = sum(r['survived_ramp'] for r in control_results)
    print(f"  survived: {control_survived}/{N_SEEDS}\n")

    print(f"REAL HEREDITY (parent-average + mutation), {N_SEEDS} seeds")
    heredity_results = [run_ramp_test(heritable=True, seed=s, random_control=False) for s in range(N_SEEDS)]
    heredity_survived = sum(r['survived_ramp'] for r in heredity_results)
    print(f"  survived: {heredity_survived}/{N_SEEDS}\n")

    print(f"RANDOM REASSIGNMENT (fresh random trait every birth), {N_SEEDS} seeds")
    random_results = [run_ramp_test(heritable=True, seed=s, random_control=True) for s in range(N_SEEDS)]
    random_survived = sum(r['survived_ramp'] for r in random_results)
    print(f"  survived: {random_survived}/{N_SEEDS}\n")

    print(f"{'='*60}")
    print(f"Fixed-trait control:  {control_survived}/{N_SEEDS}")
    print(f"Real heredity:        {heredity_survived}/{N_SEEDS}")
    print(f"Random reassignment:  {random_survived}/{N_SEEDS}")
