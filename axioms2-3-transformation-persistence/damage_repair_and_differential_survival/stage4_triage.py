"""
STAGE 4: triage-constrained repair.

The previous test rate-matched random/shuffled to whatever smart's
uncapped threshold happened to produce -- but since damage strikes
uniformly among ALL alive cells (not a pre-biased "likely noise"
population, as in the earlier P-filter work), most damaged cells were
real structure a moment before, so almost any repair choice looked
reasonable. Smart tied random as a result.

This stage imposes a genuine REPAIR BUDGET per damage event (default: 1),
well below the typical number of damaged cells per event (mean ~2, max
~11) -- forcing an actual triage decision. All three targeting modes
(random, smart, shuffled) are unified into one ranking function, so the
ONLY difference between them is which damaged cells they choose to spend
the same fixed budget on:
  - random: rank damaged cells in random order, take top `budget`
  - smart:  rank by REAL salvageability confidence (descending), take top `budget`
  - shuffled: rank by DECORRELATED confidence (descending), take top `budget`
"""

import numpy as np
from stage1_salvageability_memory import (
    gol_neighbor_count, N, BACKGROUND_INFLOW, BACKGROUND_DECAY,
    BIRTH_ENERGY_FRACTION, METABOLIC_COST, build_salvageability_memory
)
from stage2_damage_repair import apply_damage, build_shuffle_map, REPAIR_ENERGY_FRACTION
from vectorized_signature import encode_signature_grid
import statistics

REPAIR_BUDGET = 1  # hard cap: at most this many repairs per damage event
DAMAGE_INTERVAL = 5
MAX_STEPS = 3000
SOUP_DENSITY = 0.25


def repair_ranked(life, energy, pre_damage_life, damaged_mask, mode, memory, shuffle_map, rng, budget=REPAIR_BUDGET):
    n_rows, n_cols = life.shape
    life = life.copy()
    energy = energy.copy()

    damaged_rs, damaged_cs = np.where(damaged_mask)
    if len(damaged_rs) == 0 or budget <= 0:
        return life, energy, 0

    if mode == 'random':
        order = list(range(len(damaged_rs)))
        rng.shuffle(order)
        selected = [(damaged_rs[i], damaged_cs[i]) for i in order[:budget]]
    else:
        sig_grid = encode_signature_grid(pre_damage_life, 1)
        scored = []
        for r, c in zip(damaged_rs.tolist(), damaged_cs.tolist()):
            sig_int = int(sig_grid[r, c])
            lookup_sig = shuffle_map.get(sig_int, sig_int) if mode == 'shuffled' else sig_int
            d = memory.get(lookup_sig)
            conf = (d[0] / (d[0] + d[1])) if (d is not None and (d[0] + d[1]) > 0) else 0.0
            scored.append((conf, r, c))
        scored.sort(key=lambda x: -x[0])
        selected = [(r, c) for (_, r, c) in scored[:budget]]

    n_repaired = len(selected)
    if n_repaired == 0:
        return life, energy, 0

    neighbor_avg = (
        np.roll(energy, 1, 0) + np.roll(energy, -1, 0) +
        np.roll(energy, 1, 1) + np.roll(energy, -1, 1)
    ) / 4.0

    for r, c in selected:
        life[r, c] = 1
        restore_energy = REPAIR_ENERGY_FRACTION * neighbor_avg[r, c]
        energy[r, c] += restore_energy
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            rr, cc = (r + dr) % n_rows, (c + dc) % n_cols
            energy[rr, cc] -= restore_energy / 4.0

    energy = np.clip(energy, 0, None)
    return life, energy, n_repaired


def step_with_triage(life, energy, rng, step_num, mode, memory, shuffle_map, budget=REPAIR_BUDGET):
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
        if mode != 'none':
            life_next, energy_next, n_repaired = repair_ranked(
                life_next, energy_next, pre_damage_life, damaged_mask,
                mode, memory, shuffle_map, rng, budget=budget)

    return life_next, energy_next, n_repaired


def run_trial(mode, seed, memory, shuffle_map, max_steps=MAX_STEPS, budget=REPAIR_BUDGET):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.full((N, N), 1.0)

    total_repaired = 0
    for step in range(max_steps):
        life, energy, n_repaired = step_with_triage(life, energy, rng, step, mode, memory, shuffle_map, budget=budget)
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
    print(f"  correlation={corr:.4f}\n")

    N_TRIALS = 15
    modes = ['none', 'random', 'smart', 'shuffled']
    results = {m: [] for m in modes}

    print(f"Running {N_TRIALS} trials per condition, REPAIR_BUDGET={REPAIR_BUDGET} per damage event...")
    for seed in range(N_TRIALS):
        for mode in modes:
            r = run_trial(mode, seed, memory, shuffle_map)
            results[mode].append(r)
        print(f"  seed {seed} done")

    print("\n" + "=" * 70)
    print("RESULTS (triage-constrained, budget=1 repair per damage event)")
    print("=" * 70)
    for mode in modes:
        survived = [r['survived'] for r in results[mode]]
        final_live = [r['final_live'] for r in results[mode] if r['survived']]
        total_repaired = [r['total_repaired'] for r in results[mode]]
        n_survived = sum(survived)
        mean_live = statistics.mean(final_live) if final_live else 0
        mean_repaired = statistics.mean(total_repaired)
        print(f"{mode:>10}: survived {n_survived}/{N_TRIALS}, "
              f"mean final live (survivors)={mean_live:.1f}, "
              f"mean total repairs={mean_repaired:.1f}")
