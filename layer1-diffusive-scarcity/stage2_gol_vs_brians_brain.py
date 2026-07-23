"""
LAYER 1, STAGE 2, CONDITION B: GoL vs Brian's Brain, competing for a
shared, diffusing energy field at D_bg = 0.05 (Brian's Brain's own
calibrated threshold, giving both species enough ambient energy to
attempt ignition from step zero).

State encoding: 0=OFF, 1=GOL, 2=BB_FIRING, 3=BB_REFRACTORY.

MUTUALLY BLIND RULES: GoL's survival/birth logic counts only
GOL-occupied neighbors; Brian's Brain's ignition logic counts only
BB_FIRING neighbors. Neither rule can see or react to the other
species' presence directly -- the ONLY channel of interaction is
through the shared energy field (depletion and diffusion). This
isolates energetic competition from any confound of direct topological
interference.

NO MID-STATE TAKEOVERS: a cell occupied by either species evaluates
only its own species' transition logic. A cell can only change species
by first dying back to OFF, then being recolonized on a later step.

CONTESTED OFF CELLS: an OFF cell simultaneously eligible for a GOL
birth (exactly 3 GOL neighbors) and a BB ignition (exactly 2 BB_FIRING
neighbors) is resolved by a neutral 50/50 coin flip -- not by relative
neighbor count or energy weighting, since the two rules' neighbor-count
conventions are not on a comparable scale and any such resolution would
bake in an arbitrary asymmetry.

SYMMETRIC METABOLIC COST: both species pay FLIP_COST=1.0 for any state
change (GOL death, GOL birth, BB ignition, BB's two mandatory internal
transitions); staying in the same state costs nothing. This isolates
rule TOPOLOGY (facultative vs. obligate) as the sole variable in this
first experiment, before any cost asymmetry is introduced.
"""

import numpy as np
from collections import Counter
import math

N = 64
FLIP_COST = 1.0
ENERGY_CEILING = 10.0 * FLIP_COST
WARMUP_STEPS = 200
WINDOW_STEPS = 100
INIT_DENSITY_EACH = 0.10  # each species starts at this density, randomly interspersed

KERNEL_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
ORTHOGONAL_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

OFF, GOL, BB_FIRING, BB_REFRACTORY = 0, 1, 2, 3


def count_neighbors(mask):
    count = np.zeros(mask.shape, dtype=int)
    for dr, dc in KERNEL_OFFSETS:
        count += np.roll(np.roll(mask, dr, axis=0), dc, axis=1)
    return count


def propose_next(state, rng):
    gol_mask = state == GOL
    bb_firing_mask = state == BB_FIRING
    off_mask = state == OFF

    gol_neighbor_count = count_neighbors(gol_mask.astype(int))
    bb_firing_neighbor_count = count_neighbors(bb_firing_mask.astype(int))

    proposed = np.full_like(state, OFF)

    # GOL: survives on its own neighbor count only (blind to BB)
    gol_survives = gol_mask & ((gol_neighbor_count == 2) | (gol_neighbor_count == 3))
    proposed[gol_survives] = GOL
    # GOL death (gol_mask & ~gol_survives) -> proposed stays OFF (default)

    # BB: mandatory forced transitions, regardless of neighbors
    proposed[state == BB_FIRING] = BB_REFRACTORY
    proposed[state == BB_REFRACTORY] = OFF

    # OFF cell resolution: GOL birth eligibility, BB ignition eligibility, blind to each other
    gol_birth_eligible = off_mask & (gol_neighbor_count == 3)
    bb_ignition_eligible = off_mask & (bb_firing_neighbor_count == 2)

    both_eligible = gol_birth_eligible & bb_ignition_eligible
    only_gol = gol_birth_eligible & ~bb_ignition_eligible
    only_bb = bb_ignition_eligible & ~gol_birth_eligible

    coin = rng.random(state.shape) < 0.5

    proposed[only_gol] = GOL
    proposed[only_bb] = BB_FIRING
    proposed[both_eligible & coin] = GOL
    proposed[both_eligible & ~coin] = BB_FIRING

    return proposed


def diffuse_energy(energy, D_diff):
    neighbor_avg = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        neighbor_avg += np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
    neighbor_avg /= 4.0
    return energy + D_diff * (neighbor_avg - energy)


def landauer_gated_step(state, energy, D_bg, D_diff, rng, flip_cost=FLIP_COST, ceiling=ENERGY_CEILING):
    proposed = propose_next(state, rng)
    flip_mask = proposed != state

    energy = energy + D_bg
    energy = diffuse_energy(energy, D_diff)

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


def boundary_energy_gap(state, energy):
    """Mean energy of OFF cells adjacent to GOL only, vs. OFF cells
    adjacent to BB (either substate) only -- excludes OFF cells
    adjacent to BOTH, for a clean, uncontaminated signal per species."""
    gol_mask = (state == GOL).astype(int)
    bb_mask = ((state == BB_FIRING) | (state == BB_REFRACTORY)).astype(int)
    adj_gol = count_neighbors(gol_mask) > 0
    adj_bb = count_neighbors(bb_mask) > 0
    off_mask = state == OFF

    off_near_gol_only = off_mask & adj_gol & ~adj_bb
    off_near_bb_only = off_mask & adj_bb & ~adj_gol

    e_near_gol = float(energy[off_near_gol_only].mean()) if off_near_gol_only.any() else None
    e_near_bb = float(energy[off_near_bb_only].mean()) if off_near_bb_only.any() else None
    return e_near_gol, e_near_bb


