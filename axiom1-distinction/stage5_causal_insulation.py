"""
STAGE 5: causal insulation test via time-lagged mutual information.

Question: do the boundaries of spontaneously-ignited Gray-Scott spots
(from stage 4's correlated-noise ignition) show measurably REDUCED
information coupling across the boundary, compared to coupling within
a region (interior-interior or background-background)?

This is the actual test of "the system carved a causal partition out
of uniform potential" -- Axiom 1's claim in information-theoretic terms,
rather than just visual/statistical terms (spots existing).

Method:
  1. Run the strongest-igniting condition from stage 4 to let spots form.
  2. Continue running and RECORD the full V-trajectory at every cell for
     a trailing window (needed to compute mutual information, which
     requires a time series, not a single snapshot).
  3. Classify every live cell pair (4-connected neighbors) into:
       - INTERIOR: both cells inside the same spot, neither touching background
       - BOUNDARY: one cell inside a spot, adjacent cell is background (outside)
       - BACKGROUND: both cells in background, far from any spot
  4. Compute time-lagged mutual information for each pair category,
     using a histogram-based MI estimator (simple, transparent, doesn't
     require a black-box library).
  5. Compare: is BOUNDARY MI reliably lower than INTERIOR MI and
     BACKGROUND MI?

Design choices flagged explicitly:
  - MI estimated via binned histograms (10 bins per variable) -- a
    standard, simple approach. Choice of bin count is somewhat arbitrary
    but held constant across all three categories for fair comparison.
  - Lag = 1 step (the shortest meaningful lag, most likely to show real
    coupling if any exists; longer lags would show weaker coupling
    everywhere and could wash out real differences).
  - "Background far from any spot" means background cells whose nearest
    spot boundary is at least 3 cells away, to avoid diffusion-mediated
    coupling that's still "boundary-adjacent" in effect even if not
    literally touching.
"""

import numpy as np
from scipy import ndimage
from stage1_grayscott import gray_scott_step, KNOWN_REGIMES
from stage4_correlated_noise import correlated_noise_v, init_with_v_noise

N = 100
IGNITE_STEPS = 3000     # let the pattern form and stabilize first
RECORD_STEPS = 200      # then record this many steps of trajectory for MI estimation
LAG = 1
N_BINS = 10

def mutual_information(x, y, n_bins=N_BINS):
    """
    Simple histogram-based mutual information estimator.
    MI(X;Y) = sum_xy p(x,y) * log2( p(x,y) / (p(x)*p(y)) )
    """
    x = np.asarray(x)
    y = np.asarray(y)
    # use consistent bin edges based on the pooled range for stability
    lo = min(x.min(), y.min())
    hi = max(x.max(), y.max())
    if hi - lo < 1e-12:
        return 0.0  # no variance, no information
    bins = np.linspace(lo, hi, n_bins + 1)

    joint_hist, _, _ = np.histogram2d(x, y, bins=[bins, bins])
    joint_p = joint_hist / joint_hist.sum()

    px = joint_p.sum(axis=1)
    py = joint_p.sum(axis=0)

    mi = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if joint_p[i, j] > 0 and px[i] > 0 and py[j] > 0:
                mi += joint_p[i, j] * np.log2(joint_p[i, j] / (px[i] * py[j]))
    return max(mi, 0.0)  # numerical noise can push slightly negative


