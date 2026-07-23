"""
LAYER 1, STAGE 1: Brian's Brain on a diffusing energy field.

Layer 0 gave every cell an independent, unconditional energy income --
structurally, no cell's activity could ever affect a neighbor's supply.
This replaces that with a genuine shared, spatially-limited resource:

  1. Small, uniform background inflow (D_bg) -- a trickle, not enough
     on its own to sustain continuous flipping.
  2. Real diffusion: energy flows from higher-energy cells to lower-
     energy neighbors each step (discrete Laplacian), exactly
     conserving total energy on the periodic grid up to the background
     inflow term. This is the same diffusion logic already validated in
     the Exploitation/Adaptation energy-CA work, applied here to a
     completely different mechanism (Landauer-gated execution).
  3. The same Landauer gate as Layer 0: a cell can only execute its
     proposed transition if its local energy covers FLIP_COST.

This is a genuinely different architecture, not a bigger version of
Layer 0: a cell's neighbors' activity can now directly affect whether
IT can afford to flip, since spending drains a shared local pool that
diffusion only slowly replenishes. The three things being tested,
impossible to even pose under Layer 0's flat-income model:

  - Self-terminating wavefronts: does an expanding Brian's Brain wave
    burn through its local energy faster than diffusion can resupply
    it, leaving a depleted "wake" behind that resists re-ignition?
  - A critical diffusion threshold: below some D_diff, do waves
    fragment into disconnected spot-oscillators because energy can't
    migrate fast enough to sustain a continuous front?
  - Non-monotonic complexity: does mean mutual information (C) peak at
    an intermediate diffusion rate, rising with coherent wave activity
    but falling if high activity causes local starvation and breakup?
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
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def brians_brain_propose(state):
    firing_count = np.zeros_like(state)
    firing_mask = (state == 1).astype(int)
    for dr, dc in KERNEL_OFFSETS:
        firing_count += np.roll(np.roll(firing_mask, dr, axis=0), dc, axis=1)

    proposed = np.zeros_like(state)
    ready_mask = state == 0
    proposed[ready_mask & (firing_count == 2)] = 1
    proposed[ready_mask & (firing_count != 2)] = 0
    proposed[state == 1] = 2
    proposed[state == 2] = 0
    return proposed


def diffuse_energy(energy, D_diff):
    """Discrete Laplacian diffusion over 4 orthogonal neighbors -- exactly
    conserves total energy on the periodic grid (pure redistribution,
    no source or sink)."""
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step_diffusive(state, energy, D_bg, D_diff, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    proposed = brians_brain_propose(state)
    flip_mask = proposed != state

    energy = energy + D_bg               # small background inflow (source term)
    energy = diffuse_energy(energy, D_diff)  # redistribute (conserving)

    can_afford = energy >= flip_cost
    actually_flips = flip_mask & can_afford

    state_next = np.where(actually_flips, proposed, state)
    energy_next = np.where(actually_flips, energy - flip_cost, energy)
    energy_next = np.clip(energy_next, 0, ceiling)

    return state_next, energy_next, actually_flips


def mutual_information_discrete(x, y):
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


def run_condition(D_bg, D_diff, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS, n_mi_pairs=200):
    rng = np.random.default_rng(seed)
    state = np.zeros((N, N), dtype=int)
    state[rng.random((N, N)) < SOUP_DENSITY] = 1
    energy = np.zeros((N, N))

    for _ in range(warmup):
        state, energy, _ = landauer_gated_step_diffusive(state, energy, D_bg, D_diff)

    trajectory = np.zeros((window, N, N), dtype=int)
    energy_trace = np.zeros((window, N, N))
    total_flips = 0
    for t in range(window):
        trajectory[t] = state
        energy_trace[t] = energy
        state, energy, flips = landauer_gated_step_diffusive(state, energy, D_bg, D_diff)
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
        mis.append(mutual_information_discrete(x, y))

    c_mean = float(np.mean(mis)) if mis else 0.0
    active_count = int(((state == 1) | (state == 2)).sum())
    mean_energy_active = float(energy_trace[-1][(state == 1) | (state == 2)].mean()) if active_count > 0 else None
    quiet_mask = (state == 0)
    mean_energy_quiet = float(energy_trace[-1][quiet_mask].mean()) if quiet_mask.any() else None

    return {'D_bg': D_bg, 'D_diff': D_diff, 'phi': phi, 'C': c_mean, 'active_count': active_count,
            'mean_energy_active': mean_energy_active, 'mean_energy_quiet': mean_energy_quiet}


if __name__ == "__main__":
    print("Sanity check: does local energy near active cells actually deplete (a real 'wake')?\n")
    for D_diff in [0.0, 0.1, 0.3, 0.5]:
        r = run_condition(D_bg=0.05, D_diff=D_diff, seed=0, warmup=100, window=50, n_mi_pairs=100)
        print(f"D_diff={D_diff}: phi={r['phi']:.5f}, C={r['C']:.5f}, active={r['active_count']}, "
              f"energy(active)={r['mean_energy_active']}, energy(quiet)={r['mean_energy_quiet']}")
