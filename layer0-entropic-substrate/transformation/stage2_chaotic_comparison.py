"""
STAGE 2: chaotic rule comparison.

Same Landauer-gated mechanism as Stage 1, generalized to accept any
Life-like birth/survival rule set, so the identical protocol can run on
both GoL (B3/S23 -- known to settle toward low-flip-rate still lifes
and gliders, per the validated Persistence finding) and a genuinely
chaotic Life-like rule, B3/S1234 (birth on exactly 3 neighbors,
survival on 1-4 -- a much more permissive survival condition, well
documented to produce persistent "boiling," high-turnover dynamics that
do not settle into simple stable structures the way GoL does).

This directly tests the core thesis: does eta_T = C/Phi show a genuine
INTERIOR peak (Class 4 signature) when contrasted against a rule that
"wants" to keep consuming energy indefinitely, rather than the
monotonic plateau Stage 1 found for GoL alone?
"""

import numpy as np
from collections import Counter
import math

N = 64
FLIP_COST = 1.0
ENERGY_CEILING = 10.0 * FLIP_COST
WARMUP_STEPS = 200
WINDOW_STEPS = 75
SOUP_DENSITY = 0.25

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

RULES = {
    'GoL': {'birth': {3}, 'survive': {2, 3}},
    'DayAndNight': {'birth': {3, 6, 7, 8}, 'survive': {3, 4, 6, 7, 8}},
}


def rule_propose(life, birth_set, survive_set):
    neighbor_count = np.zeros_like(life)
    for dr, dc in KERNEL_OFFSETS:
        neighbor_count += np.roll(np.roll(life, dr, axis=0), dc, axis=1)
    proposed = np.zeros_like(life)
    survive_mask = np.isin(neighbor_count, list(survive_set))
    birth_mask = np.isin(neighbor_count, list(birth_set))
    proposed[(life == 1) & survive_mask] = 1
    proposed[(life == 0) & birth_mask] = 1
    return proposed


def landauer_gated_step(life, energy, D, birth_set, survive_set, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    proposed = rule_propose(life, birth_set, survive_set)
    flip_mask = proposed != life

    energy = energy + D
    can_afford = energy >= flip_cost
    actually_flips = flip_mask & can_afford

    life_next = np.where(actually_flips, proposed, life)
    energy_next = np.where(actually_flips, energy - flip_cost, energy)
    energy_next = np.clip(energy_next, 0, ceiling)

    return life_next, energy_next, actually_flips


def mutual_information_binary(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    joint = Counter(zip(x.tolist(), y.tolist()))
    total = len(x)
    px = Counter(x.tolist())
    py = Counter(y.tolist())
    mi = 0.0
    for (xi, yi), count in joint.items():
        p_xy = count / total
        p_x = px[xi] / total
        p_y = py[yi] / total
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return max(mi, 0.0)


def run_condition(D, rule_name, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS, n_mi_pairs=200):
    birth_set, survive_set = RULES[rule_name]['birth'], RULES[rule_name]['survive']
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.zeros((N, N))

    for _ in range(warmup):
        life, energy, _ = landauer_gated_step(life, energy, D, birth_set, survive_set)

    trajectory = np.zeros((window, N, N), dtype=int)
    total_flips = 0
    for t in range(window):
        trajectory[t] = life
        life, energy, flips = landauer_gated_step(life, energy, D, birth_set, survive_set)
        total_flips += int(flips.sum())

    phi = total_flips * FLIP_COST / (window * N * N)

    rng_mi = np.random.default_rng(seed + 50000)
    mis = []
    for _ in range(n_mi_pairs):
        r, c = rng_mi.integers(0, N), rng_mi.integers(0, N)
        dr, dc = rng_mi.choice([-1, 0, 1]), rng_mi.choice([-1, 0, 1])
        if dr == 0 and dc == 0:
            continue
        r2, c2 = (r + dr) % N, (c + dc) % N
        x = trajectory[:-1, r, c]
        y = trajectory[1:, r2, c2]
        mis.append(mutual_information_binary(x, y))

    c_mean = float(np.mean(mis)) if mis else 0.0
    final_live = int(life.sum())

    return {'D': D, 'phi': phi, 'C': c_mean, 'final_live': final_live}


if __name__ == "__main__":
    print("Sanity check: chaotic rule (B3/S1234) at a few D values, unthrottled reference\n")
    for D in [0.0, 0.3, 1.0]:
        r = run_condition(D, 'Chaotic_B3S1234', seed=0, warmup=50, window=30, n_mi_pairs=50)
        print(f"D={D}: phi={r['phi']:.5f}, C={r['C']:.5f}, final_live={r['final_live']}")