def classify_cell_pairs(V_snapshot, labeled_spots, n_spots):
    """
    Returns three lists of ((r1,c1), (r2,c2)) pairs for INTERIOR,
    BOUNDARY, and BACKGROUND categories, using 4-connected neighbors.
    """
    n_rows, n_cols = V_snapshot.shape
    is_spot = labeled_spots > 0

    # distance from every background cell to nearest spot cell (for the
    # "far from any spot" background criterion)
    dist_to_spot = ndimage.distance_transform_edt(~is_spot)

    interior_pairs = []
    boundary_pairs = []
    background_pairs = []

    for r in range(n_rows):
        for c in range(n_cols):
            for dr, dc in [(0, 1), (1, 0)]:  # right and down neighbor (avoid double-count)
                r2, c2 = (r + dr) % n_rows, (c + dc) % n_cols
                a_spot = is_spot[r, c]
                b_spot = is_spot[r2, c2]

                if a_spot and b_spot:
                    interior_pairs.append(((r, c), (r2, c2)))
                elif a_spot != b_spot:
                    boundary_pairs.append(((r, c), (r2, c2)))
                else:
                    # both background -- only count as "far background" if
                    # BOTH cells are at least 3 cells from any spot
                    if dist_to_spot[r, c] >= 3 and dist_to_spot[r2, c2] >= 3:
                        background_pairs.append(((r, c), (r2, c2)))

    return interior_pairs, boundary_pairs, background_pairs


if __name__ == "__main__":
    print("Igniting pattern (amp=0.10, corr_len=1.0, the strongest condition from stage 4)...")
    rng = np.random.default_rng(123)
    v_field = correlated_noise_v(N, N, rng, amplitude=0.10, correlation_length=1.0)
    U, V = init_with_v_noise(N, N, v_field, rng=rng)
    params = KNOWN_REGIMES["spots"]

    for step in range(IGNITE_STEPS):
        U, V = gray_scott_step(U, V, **params)

    print(f"Post-ignition V field: mean={V.mean():.4f} std={V.std():.4f}\n")

    print(f"Recording {RECORD_STEPS} steps of trajectory for MI estimation...")
    trajectory = np.zeros((RECORD_STEPS, N, N))
    for t in range(RECORD_STEPS):
        trajectory[t] = V
        U, V = gray_scott_step(U, V, **params)

    print("Classifying cell pairs using final-snapshot spot structure...")
    final_snapshot = trajectory[-1]
    threshold = final_snapshot.mean() + 0.5 * final_snapshot.std()
    binary = final_snapshot > threshold
    labeled, n_spots = ndimage.label(binary)
    print(f"  Found {n_spots} discrete spots at classification time.\n")

    interior_pairs, boundary_pairs, background_pairs = classify_cell_pairs(
        final_snapshot, labeled, n_spots)

    print(f"Pair counts: INTERIOR={len(interior_pairs)}, BOUNDARY={len(boundary_pairs)}, "
          f"BACKGROUND={len(background_pairs)}\n")

    def sample_and_measure(pairs, label, n_sample=300):
        if len(pairs) == 0:
            print(f"{label}: no pairs available.")
            return None
        rng_local = np.random.default_rng(0)
        n_sample = min(n_sample, len(pairs))
        idxs = rng_local.choice(len(pairs), size=n_sample, replace=False)
        mis = []
        for idx in idxs:
            (r1, c1), (r2, c2) = pairs[idx]
            x = trajectory[:-LAG, r1, c1]
            y = trajectory[LAG:, r2, c2]
            mi = mutual_information(x, y)
            mis.append(mi)
        mean_mi = np.mean(mis)
        std_mi = np.std(mis)
        print(f"{label}: n_pairs_sampled={n_sample}, mean_MI={mean_mi:.4f} (std {std_mi:.4f})")
        return mis

    print("Time-lagged (lag=1) mutual information by pair category:")
    print("(LOWER MI across boundary would indicate real causal insulation)\n")

    interior_mis = sample_and_measure(interior_pairs, "INTERIOR (spot-spot)")
    boundary_mis = sample_and_measure(boundary_pairs, "BOUNDARY (spot-background)")
    background_mis = sample_and_measure(background_pairs, "BACKGROUND (far-far)")

    if interior_mis is not None and boundary_mis is not None:
        print(f"\nInterior vs Boundary gap: {np.mean(interior_mis) - np.mean(boundary_mis):+.4f}")
    if background_mis is not None and boundary_mis is not None:
        print(f"Background vs Boundary gap: {np.mean(background_mis) - np.mean(boundary_mis):+.4f}")
