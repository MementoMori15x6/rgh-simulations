"""
STAGE 1: naive self-replication baseline (Parasitic Crucible test, Claim 1).

The trait here is heritable and mutating (same inheritance mechanism
validated in the Heredity/Variation work), but FUNCTIONALLY INERT -- it
does not affect energy transfer, replication cost, or anything else. It
exists purely as a lineage marker, so we can identify related
individuals for the ablation test below, without introducing any real
functional differentiation. This is the honest "naive replication, no
constraint" baseline Claim 1 predicts should plateau at uniform,
undifferentiated copying.

ABLATION METHODOLOGY (the operational definition of "genuinely
collective, mutually-dependent organization" used throughout this
test): at equilibrium, remove a population subgroup defined by a
specific trait-value band, and separately remove an equally-sized
RANDOM subgroup (regardless of trait). Compare the harm done to the
remaining population in each case.

  - If specific-band removal hurts about the SAME as random removal:
    individuals are functionally interchangeable regardless of trait/
    lineage -- a Level 0 signature, no real interdependency.
  - If specific-band removal hurts SUBSTANTIALLY MORE than random
    removal: the population depends on having multiple distinct
    trait-groups present, not just raw numbers -- a Level 1 signature,
    real functional interdependency.

This baseline is expected (per Claim 1) to show NO difference between
specific and random removal -- confirming both that naive replication
plateaus at undifferentiated copying, AND that the ablation test itself
is not biased (a known-inert trait should not show a fake signal).
"""

import numpy as np
from stage1_energy_baseline import gol_neighbor_count, N, METABOLIC_COST, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION
from stage1b_robustness_check import random_soup_seed

DIFFUSION_RATE = 0.1
EXPLOIT_RATE = 0.4
MUTUALISM_COST = 0.01
MUTUALISM_BONUS = 0.03
NEUTRAL_MUTUALISM_PROB = 0.5   # fixed, trait-independent -- the trait has NO effect here
MUTATION_STD = 0.05


def neutral_transfer(energy, life, rng, exploit_rate=EXPLOIT_RATE, diffusion_rate=DIFFUSION_RATE,
                       mutualism_cost=MUTUALISM_COST, mutualism_bonus=MUTUALISM_BONUS,
                       mutualism_prob=NEUTRAL_MUTUALISM_PROB):
    """Same validated exploit/mutualism transfer, but using a FIXED
    shared probability -- trait plays no role in this decision at all."""
    n_rows, n_cols = life.shape
    energy_delta = np.zeros_like(energy)

    for dr, dc in [(0, 1), (1, 0)]:
        neighbor_life = np.roll(np.roll(life, -dr, axis=0), -dc, axis=1)
        neighbor_energy = np.roll(np.roll(energy, -dr, axis=0), -dc, axis=1)

        both_alive = (life == 1) & (neighbor_life == 1)
        choice_roll = rng.random(life.shape)
        chooses_mutualism = both_alive & (choice_roll < mutualism_prob)
        chooses_exploit = both_alive & ~chooses_mutualism

        energy_delta = np.where(chooses_mutualism, energy_delta - mutualism_cost + mutualism_bonus, energy_delta)
        neighbor_delta_mutualism = np.where(chooses_mutualism, -mutualism_cost + mutualism_bonus, 0.0)

        this_richer = energy > neighbor_energy
        uncapped_draw = exploit_rate * (energy - neighbor_energy)
        capped_draw = np.minimum(uncapped_draw, np.maximum(neighbor_energy, 0.0))
        flow_to_this_cell = np.where(
            chooses_exploit,
            np.where(this_richer, capped_draw, -diffusion_rate * (energy - neighbor_energy)),
            0.0
        )
        energy_delta = energy_delta + flow_to_this_cell
        neighbor_delta_exploit = -flow_to_this_cell

        not_both_alive = ~both_alive
        diffusion_flow = np.where(not_both_alive, diffusion_rate * (neighbor_energy - energy), 0.0)
        energy_delta = energy_delta + diffusion_flow
        neighbor_delta_diffusion = -diffusion_flow

        total_neighbor_delta = np.where(chooses_mutualism, neighbor_delta_mutualism,
                                 np.where(chooses_exploit, neighbor_delta_exploit,
                                          neighbor_delta_diffusion))
        scattered = np.roll(np.roll(total_neighbor_delta, dr, axis=0), dc, axis=1)
        energy_delta = energy_delta + scattered

    return energy + energy_delta


def step_naive(life, energy, trait, rng, metabolic_cost=METABOLIC_COST, mutation_std=MUTATION_STD):
    """Naive replication step: standard GoL + energy dynamics, trait
    inherited (parent-average + mutation) purely as an inert marker --
    it has NO effect on energy, survival, or replication cost."""
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    energy = neutral_transfer(energy, life, rng)
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

    # trait inheritance (same mechanism validated in Heredity/Variation, purely a marker here)
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
    print("Sanity check: naive replication baseline runs and produces bounded dynamics.\n")
    rng = np.random.default_rng(0)
    life = (rng.random((N, N)) < 0.25).astype(int)
    energy = np.full((N, N), 1.0)
    trait = rng.random((N, N))

    for step in range(1500):
        life, energy, trait = step_naive(life, energy, trait, rng)
        if step % 200 == 0:
            live_mask = life == 1
            print(f"step {step}: live={life.sum():>4} energy_mean={energy.mean():.4f} "
                  f"trait_mean={trait[live_mask].mean() if live_mask.any() else None}")
        if life.sum() == 0:
            print(f"EXTINCT at step {step}")
            break
    else:
        print(f"\nSurvived. Final live cells: {life.sum()}")
