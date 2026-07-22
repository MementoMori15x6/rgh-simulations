"""
STAGE 6: single-parent inheritance variant.

The Stage 5 long-run test found mean trait STABILIZES rather than
eroding toward zero, and proposed a specific mechanistic hypothesis:
averaging a birth's trait across all 3 live GoL-neighbor "parents"
structurally pulls any low-trait mutant back toward the local mean,
preventing a "pure cheater lineage" from breeding true and spreading.

This tests that hypothesis directly: instead of averaging, each birth
copies the trait of a SINGLE randomly-chosen parent (+ mutation) --
also a more biologically natural analog of actual cellular reproduction
(binary fission copies one parent, it does not average several). If the
averaging hypothesis is correct, single-parent inheritance should let a
low-trait mutant lineage breed true more easily, and we should now see
real erosion of mean trait over the same long run where averaging
showed none.
"""

import numpy as np
from stage1_energy_baseline import gol_neighbor_count, N, METABOLIC_COST, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION
from stage1_naive_baseline import neutral_transfer, MUTATION_STD
from stage3_contribution_mechanism import CONTRIBUTION_RATE


def step_with_contribution_single_parent(life, energy, trait, rng, metabolic_cost=METABOLIC_COST,
                                            mutation_std=MUTATION_STD, contribution_rate=CONTRIBUTION_RATE):
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    energy = neutral_transfer(energy, life, rng)

    give_amount = np.where(life == 1, trait * contribution_rate, 0.0)
    energy = energy - give_amount
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

    # SINGLE-PARENT INHERITANCE: for each birth, randomly select ONE of
    # its (exactly 3) live neighbors and copy that parent's trait, rather
    # than averaging all 3. Implemented by picking a random one of the 8
    # neighbor OFFSETS per birth cell, restricted to positions that are
    # actually alive, so each birth's single parent is a real live neighbor.
    new_birth_trait = trait.copy()
    if born.any():
        rows, cols = np.where(born)
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r, c in zip(rows.tolist(), cols.tolist()):
            live_neighbor_traits = []
            for dr, dc in offsets:
                rr, cc = (r + dr) % n_rows, (c + dc) % n_cols
                if life[rr, cc] == 1:
                    live_neighbor_traits.append(trait[rr, cc])
            if live_neighbor_traits:
                chosen_parent_trait = live_neighbor_traits[rng.integers(0, len(live_neighbor_traits))]
                mutation = rng.normal(0, mutation_std)
                new_birth_trait[r, c] = np.clip(chosen_parent_trait + mutation, 0.0, 1.0)

    life_next = np.zeros_like(life)
    life_next[survives & (energy > 0)] = 1
    life_next[born & (energy > 0)] = 1
    energy = np.clip(energy, 0, None)

    trait_next = np.where(survives & (energy > 0), trait, np.where(born & (energy > 0), new_birth_trait, trait))

    return life_next, energy, trait_next


if __name__ == "__main__":
    print("Sanity check: single-parent inheritance runs and produces bounded dynamics.\n")
    from stage1b_robustness_check import random_soup_seed
    rng = np.random.default_rng(0)
    life, energy = random_soup_seed(N, 0.25, rng)
    trait = rng.random((N, N))

    for step in range(1500):
        life, energy, trait = step_with_contribution_single_parent(life, energy, trait, rng, contribution_rate=0.03)
        if step % 200 == 0:
            live_mask = life == 1
            print(f"step {step}: live={life.sum():>4} "
                  f"trait_mean={trait[live_mask].mean() if live_mask.any() else None}")
        if life.sum() == 0:
            print(f"EXTINCT at step {step}")
            break
    else:
        print(f"\nSurvived. Final live cells: {life.sum()}")
