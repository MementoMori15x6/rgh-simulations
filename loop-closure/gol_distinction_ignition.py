"""
STAGE 2: causal insulation test on GoL structures that emerged from
sparse random perturbation -- the direct GoL analog of the Gray-Scott
Axiom 1 causal-insulation result (stage5_causal_insulation.py).

Method, mirroring the Gray-Scott test exactly:
  1. Ignite from all-dead + sparse random perturbation (density=0.10,
     comfortably above the threshold found in stage1).
  2. Let the population settle (differential-survival work already
     confirms GoL populations reach a stable/oscillating remnant
     within ~1500-2000 steps).
  3. Record a trailing window of the settled trajectory.
  4. Classify live cells into INTERIOR (part of a connected structure,
     not touching background), BOUNDARY (touching background), and
     BACKGROUND (dead cells, far from any live structure).
  5. Compute time-lagged mutual information between adjacent-cell
     trajectories for each category.

Binary cell values simplify the MI estimator relative to Gray-Scott's
continuous fields -- only 2 bins per variable are needed, removing the
bin-count arbitrariness that applied there.
"""

import numpy as np
from scipy import ndimage
from collections import Counter
import math

N = 50
IGNITION_DENSITY = 0.10  # comfortably above the threshold found in stage1
SETTLE_STEPS = 1500      # let the population reach its stable/oscillating remnant
RECORD_STEPS = 200       # trailing window recorded for MI estimation
LAG = 1

KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


def gol_step(grid):
    neighbors = ndimage.convolve(grid, KERNEL, mode='wrap')
    next_grid = np.zeros_like(grid)
    next_grid[(grid == 1) & ((neighbors == 2) | (neighbors == 3))] = 1
    next_grid[(grid == 0) & (neighbors == 3)] = 1
    return next_grid


def mutual_information_binary(x, y):
    """Histogram-based MI for BINARY (0/1) time series -- only 2 bins
    per variable needed, no bin-count arbitrariness."""
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


def classify_cell_pairs(final_snapshot):
    """Classify 4-connected adjacent cell pairs into INTERIOR (both
    live), BOUNDARY (one live, one dead), BACKGROUND (both dead, far
    from any live structure)."""
    n_rows, n_cols = final_snapshot.shape
    is_live = final_snapshot == 1
    dist_to_live = ndimage.distance_transform_edt(~is_live)

    interior_pairs, boundary_pairs, background_pairs = [], [], []

    for r in range(n_rows):
        for c in range(n_cols):
            for dr, dc in [(0, 1), (1, 0)]:
                r2, c2 = (r + dr) % n_rows, (c + dc) % n_cols
                a_live, b_live = is_live[r, c], is_live[r2, c2]
                if a_live and b_live:
                    interior_pairs.append(((r, c), (r2, c2)))
                elif a_live != b_live:
                    boundary_pairs.append(((r, c), (r2, c2)))
                else:
                    if dist_to_live[r, c] >= 3 and dist_to_live[r2, c2] >= 3:
                        background_pairs.append(((r, c), (r2, c2)))

    return interior_pairs, boundary_pairs, background_pairs


if __name__ == "__main__":
    print(f"Igniting from all-dead + density={IGNITION_DENSITY} perturbation...")
    rng = np.random.default_rng(123)
    grid = (rng.random((N, N)) < IGNITION_DENSITY).astype(int)

    for step in range(SETTLE_STEPS):
        grid = gol_step(grid)
        if grid.sum() == 0:
            print("EXTINCT during settling -- cannot proceed with this seed.")
            exit()

    print(f"Post-settling: {grid.sum()} live cells\n")

    print(f"Recording {RECORD_STEPS} steps of trajectory for MI estimation...")
    trajectory = np.zeros((RECORD_STEPS, N, N), dtype=int)
    for t in range(RECORD_STEPS):
        trajectory[t] = grid
        grid = gol_step(grid)

    final_snapshot = trajectory[-1]
    interior_pairs, boundary_pairs, background_pairs = classify_cell_pairs(final_snapshot)
    print(f"Pair counts: INTERIOR={len(interior_pairs)}, BOUNDARY={len(boundary_pairs)}, "
          f"BACKGROUND={len(background_pairs)}\n")

    def sample_and_measure(pairs, label, n_sample=300, seed=0):
        if len(pairs) == 0:
            print(f"{label}: no pairs available.")
            return None
        rng_local = np.random.default_rng(seed)
        n_sample = min(n_sample, len(pairs))
        idxs = rng_local.choice(len(pairs), size=n_sample, replace=False)
        mis = []
        for idx in idxs:
            (r1, c1), (r2, c2) = pairs[idx]
            x = trajectory[:-LAG, r1, c1]
            y = trajectory[LAG:, r2, c2]
            mis.append(mutual_information_binary(x, y))
        mean_mi = np.mean(mis)
        std_mi = np.std(mis)
        print(f"{label}: n_sampled={n_sample}, mean_MI={mean_mi:.4f} (std {std_mi:.4f})")
        return mis

    print("Time-lagged (lag=1) mutual information by pair category:")
    print("(LOWER MI across boundary would indicate real causal insulation)\n")

    interior_mis = sample_and_measure(interior_pairs, "INTERIOR (structure-structure)")
    boundary_mis = sample_and_measure(boundary_pairs, "BOUNDARY (structure-background)")
    background_mis = sample_and_measure(background_pairs, "BACKGROUND (far-far)")

    if interior_mis is not None and boundary_mis is not None:
        print(f"\nInterior vs Boundary gap: {np.mean(interior_mis) - np.mean(boundary_mis):+.4f}")
    if background_mis is not None and boundary_mis is not None:
        print(f"Background vs Boundary gap: {np.mean(background_mis) - np.mean(boundary_mis):+.4f}")
