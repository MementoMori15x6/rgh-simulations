"""
STAGE 3: Brian's Brain through the Landauer gate.

Both prior rules (GoL, Day & Night) eventually settled into a low-flux
attractor once fully unthrottled -- neither sustained genuine, ongoing
energy demand. This tests a structurally different kind of substrate:
Brian's Brain, a 3-state rule (Ready=0, Firing=1, Refractory=2) where
two of the three transitions are MANDATORY regardless of neighbors:

  - Ready (0):      becomes Firing (1) if exactly 2 Moore neighbors are
                    Firing; otherwise stays Ready. This is the only
                    state with a real "choice."
  - Firing (1):     ALWAYS becomes Refractory (2). No configuration of
                    neighbors changes this -- a forced transition.
  - Refractory (2): ALWAYS becomes Ready (0). Also forced.

Because 2 of 3 states have no "stay the same" option, this rule cannot
freeze into a static configuration the way GoL or Day & Night can --
every Firing or Refractory cell MUST attempt a flip every step. Under
energy gating, a cell that cannot afford its mandatory transition gets
frozen mid-cycle (stuck Firing, or stuck Refractory) rather than
completing its forced transition -- a genuinely different physical
interpretation (not enough energy to finish discharging/resetting)
than anything in the binary rules tested so far.

Same Landauer flip-cost accounting (any state change costs FLIP_COST,
regardless of which transition), same D sweep, same MI-based complexity
measure (extended trivially to 3 discrete states rather than 2 -- the
histogram-based estimator already handles arbitrary discrete values).
"""

import numpy as np
from collections import Counter
import math

N = 64
FLIP_COST = 1.0
ENERGY_CEILING = 10.0 * FLIP_COST
WARMUP_STEPS = 200
WINDOW_STEPS = 75
SOUP_DENSITY = 0.25  # initial fraction of cells set to Firing (rest Ready)

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def brians_brain_propose(state):
    """state: 0=Ready, 1=Firing, 2=Refractory. Returns proposed next state."""
    firing_count = np.zeros_like(state)
    firing_mask = (state == 1).astype(int)
    for dr, dc in KERNEL_OFFSETS:
        firing_count += np.roll(np.roll(firing_mask, dr, axis=0), dc, axis=1)

    proposed = np.zeros_like(state)
    # Ready cells: ignite if exactly 2 firing neighbors, else stay ready
    ready_mask = state == 0
    proposed[ready_mask & (firing_count == 2)] = 1
    proposed[ready_mask & (firing_count != 2)] = 0
    # Firing cells: ALWAYS become refractory
    proposed[state == 1] = 2
    # Refractory cells: ALWAYS become ready
    proposed[state == 2] = 0

    return proposed


def landauer_gated_step_bb(state, energy, D, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    proposed = brians_brain_propose(state)
    flip_mask = proposed != state

    energy = energy + D
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


def run_condition(D, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS, n_mi_pairs=200):
    rng = np.random.default_rng(seed)
    state = np.zeros((N, N), dtype=int)
    state[rng.random((N, N)) < SOUP_DENSITY] = 1  # seed some Firing cells, rest Ready
    energy = np.zeros((N, N))

    for _ in range(warmup):
        state, energy, _ = landauer_gated_step_bb(state, energy, D)

    trajectory = np.zeros((window, N, N), dtype=int)
    total_flips = 0
    for t in range(window):
        trajectory[t] = state
        state, energy, flips = landauer_gated_step_bb(state, energy, D)
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

    return {'D': D, 'phi': phi, 'C': c_mean, 'active_count': active_count}


if __name__ == "__main__":
    print("Sanity check: Brian's Brain, raw ungated behavior over time\n")
    rng = np.random.default_rng(0)
    state = np.zeros((N, N), dtype=int)
    state[rng.random((N, N)) < SOUP_DENSITY] = 1

    for step in range(60):
        proposed = brians_brain_propose(state)
        flips = int((proposed != state).sum())
        if step % 5 == 0:
            n_firing = int((state == 1).sum())
            n_refractory = int((state == 2).sum())
            print(f"step {step}: firing={n_firing}, refractory={n_refractory}, flips_this_step={flips}")
        state = proposed
