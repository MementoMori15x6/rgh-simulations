"""
STAGE 7: deliberate invasion test (Claim 2, sharper version).

Stage 5/6 tested SPONTANEOUS erosion via ordinary mutation and found
none. This is the more targeted, literature-aligned test: introduce a
small number of FIXED, non-mutating, zero-contribution "cheaters" into
an established Level 1 population, and track whether they can invade
and spread -- the actual hypercycle-parasite analog.

Builds directly on the validated single-parent inheritance mechanism
(Stage 6), adding a binary "is_cheater" lineage flag that travels with
whichever single parent is chosen at each birth:

  - If the chosen parent is a cheater: offspring is ALSO a cheater,
    trait fixed at exactly 0.0, NO mutation applied -- cheater lineage
    breeds perfectly true, exactly as a hypercycle parasite should.
  - If the chosen parent is not a cheater: offspring inherits trait +
    mutation as before (ordinary population).

This means cheater status is heritable and non-decaying once
introduced -- the fairest possible test of whether it can invade, since
it cannot be diluted away by mutation the way a naturally-arising
low-trait individual could.

METRIC: fraction of the live population that is cheater-lineage, over
a long run following introduction. Growing fraction = successful
invasion (evidence FOR Claim 2). Shrinking/stable-near-zero fraction =
resisted invasion (evidence AGAINST, for this substrate).
"""

import numpy as np
import statistics
from stage1_energy_baseline import gol_neighbor_count, N, METABOLIC_COST, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION
from stage1_naive_baseline import neutral_transfer, MUTATION_STD
from stage3_contribution_mechanism import CONTRIBUTION_RATE
from stage1b_robustness_check import random_soup_seed

EQUILIBRIUM_STEPS = 1500
POST_INVASION_STEPS = 15000
RECORD_INTERVAL = 200
N_CHEATERS_INTRODUCED = 5
CONFIRMED_RATE = 0.03


def step_with_cheater_lineage(life, energy, trait, is_cheater, rng, metabolic_cost=METABOLIC_COST,
                                 mutation_std=MUTATION_STD, contribution_rate=CONFIRMED_RATE):
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    energy = neutral_transfer(energy, life, rng)

    # cheaters contribute ZERO regardless of trait (trait is already 0 for
    # them, but this is explicit and robust to that invariant)
    give_amount = np.where((life == 1) & (~is_cheater), trait * contribution_rate, 0.0)
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

    # SINGLE-PARENT INHERITANCE with cheater-lineage tracking
    new_birth_trait = trait.copy()
    new_birth_is_cheater = is_cheater.copy()
    if born.any():
        rows, cols = np.where(born)
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r, c in zip(rows.tolist(), cols.tolist()):
            live_neighbor_traits = []
            live_neighbor_cheater = []
            for dr, dc in offsets:
                rr, cc = (r + dr) % n_rows, (c + dc) % n_cols
                if life[rr, cc] == 1:
                    live_neighbor_traits.append(trait[rr, cc])
                    live_neighbor_cheater.append(is_cheater[rr, cc])
            if live_neighbor_traits:
                idx = rng.integers(0, len(live_neighbor_traits))
                chosen_trait = live_neighbor_traits[idx]
                chosen_is_cheater = live_neighbor_cheater[idx]
                if chosen_is_cheater:
                    new_birth_trait[r, c] = 0.0
                    new_birth_is_cheater[r, c] = True
                else:
                    mutation = rng.normal(0, mutation_std)
                    new_birth_trait[r, c] = np.clip(chosen_trait + mutation, 0.0, 1.0)
                    new_birth_is_cheater[r, c] = False

    life_next = np.zeros_like(life)
    life_next[survives & (energy > 0)] = 1
    life_next[born & (energy > 0)] = 1
    energy = np.clip(energy, 0, None)

    alive_next = (survives | born) & (energy > 0)
    trait_next = np.where(alive_next, np.where(survives & (energy > 0), trait, new_birth_trait), trait)
    is_cheater_next = np.where(alive_next, np.where(survives & (energy > 0), is_cheater, new_birth_is_cheater), is_cheater)

    return life_next, energy, trait_next, is_cheater_next


def has_ongoing_reproduction(life, energy, trait, is_cheater, rng, rate, check_steps=300):
    """
    Precondition check: does this population have ANY ongoing birth
    activity after equilibrium? If not, cheater invasion cannot be
    meaningfully tested -- there's no reproduction for a lineage to
    spread through, and a frozen cheater fraction would misleadingly
    look like 'resistance' when it's really just absence of opportunity.
    Same discipline as the Layer 0 causal-insulation dynamic-content
    filter: check a real precondition before trusting the test.
    """
    life_check = life.copy()
    energy_check = energy.copy()
    trait_check = trait.copy()
    is_cheater_check = is_cheater.copy()
    total_births = 0
    for _ in range(check_steps):
        neighbor_count = gol_neighbor_count(life_check)
        born = (life_check == 0) & (neighbor_count == 3)
        total_births += int(born.sum())
        life_check, energy_check, trait_check, is_cheater_check = step_with_cheater_lineage(
            life_check, energy_check, trait_check, is_cheater_check, rng, contribution_rate=rate)
        if life_check.sum() == 0:
            break
    return total_births > 0


