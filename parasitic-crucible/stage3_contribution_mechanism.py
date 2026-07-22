"""
STAGE 3: the contribution/helper mechanism (first real candidate for
Claim 1's escalation from naive replication to genuinely collective
organization).

Unlike the exploit/mutualism trait (a bilateral CHOICE between two
cells), this trait governs a UNILATERAL, unconditional cost: every live
cell gives away trait * CONTRIBUTION_RATE of its own energy every step,
split among its 4 orthogonal neighbors, regardless of whether they
reciprocate or whether they are even alive. High-trait cells become
"helpers" that subsidize nearby births (birth cost is already drawn
from ambient neighbor energy in the validated base mechanism -- real
contributed energy raises that ambient pool directly). Low-trait cells
free-ride, keeping their energy for themselves.

The exploit/mutualism transfer is held NEUTRAL (fixed 50/50, as in the
Stage 1 baseline) so the ONLY new variable introduced is this
contribution mechanism -- isolating its effect cleanly.

ABLATION TEST (using the now-validated, spatially-matched methodology):
does removing specifically the HIGH-TRAIT (best helper) individuals hurt
the surrounding population more than removing an equally-sized,
equally-CLUSTERED random group? If yes, that is a real Level 1 signature
-- helpers are doing genuine, hard-to-replace structural work. If no,
the population remains functionally interchangeable despite the
contribution mechanism being nominally present -- still Level 0.
"""

import numpy as np
from stage1_energy_baseline import gol_neighbor_count, N, METABOLIC_COST, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION
from stage1_naive_baseline import neutral_transfer, MUTATION_STD

CONTRIBUTION_RATE = 0.05  # fraction of trait-scaled energy given away per step -- calibration flagged


def step_with_contribution(life, energy, trait, rng, metabolic_cost=METABOLIC_COST,
                             mutation_std=MUTATION_STD, contribution_rate=CONTRIBUTION_RATE):
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    energy = neutral_transfer(energy, life, rng)

    # CONTRIBUTION STEP: each live cell gives away trait * contribution_rate,
    # split across its 4 orthogonal neighbors, unconditionally -- a real
    # cost to the giver, regardless of neighbor life state or reciprocity.
    give_amount = np.where(life == 1, trait * contribution_rate, 0.0)
    energy = energy - give_amount  # giver pays the full cost
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        shifted_give = np.roll(np.roll(give_amount, dr, axis=0), dc, axis=1)
        energy = energy + shifted_give / 4.0

    energy = energy + BACKGROUND_INFLOW
    energy = energy * (1 - BACKGROUND_DECAY)
    energy = np.where(life == 1, energy - metabolic_cost, energy)

    neighbor_energy_avg = (
        np.roll(energy, 1, 0) + np.roll(energy, -1, 0) +
        np.roll(energy, 1, 1) + np.roll(energy, -1, 1)
    ) / 4.0
    birth_cost = BIRTH_ENERGY_FRACTION * neighbor_energy_avg
    energy = np.where(born, energy + birth_cost, energy)
    cost_share = np.zeros_like(energy)
    if born.any():
        rows, cols = np.where(born)
        for r, c in zip(rows.tolist(), cols.tolist()):
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                rr, cc = (r + dr) % n_rows, (c + dc) % n_cols
                cost_share[rr, cc] += birth_cost[r, c] / 4.0
    energy = energy - cost_share

    trait_sum_alive_neighbors = np.zeros_like(trait)
    for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        shifted_life = np.roll(np.roll(life, dr, axis=0), dc, axis=1)
        shifted_trait = np.roll(np.roll(trait, dr, axis=0), dc, axis=1)
        trait_sum_alive_neighbors += shifted_life * shifted_trait
    avg_parent_trait = trait_sum_alive_neighbors / 3.0
    mutation = rng.normal(0, mutation_std, trait.shape)
    new_birth_trait = np.clip(avg_parent_trait + mutation, 0.0, 1.0)

    life_next = np.zeros_like(life)
    life_next[survives & (energy > 0)] = 1
    life_next[born & (energy > 0)] = 1
    energy = np.clip(energy, 0, None)

    trait_next = np.where(survives & (energy > 0), trait, np.where(born & (energy > 0), new_birth_trait, trait))

    return life_next, energy, trait_next


if __name__ == "__main__":
    print("Calibration check: does the contribution mechanism actually matter?\n")
    from stage1b_robustness_check import random_soup_seed
    from stage1_naive_baseline import step_naive

    for rate in [0.0, 0.02, 0.05, 0.10, 0.20]:
        rng = np.random.default_rng(0)
        life, energy = random_soup_seed(N, 0.25, rng)
        trait = rng.random((N, N))
        for step in range(1500):
            life, energy, trait = step_with_contribution(life, energy, trait, rng, contribution_rate=rate)
            if life.sum() == 0:
                break
        print(f"contribution_rate={rate}: final live={life.sum()}, "
              f"final energy_mean={energy.mean():.4f}" if life.sum() > 0 else
              f"contribution_rate={rate}: EXTINCT")
