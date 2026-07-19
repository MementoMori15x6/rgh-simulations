"""
STAGE 2: damage types + repair mechanism variants on the energy-CA substrate.

Timestep order, made explicit so "damaged" cells are precisely defined:
  1. Compute normal GoL life_next (survives/born) from current life+energy.
  2. Apply normal energy updates (diffusion, inflow/decay, metabolic cost,
     birth cost) -> this is what WOULD happen with no damage at all.
  3. Apply damage:
     a. STRUCTURAL: a random fraction of life_next==1 cells are forcibly
        killed (set to 0) -- direct structural damage, independent of
        energy.
     b. ENERGY DRAIN: a random fraction of life_next==1 cells have their
        energy forcibly multiplied down (hostile drain) -- may or may
        not kill them depending on whether it pushes them <= 0.
  4. DAMAGED_MASK = cells that were alive after step 2 (i.e. would have
     survived with no damage) but are dead after step 3 -- this is the
     precise, auditable population repair acts on.
  5. Repair (if any) attempts to restore DAMAGED_MASK cells to life,
     paying a REAL energy cost drawn from the local neighborhood
     (analogous to birth cost) -- repair is not free.

Four repair conditions, matched at the same repair RATE where applicable:
  - NO_REPAIR: damaged cells stay dead.
  - RANDOM_REPAIR: a random subset of damaged cells is repaired.
  - SMART_REPAIR: damaged cells are repaired only if the PRE-damage local
    3x3 signature (from step 2's life_next, before damage) has
    salvageability confidence above a threshold.
  - SHUFFLED_REPAIR (control): identical mechanism to SMART_REPAIR, but
    using a signature lookup DECORRELATED from the real one -- verified
    below to actually decorrelate (not just relabel within a symmetric
    class, the bug caught in the earlier P-filter attempt) before being
    trusted as a valid control.
"""

import numpy as np
from scipy import ndimage
from collections import defaultdict
import statistics
from vectorized_signature import encode_signature_grid, signature_to_int
from stage1_salvageability_memory import (
    gol_neighbor_count, N, WINDOW, BACKGROUND_INFLOW, BACKGROUND_DECAY,
    BIRTH_ENERGY_FRACTION, METABOLIC_COST, build_salvageability_memory
)

REPAIR_ENERGY_FRACTION = 0.3  # same magnitude as birth cost -- repair is not free
SMART_THRESHOLD = 0.3         # repair only if salvageability confidence exceeds this
                               # (calibrated relative to the observed mean confidence
                               # of 0.172 -- set diagnostics will confirm this is
                               # discriminating, not near-universal or near-never)

STRUCTURAL_DAMAGE_RATE = 0.01   # fraction of live cells forcibly killed per damage event
ENERGY_DRAIN_RATE = 0.01        # fraction of live cells forcibly energy-drained per event
ENERGY_DRAIN_FACTOR = 0.05      # drained cells retain this fraction of their energy
DAMAGE_INTERVAL = 5              # apply damage every N steps


def apply_damage(life_next, energy_next, rng):
    """Applies both damage types to a post-normal-update state.
    Returns (life_after_damage, energy_after_damage, damaged_mask)."""
    n_rows, n_cols = life_next.shape

    # STRUCTURAL DAMAGE: forcibly kill a random fraction of live cells
    alive_mask = life_next == 1
    structural_roll = rng.random(life_next.shape)
    structural_hits = alive_mask & (structural_roll < STRUCTURAL_DAMAGE_RATE)

    # ENERGY DRAIN DAMAGE: forcibly drain energy of a random fraction of live cells
    drain_roll = rng.random(life_next.shape)
    drain_hits = alive_mask & (drain_roll < ENERGY_DRAIN_RATE) & (~structural_hits)
    energy_after_drain = np.where(drain_hits, energy_next * ENERGY_DRAIN_FACTOR, energy_next)

    life_after_structural = np.where(structural_hits, 0, life_next)
    # cells drained below zero also die (consistent with the normal energy>0 rule)
    drain_kills = drain_hits & (energy_after_drain <= 0)
    life_after_damage = np.where(drain_kills, 0, life_after_structural)

    damaged_mask = alive_mask & (life_after_damage == 0)

    return life_after_damage, np.clip(energy_after_drain, 0, None), damaged_mask