def run_invasion_trial(seed, rate=CONFIRMED_RATE, n_cheaters=N_CHEATERS_INTRODUCED,
                         eq_steps=EQUILIBRIUM_STEPS, post_steps=POST_INVASION_STEPS):
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.25, rng)
    trait = rng.random((N, N))
    is_cheater = np.zeros((N, N), dtype=bool)

    # Phase 1: reach established Level 1 equilibrium, no cheaters yet
    for step in range(eq_steps):
        life, energy, trait, is_cheater = step_with_cheater_lineage(life, energy, trait, is_cheater, rng, contribution_rate=rate)
        if life.sum() == 0:
            return None

    # PRECONDITION CHECK: does this population have real ongoing reproduction?
    if not has_ongoing_reproduction(life, energy, trait, is_cheater, rng, rate):
        return 'NO_REPRODUCTION'

    # Introduce cheaters: convert a small number of existing live cells
    live_rs, live_cs = np.where(life == 1)
    n_live = len(live_rs)
    n_to_convert = min(n_cheaters, n_live)
    convert_idx = rng.choice(n_live, size=n_to_convert, replace=False)
    for idx in convert_idx:
        r, c = live_rs[idx], live_cs[idx]
        trait[r, c] = 0.0
        is_cheater[r, c] = True

    # Phase 2: run long-term, tracking cheater fraction over time
    trace = []
    for step in range(post_steps):
        if step % RECORD_INTERVAL == 0:
            live_mask = life == 1
            n_live_now = int(live_mask.sum())
            n_cheater_now = int((live_mask & is_cheater).sum())
            cheater_frac = n_cheater_now / n_live_now if n_live_now > 0 else None
            trace.append({'step': step, 'live_count': n_live_now, 'n_cheater': n_cheater_now, 'cheater_frac': cheater_frac})

        life, energy, trait, is_cheater = step_with_cheater_lineage(life, energy, trait, is_cheater, rng, contribution_rate=rate)
        if life.sum() == 0:
            trace.append({'step': step + 1, 'live_count': 0, 'n_cheater': 0, 'cheater_frac': None})
            break

    return trace


if __name__ == "__main__":
    print(f"Invasion test: {N_CHEATERS_INTRODUCED} fixed cheaters introduced after {EQUILIBRIUM_STEPS}-step equilibrium, "
          f"tracked for {POST_INVASION_STEPS} steps, rate={CONFIRMED_RATE}")
    print("Filtering for seeds with genuine ongoing reproduction after equilibrium (a real precondition,")
    print("same discipline as the Layer 0 dynamic-content filter) before trusting the invasion test.\n")

    N_QUALIFYING_SEEDS_NEEDED = 8
    all_traces = {}
    seed = 0
    n_checked = 0
    n_no_repro = 0
    n_extinct = 0
    while len(all_traces) < N_QUALIFYING_SEEDS_NEEDED and seed < 200:
        n_checked += 1
        trace = run_invasion_trial(seed)
        if trace is None:
            n_extinct += 1
        elif trace == 'NO_REPRODUCTION':
            n_no_repro += 1
        else:
            all_traces[seed] = trace
            final = [t for t in trace if t['cheater_frac'] is not None]
            if final:
                print(f"seed {seed}: final_live={final[-1]['live_count']}, final_cheater_frac={final[-1]['cheater_frac']:.4f}")
        seed += 1

    print(f"\nChecked {n_checked} seeds: {len(all_traces)} qualifying (had ongoing reproduction), "
          f"{n_no_repro} excluded (no reproduction), {n_extinct} extinct before invasion phase")

    print(f"\n{'='*80}")
    print("CHEATER FRACTION OVER TIME (averaged across qualifying seeds)")
    print(f"{'='*80}")
    max_step = max(t['step'] for trace in all_traces.values() for t in trace if t['step'] % RECORD_INTERVAL == 0)
    for target_step in range(0, max_step + 1, RECORD_INTERVAL * 5):
        fracs = []
        n_alive = 0
        for s, trace in all_traces.items():
            matching = [t for t in trace if t['step'] == target_step]
            if matching and matching[0]['cheater_frac'] is not None:
                fracs.append(matching[0]['cheater_frac'])
                n_alive += 1
        if fracs:
            print(f"  step {target_step:>5}: mean_cheater_frac={statistics.mean(fracs):.4f} "
                  f"(n_alive_seeds={n_alive}/{len(all_traces)})")
