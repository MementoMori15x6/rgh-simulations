"""
LAYER 0 EXTENDED TO TRANSFORMATION: Landauer-gated state transitions.

Every prior Layer 0 test let the rule execute unconditionally and used
energy only to determine whether the RESULT survived afterward. This
is a genuinely different mechanism: energy gates whether the proposed
transition can happen AT ALL. Each step:

  1. Compute what standard Game-of-Life would propose for every cell
     (neighbor-count rule), without applying it yet.
  2. Any cell whose proposed state differs from its current state is a
     BIT FLIP (Landauer's formulation: a state change that must be paid
     for). A cell that would stay the same costs nothing -- static
     cells do no thermodynamic work.
  3. A cell can only execute its proposed flip if it has enough energy
     to pay FLIP_COST. If not, the cell is FROZEN -- it stays at its
     current state this step, regardless of what the rule wanted,
     because the substrate genuinely could not afford to run the rule
     there. This is the real on/off condition for Transformation itself
     that no previous Layer 0 test had.
  4. Energy accumulates via unconditional inflow D each step (no decay
     term) -- at D=1.0 (equal to FLIP_COST), every cell earns exactly
     enough per step to always afford a flip, recovering unconstrained
     GoL. At D=0, cells can never flip past whatever initial reserve
     they start with -- a true freeze. Intermediate D throttles flip
     FREQUENCY rather than hard-gating it.

TWO MEASURED QUANTITIES, over a trailing window after warmup:
  Phi -- flux actually consumed: total flip cost actually paid,
    measured directly (not assumed).
  C -- complexity: mean time-lagged mutual information between live
    cells and their immediate neighbors' trajectories, reusing the
    validated binary MI estimator from the Axiom 1 GoL-extension work.
    This has the right shape for what we need: near-zero for a frozen
    grid (no variance to have information about) AND near-zero for
    genuinely incoherent noise (neighbors don't predict each other) --
    unlike Lempel-Ziv complexity, which rises monotonically with
    randomness and cannot distinguish structure from noise.

eta_T = C / Phi is the thermodynamic efficiency of computation.
"""

import numpy as np
from collections import Counter
import math

N = 64
FLIP_COST = 1.0
ENERGY_CEILING = 10.0 * FLIP_COST  # bounds growth, doesn't change qualitative dynamics
WARMUP_STEPS = 200
WINDOW_STEPS = 75
SOUP_DENSITY = 0.25

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def gol_propose(life):
    """Standard GoL neighbor-count rule, returns the PROPOSED next
    state without applying any gating."""
    neighbor_count = np.zeros_like(life)
    for dr, dc in KERNEL_OFFSETS:
        neighbor_count += np.roll(np.roll(life, dr, axis=0), dc, axis=1)
    proposed = np.zeros_like(life)
    proposed[(life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))] = 1
    proposed[(life == 0) & (neighbor_count == 3)] = 1
    return proposed


def landauer_gated_step(life, energy, D, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    proposed = gol_propose(life)
    flip_mask = proposed != life

    energy = energy + D  # unconditional inflow, no decay
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


def run_condition(D, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS, n_mi_pairs=200):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.zeros((N, N))

    for _ in range(warmup):
        life, energy, _ = landauer_gated_step(life, energy, D)

    trajectory = np.zeros((window, N, N), dtype=int)
    total_flips = 0
    for t in range(window):
        trajectory[t] = life
        life, energy, flips = landauer_gated_step(life, energy, D)
        total_flips += int(flips.sum())

    phi = total_flips * FLIP_COST / (window * N * N)  # normalized: flux per cell per step

    # sample random adjacent pairs for MI (regardless of life state --
    # the trajectory itself, 0/1, is the signal)
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
    print("Sanity check: Landauer-gated step at a few D values\n")
    for D in [0.0, 0.3, 0.6, 1.0]:
        r = run_condition(D, seed=0, warmup=50, window=30, n_mi_pairs=50)
        print(f"D={D}: phi={r['phi']:.5f}, C={r['C']:.5f}, final_live={r['final_live']}")