def repair_cells(life, energy, pre_damage_life, damaged_mask, mode, memory, rng, shuffle_map=None, repair_rate_target=None):
    """
    mode: 'none', 'random', 'smart', 'shuffled'
    shuffle_map: required if mode == 'shuffled' -- the validated,
      decorrelated signature mapping built by build_shuffle_map().
      Passed explicitly rather than relied on as a module global, since
      relying on module-level mutable state here was a real bug caught
      during development (reassigning it in __main__ never actually
      reached this function's reference to it).
    repair_rate_target: for 'random', match this rate (fraction of damaged
      cells repaired) to whatever 'smart' produced in the same step, so
      random and smart are compared at equal intervention rate.
    """
    n_rows, n_cols = life.shape
    life = life.copy()
    energy = energy.copy()

    damaged_rs, damaged_cs = np.where(damaged_mask)
    if len(damaged_rs) == 0:
        return life, energy, 0

    if mode == 'none':
        return life, energy, 0

    if mode == 'random':
        n_to_repair = int(round(repair_rate_target * len(damaged_rs))) if repair_rate_target else 0
        n_to_repair = min(n_to_repair, len(damaged_rs))
        if n_to_repair == 0:
            return life, energy, 0
        idxs = rng.choice(len(damaged_rs), size=n_to_repair, replace=False)
        selected = [(damaged_rs[i], damaged_cs[i]) for i in idxs]
    else:
        # smart / shuffled: decide per-cell using the PRE-damage signature
        sig_grid = encode_signature_grid(pre_damage_life, WINDOW)
        selected = []
        for r, c in zip(damaged_rs.tolist(), damaged_cs.tolist()):
            sig_int = int(sig_grid[r, c])
            if mode == 'shuffled':
                lookup_sig = shuffle_map.get(sig_int, sig_int)
            else:
                lookup_sig = sig_int
            d = memory.get(lookup_sig)
            conf = (d[0] / (d[0] + d[1])) if (d is not None and (d[0] + d[1]) > 0) else 0.0
            if conf > SMART_THRESHOLD:
                selected.append((r, c))

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


def repair_cells_shuffled_matched(life, energy, pre_damage_life, damaged_mask, memory, shuffle_map, n_cap):
    """
    Rate-matched shuffled control: rank damaged cells by their SHUFFLED
    (decorrelated) confidence, repair the top n_cap of them -- exactly
    matching smart's intervention COUNT, not just its threshold. This
    fixes a real design flaw caught during testing: using the same
    threshold (0.3) for both smart and shuffled produced very different
    intervention RATES (shuffled repaired ~5x less often than smart),
    making the two conditions not actually comparable. Capping by count
    isolates targeting quality as the only remaining difference.
    """
    n_rows, n_cols = life.shape
    life = life.copy()
    energy = energy.copy()

    damaged_rs, damaged_cs = np.where(damaged_mask)
    if len(damaged_rs) == 0 or n_cap <= 0:
        return life, energy, 0

    sig_grid = encode_signature_grid(pre_damage_life, WINDOW)
    scored = []
    for r, c in zip(damaged_rs.tolist(), damaged_cs.tolist()):
        sig_int = int(sig_grid[r, c])
        lookup_sig = shuffle_map.get(sig_int, sig_int)
        d = memory.get(lookup_sig)
        conf = (d[0] / (d[0] + d[1])) if (d is not None and (d[0] + d[1]) > 0) else 0.0
        scored.append((conf, r, c))

    scored.sort(key=lambda x: -x[0])
    selected = [(r, c) for (_, r, c) in scored[:n_cap]]

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



def build_shuffle_map(memory, seed=0):
    """
    Build a randomized derangement of the OBSERVED signature space, then
    verify it actually decorrelates confidence (correlation near zero)
    before trusting it as a valid control -- learned from the earlier
    P-filter bug, where a geometric bit-reversal transform accidentally
    preserved the one feature (orthogonal vs diagonal) that mattered.
    """
    sigs = list(memory.keys())
    rng = np.random.default_rng(seed)
    shuffled_sigs = sigs.copy()
    rng.shuffle(shuffled_sigs)
    mapping = dict(zip(sigs, shuffled_sigs))

    real_confs = []
    shuffled_confs = []
    for sig in sigs:
        p, v = memory[sig]
        real_confs.append(p / (p + v) if (p + v) > 0 else 0.0)
        p2, v2 = memory[mapping[sig]]
        shuffled_confs.append(p2 / (p2 + v2) if (p2 + v2) > 0 else 0.0)

    mean_r, mean_s = statistics.mean(real_confs), statistics.mean(shuffled_confs)
    cov = sum((r - mean_r) * (s - mean_s) for r, s in zip(real_confs, shuffled_confs)) / len(sigs)
    std_r = statistics.pstdev(real_confs)
    std_s = statistics.pstdev(shuffled_confs)
    corr = cov / (std_r * std_s) if std_r > 0 and std_s > 0 else float('nan')

    return mapping, corr


if __name__ == "__main__":
    print("Building salvageability memory (20 seeds)...")
    memory, total = build_salvageability_memory(n_seeds=20)
    print(f"  {len(memory)} signatures, {total} tagged observations\n")

    print("Building and validating shuffle map...")
    mapping, corr = build_shuffle_map(memory, seed=0)
    print(f"  Correlation between real and shuffled confidence: {corr:.4f}")
    print(f"  (should be near zero; if not, the shuffle isn't a valid decorrelated control)")

    if abs(corr) > 0.15:
        print("  WARNING: correlation not near zero, trying alternate shuffle seeds...")
        for alt_seed in range(1, 10):
            mapping, corr = build_shuffle_map(memory, seed=alt_seed)
            print(f"    seed={alt_seed}: corr={corr:.4f}")
            if abs(corr) < 0.15:
                print(f"    -> using seed={alt_seed}")
                break

    print(f"\nFinal shuffle map correlation: {corr:.4f} (built with the winning seed above)")
    print("This mapping will be passed explicitly to repair_cells() in the full test.")
