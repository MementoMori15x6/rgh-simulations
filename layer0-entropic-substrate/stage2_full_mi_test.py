"""
STAGE 2: full causal-insulation MI test, Condition A vs Condition B.

Reuses the exact classification and mutual-information machinery
validated in the original Axiom 1 causal-insulation test
(stage5_causal_insulation.py), generalized to accept F, k as parameters
so the identical test can run on both the dissipative and non-dissipative
conditions for directly comparable numbers.
"""

import numpy as np
from scipy import ndimage
from collections import Counter
import math
from stage1_grayscott import gray_scott_step
from stage4_correlated_noise import correlated_noise_v, init_with_v_noise

N = 100
Du, Dv = 0.16, 0.08
IGNITE_STEPS = 3000
RECORD_STEPS = 200
LAG = 1
N_BINS = 10
IGNITE_AMPLITUDE = 0.10
CORRELATION_LENGTH = 1.0


def mutual_information(x, y, n_bins=N_BINS):
    x = np.asarray(x)
    y = np.asarray(y)
    lo = min(x.min(), y.min())
    hi = max(x.max(), y.max())
    if hi - lo < 1e-12:
        return 0.0
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
    return max(mi, 0.0)


def classify_cell_pairs(V_snapshot, labeled_spots, n_spots):
    n_rows, n_cols = V_snapshot.shape
    is_spot = labeled_spots > 0
    dist_to_spot = ndimage.distance_transform_edt(~is_spot)

    interior_pairs, boundary_pairs, background_pairs = [], [], []
    for r in range(n_rows):
        for c in range(n_cols):
            for dr, dc in [(0, 1), (1, 0)]:
                r2, c2 = (r + dr) % n_rows, (c + dc) % n_cols
                a_spot, b_spot = is_spot[r, c], is_spot[r2, c2]
                if a_spot and b_spot:
                    interior_pairs.append(((r, c), (r2, c2)))
                elif a_spot != b_spot:
                    boundary_pairs.append(((r, c), (r2, c2)))
                else:
                    if dist_to_spot[r, c] >= 3 and dist_to_spot[r2, c2] >= 3:
                        background_pairs.append(((r, c), (r2, c2)))
    return interior_pairs, boundary_pairs, background_pairs


def run_full_test(F, k, label, seed=123):
    print(f"\n{'='*60}\n{label} (F={F}, k={k})\n{'='*60}")
    rng = np.random.default_rng(seed)
    v_field = correlated_noise_v(N, N, rng, amplitude=IGNITE_AMPLITUDE, correlation_length=CORRELATION_LENGTH)
    U, V = init_with_v_noise(N, N, v_field, rng=rng)

    for step in range(IGNITE_STEPS):
        U, V = gray_scott_step(U, V, Du, Dv, F, k)

    print(f"Post-ignition V field: mean={V.mean():.5f} std={V.std():.5f}")

    trajectory = np.zeros((RECORD_STEPS, N, N))
    for t in range(RECORD_STEPS):
        trajectory[t] = V
        U, V = gray_scott_step(U, V, Du, Dv, F, k)

    final_snapshot = trajectory[-1]
    threshold = final_snapshot.mean() + 0.5 * final_snapshot.std()
    binary = final_snapshot > threshold
    labeled, n_spots = ndimage.label(binary)
    print(f"Found {n_spots} discrete spots at classification time.")

    interior_pairs, boundary_pairs, background_pairs = classify_cell_pairs(final_snapshot, labeled, n_spots)
    print(f"Pair counts: INTERIOR={len(interior_pairs)}, BOUNDARY={len(boundary_pairs)}, "
          f"BACKGROUND={len(background_pairs)}")

    def sample_and_measure(pairs, plabel, n_sample=300, s=0):
        if len(pairs) == 0:
            print(f"  {plabel}: no pairs available.")
            return None
        rng_local = np.random.default_rng(s)
        n_sample = min(n_sample, len(pairs))
        idxs = rng_local.choice(len(pairs), size=n_sample, replace=False)
        mis = []
        for idx in idxs:
            (r1, c1), (r2, c2) = pairs[idx]
            x = trajectory[:-LAG, r1, c1]
            y = trajectory[LAG:, r2, c2]
            mis.append(mutual_information(x, y))
        mean_mi = np.mean(mis)
        print(f"  {plabel}: n={n_sample}, mean_MI={mean_mi:.4f} (std {np.std(mis):.4f})")
        return mean_mi

    i_mi = sample_and_measure(interior_pairs, "INTERIOR")
    b_mi = sample_and_measure(boundary_pairs, "BOUNDARY")
    bg_mi = sample_and_measure(background_pairs, "BACKGROUND")

    return {"V_std": V.std(), "n_spots": n_spots, "interior_mi": i_mi, "boundary_mi": b_mi, "background_mi": bg_mi}


if __name__ == "__main__":
    result_a = run_full_test(F=0.035, k=0.065, label="CONDITION A (DISSIPATIVE)")
    result_b = run_full_test(F=0.0, k=0.0, label="CONDITION B (NON-DISSIPATIVE CONTROL)")

    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    print(f"{'Condition':>12} {'V_std':>10} {'n_spots':>9} {'interior_MI':>12} {'boundary_MI':>12} {'background_MI':>14}")
    for name, r in [("A (dissip.)", result_a), ("B (control)", result_b)]:
        i = f"{r['interior_mi']:.4f}" if r['interior_mi'] is not None else "N/A"
        b = f"{r['boundary_mi']:.4f}" if r['boundary_mi'] is not None else "N/A"
        bg = f"{r['background_mi']:.4f}" if r['background_mi'] is not None else "N/A"
        print(f"{name:>12} {r['V_std']:>10.5f} {r['n_spots']:>9} {i:>12} {b:>12} {bg:>14}")
