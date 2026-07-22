"""
STAGE 7: causal-insulation test, sourced vs independent ongoing noise.

Uses the exact validated MI methodology (interior/boundary/background,
time-lagged mutual information), applied to both noise-source conditions
at budget=0.05 -- a calibration where both showed substantial, non-
degenerate structure in the Stage 6 sweep. Noise injection stays ACTIVE
during the recorded trajectory window (not just at ignition), since this
is now an ongoing process, unlike every prior Layer 0 test.
"""

import numpy as np
from scipy import ndimage
from stage1_grayscott import gray_scott_step
from stage4_correlated_noise import correlated_noise_v, init_with_v_noise
from stage2_full_mi_test import mutual_information, classify_cell_pairs
from stage6_noise_source_control import (
    inject_dissipation_sourced_noise, inject_dissipation_independent_noise,
    N, Du, Dv, F, k, IGNITE_AMPLITUDE, CORRELATION_LENGTH
)

IGNITE_STEPS = 3000
RECORD_STEPS = 200
NOISE_BUDGET = 0.05


def run_full_mi_test(noise_mode, label, seed=123):
    print(f"\n{'='*60}\n{label} (noise_mode={noise_mode}, budget={NOISE_BUDGET})\n{'='*60}")
    rng = np.random.default_rng(seed)
    v_field = correlated_noise_v(N, N, rng, amplitude=IGNITE_AMPLITUDE, correlation_length=CORRELATION_LENGTH)
    U, V = init_with_v_noise(N, N, v_field, rng=rng)

    def apply_noise(U, V):
        if noise_mode == 'sourced':
            return inject_dissipation_sourced_noise(U, V, rng, budget=NOISE_BUDGET)
        elif noise_mode == 'independent':
            return inject_dissipation_independent_noise(U, V, rng, budget=NOISE_BUDGET)
        return V

    for step in range(IGNITE_STEPS):
        U, V = gray_scott_step(U, V, Du, Dv, F, k)
        V = apply_noise(U, V)
        V = np.clip(V, 0, 1)

    print(f"Post-ignition V field: mean={V.mean():.5f} std={V.std():.5f}")

    trajectory = np.zeros((RECORD_STEPS, N, N))
    for t in range(RECORD_STEPS):
        trajectory[t] = V
        U, V = gray_scott_step(U, V, Du, Dv, F, k)
        V = apply_noise(U, V)
        V = np.clip(V, 0, 1)

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
            x = trajectory[:-1, r1, c1]
            y = trajectory[1:, r2, c2]
            mis.append(mutual_information(x, y))
        mean_mi = np.mean(mis)
        print(f"  {plabel}: n={n_sample}, mean_MI={mean_mi:.4f} (std {np.std(mis):.4f})")
        return mean_mi

    i_mi = sample_and_measure(interior_pairs, "INTERIOR")
    b_mi = sample_and_measure(boundary_pairs, "BOUNDARY")
    bg_mi = sample_and_measure(background_pairs, "BACKGROUND")

    return {"V_std": V.std(), "V_mean": V.mean(), "n_spots": n_spots,
            "interior_mi": i_mi, "boundary_mi": b_mi, "background_mi": bg_mi}


if __name__ == "__main__":
    result_sourced = run_full_mi_test('sourced', "DISSIPATION-SOURCED NOISE")
    result_independent = run_full_mi_test('independent', "DISSIPATION-INDEPENDENT NOISE")

    print(f"\n{'='*70}\nSUMMARY\n{'='*70}")
    print(f"{'Condition':>14} {'V_mean':>8} {'V_std':>8} {'n_spots':>9} {'interior_MI':>12} {'boundary_MI':>12} {'background_MI':>14}")
    for name, r in [("sourced", result_sourced), ("independent", result_independent)]:
        i = f"{r['interior_mi']:.4f}" if r['interior_mi'] is not None else "N/A"
        b = f"{r['boundary_mi']:.4f}" if r['boundary_mi'] is not None else "N/A"
        bg = f"{r['background_mi']:.4f}" if r['background_mi'] is not None else "N/A"
        print(f"{name:>14} {r['V_mean']:>8.4f} {r['V_std']:>8.5f} {r['n_spots']:>9} {i:>12} {b:>12} {bg:>14}")

    if result_sourced['interior_mi'] is not None and result_sourced['boundary_mi'] is not None:
        print(f"\nSourced Interior-Boundary gap: {result_sourced['interior_mi'] - result_sourced['boundary_mi']:+.4f}")
    if result_independent['interior_mi'] is not None and result_independent['boundary_mi'] is not None:
        print(f"Independent Interior-Boundary gap: {result_independent['interior_mi'] - result_independent['boundary_mi']:+.4f}")
