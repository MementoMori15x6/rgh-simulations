"""
STAGE 1: baseline energy-conservation CA.

Two coupled fields per cell:
  - LIFE: standard GoL binary state (alive/dead)
  - ENERGY: a real scalar, non-negative

Rules, each an explicit design choice:

1. METABOLIC COST: every step, every LIVE cell consumes METABOLIC_COST
   energy just to continue existing. If a live cell's energy hits zero
   or below, it dies IMMEDIATELY regardless of what GoL's own rule would
   have done -- this is what gives persistence real stakes for the first
   time in this project.

2. GoL TRANSFORMATION: the standard birth/survival rule still applies
   on top of the energy check -- a cell must BOTH satisfy GoL's rule AND
   have enough energy to survive. A newly-born cell inherits a starting
   energy endowment (BIRTH_ENERGY) -- has to come from somewhere;
   flagged explicitly below.

3. DIFFUSION (the baseline, NOT exploitation): energy diffuses evenly
   between adjacent cells each step, proportional to the difference in
   energy levels (basic heat-equation-style diffusion). This is
   deliberately symmetric/cooperative -- no cell gains disproportionately
   at another's expense. This is the control condition, not the
   exploitation test.

4. ENERGY SOURCE: since metabolic cost constantly drains energy from the
   system, SOMETHING must replenish it or every run trivially starves to
   zero regardless of any other rule. We model a constant, uniform
   background energy INFLOW per step (like ambient light/chemical
   energy) -- flagged explicitly as a modeling choice, analogous to
   Gray-Scott's feed rate F.

DESIGN CHOICES FLAGGED (not discovered facts):
  - BIRTH_ENERGY: how much energy a newly-born cell starts with, and
    where it comes from (we take it from the average of contributing
    neighbors' energy, so birth isn't a free energy injection -- it's
    a REAL COST to the neighbors that enabled the birth).
  - METABOLIC_COST, DIFFUSION_RATE, BACKGROUND_INFLOW: specific
    numeric choices that will need calibration -- the first empirical
    question is whether ANY parameter regime here sustains life at all.
"""

import numpy as np
from scipy import ndimage

N = 50
METABOLIC_COST = 0.04       # energy drained per live cell per step just to exist
                            # RECALIBRATED: 0.02 was empirically inert (identical
                            # results to plain GoL with no energy constraint at all,
                            # confirmed by direct comparison). A sweep found 0.04
                            # is the lowest value producing real, non-trivial
                            # selection (76 -> 32 cells vs plain GoL on the same
                            # seed) without causing total extinction. This value
                            # sits in a narrow, non-monotonic transition zone
                            # (0.07-0.10 caused total extinction on the same seed,
                            # except for an unexplained partial survival at 0.09)
                            # -- flagged as a real, not fully understood feature
                            # of this substrate, not swept under the rug.
DIFFUSION_RATE = 0.1        # fraction of energy gradient that equalizes per step
BACKGROUND_INFLOW = 0.015   # ambient energy added per cell per step (like light/feed)
BACKGROUND_DECAY = 0.02     # fraction of energy that dissipates per step everywhere
                            # (FIX: without this, background inflow accumulates
                            # unboundedly in empty cells with nothing to spend it,
                            # since metabolic cost only drains LIVE cells. This
                            # decay term is what lets the system reach a real
                            # equilibrium instead of energy growing forever --
                            # analogous to Gray-Scott's own (F+k)*V decay term.)
BIRTH_ENERGY_FRACTION = 0.3 # fraction of avg neighbor energy a newborn cell draws

KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])

def gol_neighbor_count(life):
    return ndimage.convolve(life, KERNEL, mode='wrap')

def diffuse_energy(energy, life_mask, rate=DIFFUSION_RATE):
    """
    Simple, symmetric diffusion: each cell exchanges energy with its
    4-connected neighbors proportional to the energy difference. This is
    the BASELINE (cooperative/neutral) case -- no directional advantage.
    """
    neighbor_avg = (
        np.roll(energy, 1, axis=0) + np.roll(energy, -1, axis=0) +
        np.roll(energy, 1, axis=1) + np.roll(energy, -1, axis=1)
    ) / 4.0
    return energy + rate * (neighbor_avg - energy)

def step(life, energy):
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)

    # standard GoL rule determines CANDIDATE next-state
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    # energy diffuses regardless of life/death (background field)
    energy = diffuse_energy(energy, life)

    # background inflow, offset by background decay (FIX for unbounded growth)
    energy = energy + BACKGROUND_INFLOW
    energy = energy * (1 - BACKGROUND_DECAY)

    # metabolic cost: only currently-alive cells pay it
    energy = np.where(life == 1, energy - METABOLIC_COST, energy)

    # newborn cells draw a startup cost from local neighbor energy average
    # (a REAL cost -- birth isn't free, it draws down the surrounding field)
    neighbor_energy_avg = (
        np.roll(energy, 1, axis=0) + np.roll(energy, -1, axis=0) +
        np.roll(energy, 1, axis=1) + np.roll(energy, -1, axis=1)
    ) / 4.0
    birth_cost = BIRTH_ENERGY_FRACTION * neighbor_energy_avg
    energy = np.where(born, energy + birth_cost, energy)  # newborn RECEIVES this
    # the cost is paid by uniformly discounting the local neighborhood
    # (approximation: subtract a small share from the 4-neighborhood of
    # each newborn cell, redistributed)
    cost_share = np.zeros_like(energy)
    if born.any():
        rows, cols = np.where(born)
        for r, c in zip(rows.tolist(), cols.tolist()):
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                rr, cc = (r+dr) % n_rows, (c+dc) % n_cols
                cost_share[rr, cc] += birth_cost[r, c] / 4.0
    energy = energy - cost_share

    # final life state: survives/born from GoL AND has positive energy
    life_next = np.zeros_like(life)
    life_next[survives & (energy > 0)] = 1
    life_next[born & (energy > 0)] = 1

    # energy floor: can't go negative
    energy = np.clip(energy, 0, None)

    return life_next, energy


def init_seed(size=N, initial_energy=1.0):
    life = np.zeros((size, size), dtype=int)
    glider = np.array([[0,1,0],[0,0,1],[1,1,1]])
    life[5:8, 5:8] = glider
    life[15:18, 25:28] = glider
    life[35:38, 10:13] = glider
    block = np.array([[1,1],[1,1]])
    life[10:12, 40:42] = block
    life[40:42, 40:42] = block

    energy = np.full((size, size), initial_energy, dtype=float)
    return life, energy


if __name__ == "__main__":
    life, energy = init_seed()
    print(f"Initial: {life.sum()} live cells, energy mean={energy.mean():.4f}\n")

    for step_num in range(2000):
        life, energy = step(life, energy)
        if step_num % 200 == 0:
            print(f"step {step_num}: live_cells={life.sum():>4} "
                  f"energy_mean={energy.mean():.4f} energy_std={energy.std():.4f} "
                  f"energy_min={energy.min():.4f} energy_max={energy.max():.4f}")

        if life.sum() == 0:
            print(f"\nEXTINCTION at step {step_num}")
            break
    else:
        print(f"\nSurvived full run. Final live cells: {life.sum()}")
