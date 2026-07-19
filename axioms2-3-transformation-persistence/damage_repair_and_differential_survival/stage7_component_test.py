"""
STAGE 7: component-size-based smart repair vs. random vs. shuffled vs. none.

Same damage mechanism, same calibrated settings (damage=0.02/0.02,
budget=2, n=50) as the local-signature test, so results are directly
comparable. The only change: targeting is based on CONNECTED-COMPONENT
SIZE (looked up in the memory built in stage6), not local 3x3 pattern.
"""

import numpy as np
import statistics
from stage1_salvageability_memory import (
    gol_neighbor_count, N, BACKGROUND_INFLOW, BACKGROUND_DECAY,
    BIRTH_ENERGY_FRACTION, METABOLIC_COST
)
from stage2_damage_repair import apply_damage, REPAIR_ENERGY_FRACTION
from stage6_component_memory import build_component_memory, component_size_grid, bucket_size, MAX_COMPONENT_SIZE_BUCKET

DAMAGE_INTERVAL = 5
MAX_STEPS = 3000
SOUP_DENSITY = 0.25
STRUCTURAL_DAMAGE_RATE = 0.02
ENERGY_DRAIN_RATE = 0.02
REPAIR_BUDGET = 2


def build_component_shuffle_map(memory, seed=0):
    sizes = list(memory.keys())
    rng = np.random.default_rng(seed)
    shuffled_sizes = sizes.copy()
    rng.shuffle(shuffled_sizes)
    mapping = dict(zip(sizes, shuffled_sizes))

    real_confs, shuffled_confs = [], []
    for s in sizes:
        p, v = memory[s]
        real_confs.append(p / (p + v) if (p + v) > 0 else 0.0)
        p2, v2 = memory[mapping[s]]
        shuffled_confs.append(p2 / (p2 + v2) if (p2 + v2) > 0 else 0.0)

    mean_r, mean_s = statistics.mean(real_confs), statistics.mean(shuffled_confs)
    cov = sum((r - mean_r) * (sc - mean_s) for r, sc in zip(real_confs, shuffled_confs)) / len(sizes)
    std_r, std_s = statistics.pstdev(real_confs), statistics.pstdev(shuffled_confs)
    corr = cov / (std_r * std_s) if std_r > 0 and std_s > 0 else float('nan')
    return mapping, corr


def repair_ranked_component(life, energy, pre_damage_life, damaged_mask, mode, memory, shuffle_map, rng, budget):
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
        comp_grid = component_size_grid(pre_damage_life)
        scored = []
        for r, c in zip(damaged_rs.tolist(), damaged_cs.tolist()):
            size = bucket_size(int(comp_grid[r, c]))
            lookup_size = shuffle_map.get(size, size) if mode == 'shuffled' else size
            d = memory.get(lookup_size)
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


def step_with_component_triage(life, energy, rng, step_num, mode, memory, shuffle_map, budget=REPAIR_BUDGET):
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
        import stage2_damage_repair as s2
        s2.STRUCTURAL_DAMAGE_RATE = STRUCTURAL_DAMAGE_RATE
        s2.ENERGY_DRAIN_RATE = ENERGY_DRAIN_RATE
        pre_damage_life = life_next.copy()
        life_next, energy_next, damaged_mask = apply_damage(life_next, energy_next, rng)
        if mode != 'none':
            life_next, energy_next, n_repaired = repair_ranked_component(
                life_next, energy_next, pre_damage_life, damaged_mask,
                mode, memory, shuffle_map, rng, budget=budget)

    return life_next, energy_next, n_repaired


def run_trial(mode, seed, memory, shuffle_map, max_steps=MAX_STEPS, budget=REPAIR_BUDGET):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.full((N, N), 1.0)

    total_repaired = 0
    for step in range(max_steps):
        life, energy, n_repaired = step_with_component_triage(life, energy, rng, step, mode, memory, shuffle_map, budget=budget)
        total_repaired += n_repaired
        if life.sum() == 0:
            return {'survived': False, 'final_live': 0, 'total_repaired': total_repaired}
        if life.sum() == life.size:
            return {'survived': False, 'final_live': int(life.sum()), 'total_repaired': total_repaired}

    return {'survived': True, 'final_live': int(life.sum()), 'total_repaired': total_repaired}


if __name__ == "__main__":
    print("Building component-size salvageability memory (20 seeds)...")
    memory, total = build_component_memory(n_seeds=20)
    print(f"  {len(memory)} buckets\n")

    print("Validating component-size shuffle map...")
    shuffle_map, corr = build_component_shuffle_map(memory, seed=0)
    print(f"  correlation={corr:.4f} (near zero = valid decorrelated control)\n")

    N_TRIALS = 50
    modes = ['none', 'random', 'smart', 'shuffled']
    results = {m: [] for m in modes}

    print(f"Running {N_TRIALS} trials per condition, damage=0.02/0.02, budget={REPAIR_BUDGET}...")
    for seed in range(N_TRIALS):
        for mode in modes:
            r = run_trial(mode, seed, memory, shuffle_map)
            results[mode].append(r)
        if seed % 10 == 0:
            print(f"  seed {seed} done")

    print("\n" + "=" * 70)
    print(f"RESULTS (component-size targeting, n={N_TRIALS})")
    print("=" * 70)
    for mode in modes:
        survived = [r['survived'] for r in results[mode]]
        final_live = [r['final_live'] for r in results[mode] if r['survived']]
        total_repaired = [r['total_repaired'] for r in results[mode]]
        n_survived = sum(survived)
        mean_live = statistics.mean(final_live) if final_live else 0
        mean_repaired = statistics.mean(total_repaired)
        print(f"{mode:>10}: survived {n_survived}/{N_TRIALS} ({100*n_survived/N_TRIALS:.0f}%), "
              f"mean_live={mean_live:.1f}, mean_repairs={mean_repaired:.1f}")