def net_boundary_flux(state, energy, D_diff):
    """Direct measurement: at OFF cells sitting between GOL and BB
    territory (adjacent to both), compute the actual diffusion term
    contribution from each side separately, to see which direction
    energy is really moving at the contested boundary."""
    gol_mask = (state == GOL).astype(int)
    bb_mask = ((state == BB_FIRING) | (state == BB_REFRACTORY)).astype(int)
    adj_gol = count_neighbors(gol_mask) > 0
    adj_bb = count_neighbors(bb_mask) > 0
    contested_off = (state == OFF) & adj_gol & adj_bb

    if not contested_off.any():
        return None

    # for each contested OFF cell, average energy of GOL neighbors vs BB neighbors specifically
    gol_energy_sum = np.zeros_like(energy)
    gol_neighbor_n = np.zeros_like(energy)
    bb_energy_sum = np.zeros_like(energy)
    bb_neighbor_n = np.zeros_like(energy)
    for dr, dc in ORTHOGONAL_OFFSETS:
        shifted_state = np.roll(np.roll(state, dr, axis=0), dc, axis=1)
        shifted_energy = np.roll(np.roll(energy, dr, axis=0), dc, axis=1)
        is_gol_neighbor = shifted_state == GOL
        is_bb_neighbor = (shifted_state == BB_FIRING) | (shifted_state == BB_REFRACTORY)
        gol_energy_sum += np.where(is_gol_neighbor, shifted_energy, 0.0)
        gol_neighbor_n += is_gol_neighbor.astype(float)
        bb_energy_sum += np.where(is_bb_neighbor, shifted_energy, 0.0)
        bb_neighbor_n += is_bb_neighbor.astype(float)

    valid = contested_off & (gol_neighbor_n > 0) & (bb_neighbor_n > 0)
    if not valid.any():
        return None
    avg_gol_side = (gol_energy_sum[valid] / gol_neighbor_n[valid]).mean()
    avg_bb_side = (bb_energy_sum[valid] / bb_neighbor_n[valid]).mean()
    # positive = energy flows from GOL side toward BB side (GOL side is higher)
    return float(avg_gol_side - avg_bb_side)


def run_condition(D_bg, D_diff, seed=0, warmup=WARMUP_STEPS, window=WINDOW_STEPS, n_mi_pairs=150):
    rng = np.random.default_rng(seed)
    state = np.full((N, N), OFF, dtype=int)
    r = rng.random((N, N))
    state[r < INIT_DENSITY_EACH] = GOL
    state[(r >= INIT_DENSITY_EACH) & (r < 2 * INIT_DENSITY_EACH)] = BB_FIRING
    energy = np.zeros((N, N))

    extinction_step = {'GOL': None, 'BB': None}

    for step in range(warmup):
        state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng)
        n_gol = int((state == GOL).sum())
        n_bb = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
        if n_gol == 0 and extinction_step['GOL'] is None:
            extinction_step['GOL'] = step
        if n_bb == 0 and extinction_step['BB'] is None:
            extinction_step['BB'] = step

    trajectory_bb = np.zeros((window, N, N), dtype=int)
    for t in range(window):
        trajectory_bb[t] = (state == BB_FIRING) | (state == BB_REFRACTORY)
        state, energy, _ = landauer_gated_step(state, energy, D_bg, D_diff, rng)
        n_gol = int((state == GOL).sum())
        n_bb = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
        if n_gol == 0 and extinction_step['GOL'] is None:
            extinction_step['GOL'] = warmup + t
        if n_bb == 0 and extinction_step['BB'] is None:
            extinction_step['BB'] = warmup + t

    n_gol_final = int((state == GOL).sum())
    n_bb_final = int(((state == BB_FIRING) | (state == BB_REFRACTORY)).sum())
    total_occupied = n_gol_final + n_bb_final
    gol_territory_frac = n_gol_final / total_occupied if total_occupied > 0 else None
    bb_territory_frac = n_bb_final / total_occupied if total_occupied > 0 else None

    e_near_gol, e_near_bb = boundary_energy_gap(state, energy)
    flux = net_boundary_flux(state, energy, D_diff)
    mean_gol_cell_energy = float(energy[state == GOL].mean()) if n_gol_final > 0 else None

    # BB coherence: MI among cells that were ever BB-occupied during the window
    rng_mi = np.random.default_rng(seed + 50000)
    mis = []
    for _ in range(n_mi_pairs):
        r_, c_ = rng_mi.integers(0, N), rng_mi.integers(0, N)
        dr, dc = rng_mi.choice([-1, 0, 1]), rng_mi.choice([-1, 0, 1])
        if dr == 0 and dc == 0:
            continue
        r2, c2 = (r_ + dr) % N, (c_ + dc) % N
        x = trajectory_bb[:-1, r_, c_]
        y = trajectory_bb[1:, r2, c2]
        mis.append(mutual_information_discrete(x, y))
    bb_coherence = float(np.mean(mis)) if mis else 0.0

    return {
        'D_bg': D_bg, 'D_diff': D_diff,
        'n_gol_final': n_gol_final, 'n_bb_final': n_bb_final,
        'gol_territory_frac': gol_territory_frac, 'bb_territory_frac': bb_territory_frac,
        'e_near_gol': e_near_gol, 'e_near_bb': e_near_bb,
        'mean_gol_cell_energy': mean_gol_cell_energy,
        'net_boundary_flux': flux,
        'bb_coherence': bb_coherence,
        'gol_extinct_step': extinction_step['GOL'], 'bb_extinct_step': extinction_step['BB'],
    }


if __name__ == "__main__":
    print("Sanity check: GoL vs Brian's Brain, single run\n")
    r = run_condition(D_bg=0.05, D_diff=0.05, seed=0, warmup=200, window=100, n_mi_pairs=100)
    for k, v in r.items():
        print(f"  {k}: {v}")
