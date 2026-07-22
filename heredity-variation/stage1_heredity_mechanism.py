"""
STAGE 1: heredity and variation, isolated from the learning mechanism.

Every prior E/A test used a SHARED, global mechanism (a memory table
consulted by the whole population, or a single global mutualism
probability). This test replaces that with a genuinely different
mechanism: each live cell carries its own inheritable, mutable trait
(a personal exploit-vs-mutualism propensity), passed to offspring at
birth with small random mutation -- real heredity and variation, with
NO individual learning at all.

INHERITANCE RULE: GoL births occur when exactly 3 neighbors are alive.
The new cell's trait is the average of its 3 "parent" cells' trait
values, plus Gaussian mutation noise (small-to-moderate step size,
per the population-genetics consensus that most mutations are small-
effect, with occasional larger ones -- flagged as a calibration choice,
adjustable if no meaningful drift is observed).

INTERACTION RULE: for each live-live pairwise interaction, the
probability of choosing mutualism (vs. exploitation) is the AVERAGE of
the two participating cells' own trait values -- a symmetric,
defensible way to let both parties' tendencies matter, since the
exploit/mutualism transfer mechanism already treats each interaction
as a single joint choice (both cells get the same outcome for a given
pairwise interaction), not an independent per-side decision.

COMPARISON: a population with heritable, mutating traits (founder
population seeded with random initial variation) vs. a population with
a FIXED, uniform trait (0.5 for every cell, forever -- no inheritance,
no mutation, no variation at all). Both otherwise identical.
"""

import numpy as np
from stage1_energy_baseline import gol_neighbor_count, N, METABOLIC_COST, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION

DIFFUSION_RATE = 0.1
EXPLOIT_RATE = 0.4
MUTUALISM_COST = 0.01
MUTUALISM_BONUS = 0.03
MUTATION_STD = 0.05   # Gaussian mutation step size -- small-to-moderate,
                      # calibration flagged as adjustable


def exploit_mutualism_transfer_trait(energy, life, trait, rng,
                                       exploit_rate=EXPLOIT_RATE, diffusion_rate=DIFFUSION_RATE,
                                       mutualism_cost=MUTUALISM_COST, mutualism_bonus=MUTUALISM_BONUS):
    """Same structure as the validated sign-fixed exploit/mutualism
    transfer, but the per-pair mutualism probability is now the AVERAGE
    of the two participating cells' own traits, not a shared global
    scalar."""
    n_rows, n_cols = life.shape
    energy_delta = np.zeros_like(energy)

    for dr, dc in [(0, 1), (1, 0)]:
        neighbor_life = np.roll(np.roll(life, -dr, axis=0), -dc, axis=1)
        neighbor_energy = np.roll(np.roll(energy, -dr, axis=0), -dc, axis=1)
        neighbor_trait = np.roll(np.roll(trait, -dr, axis=0), -dc, axis=1)

        both_alive = (life == 1) & (neighbor_life == 1)
        pair_mutualism_prob = (trait + neighbor_trait) / 2.0

        choice_roll = rng.random(life.shape)
        chooses_mutualism = both_alive & (choice_roll < pair_mutualism_prob)
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


def step_with_heredity(life, energy, trait, rng, metabolic_cost=METABOLIC_COST,
                         heritable=True, mutation_std=MUTATION_STD, random_control=False):
    """
    heritable=True, random_control=False: births inherit average parent
      trait + mutation (real heredity).
    heritable=False: births get the FIXED baseline trait (0.5) -- the
      no-heredity, no-variation control.
    random_control=True: births get a UNIFORM RANDOM trait, unrelated
      to their actual parents -- isolates whether "ongoing variation"
      alone (with no real transmission of successful parents' traits)
      produces the same effect as genuine heredity.
    """
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    energy = exploit_mutualism_transfer_trait(energy, life, trait, rng)
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

    if random_control:
        # ISOLATING CONTROL: trait unrelated to actual parents
        new_birth_trait = rng.random(trait.shape)
    elif heritable:
        mutation = rng.normal(0, mutation_std, trait.shape)
        new_birth_trait = np.clip(avg_parent_trait + mutation, 0.0, 1.0)
    else:
        new_birth_trait = np.full_like(trait, 0.5)

    life_next = np.zeros_like(life)
    life_next[survives & (energy > 0)] = 1
    life_next[born & (energy > 0)] = 1
    energy = np.clip(energy, 0, None)

    trait_next = np.where(survives & (energy > 0), trait, np.where(born & (energy > 0), new_birth_trait, trait))

    return life_next, energy, trait_next


if __name__ == "__main__":
    print("Sanity check: heritable trait mechanism runs and produces bounded dynamics.\n")
    rng = np.random.default_rng(0)
    life = (rng.random((N, N)) < 0.25).astype(int)
    energy = np.full((N, N), 1.0)
    trait = rng.random((N, N))  # random founder trait values in [0,1]

    for step in range(2000):
        life, energy, trait = step_with_heredity(life, energy, trait, rng, heritable=True)
        if step % 200 == 0:
            live_mask = life == 1
            mean_trait = trait[live_mask].mean() if live_mask.any() else None
            print(f"step {step}: live={life.sum():>4} energy_mean={energy.mean():.4f} "
                  f"mean_trait={mean_trait}")
        if life.sum() == 0:
            print(f"EXTINCT at step {step}")
            break
    else:
        print(f"\nSurvived. Final live cells: {life.sum()}, "
              f"final mean trait: {trait[life==1].mean():.4f}")
