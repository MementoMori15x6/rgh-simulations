"""
STAGE 5: causal-insulation confirmation in the partial-dissipation
Turing-unstable regime (scale ~0.90), using the exact validated MI
methodology from the original Axiom 1 result and the Layer 0 Stage 2
test -- just applied to a different (F, k) point that Stage 4's sweep
identified as pattern-forming but NOT full-strength.

This closes the gap flagged in the Layer 0 findings: variance growing
in this regime was confirmed, but causal insulation (the actual
Axiom-1-relevant signature) was not yet re-tested there specifically.
"""

import numpy as np
from scipy import ndimage
from stage1_grayscott import gray_scott_step
from stage4_correlated_noise import correlated_noise_v, init_with_v_noise
from stage2_full_mi_test import mutual_information, classify_cell_pairs

N = 100
Du, Dv = 0.16, 0.08
IGNITE_STEPS = 3000
RECORD_STEPS = 200
IGNITE_AMPLITUDE = 0.10
CORRELATION_LENGTH = 1.0
F_FULL, K_FULL = 0.035, 0.065


def run_full_mi_test(scale, label, seed=123):
    F, k = F_FULL * scale, K_FULL * scale
    print(f"\n{'='*60}\n{label} (scale={scale}, F={F:.4f}, k={k:.4f})\n{'='*60}")
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
            x = trajectory[:-1, r1, c1]
            y = trajectory[1:, r2, c2]
            mis.append(mutual_information(x, y))
        mean_mi = np.mean(mis)
        print(f"  {plabel}: n={n_sample}, mean_MI={mean_mi:.4f} (std {np.std(mis):.4f})")
        return mean_mi

    i_mi = sample_and_measure(interior_pairs, "INTERIOR")
    b_mi = sample_and_measure(boundary_pairs, "BOUNDARY")
    bg_mi = sample_and_measure(background_pairs, "BACKGROUND")

    return {"V_std": V.std(), "n_spots": n_spots, "interior_mi": i_mi, "boundary_mi": b_mi, "background_mi": bg_mi}


if __name__ == "__main__":
    result_partial = run_full_mi_test(scale=0.90, label="PARTIAL DISSIPATION (Turing-unstable, sub-full-strength)")
    result_full = run_full_mi_test(scale=1.00, label="FULL DISSIPATION (original Axiom 1 regime)")

    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    print(f"{'Condition':>14} {'V_std':>10} {'n_spots':>9} {'interior_MI':>12} {'boundary_MI':>12} {'background_MI':>14}")
    for name, r in [("partial(0.90)", result_partial), ("full(1.00)", result_full)]:
        i = f"{r['interior_mi']:.4f}" if r['interior_mi'] is not None else "N/A"
        b = f"{r['boundary_mi']:.4f}" if r['boundary_mi'] is not None else "N/A"
        bg = f"{r['background_mi']:.4f}" if r['background_mi'] is not None else "N/A"
        print(f"{name:>14} {r['V_std']:>10.5f} {r['n_spots']:>9} {i:>12} {b:>12} {bg:>14}")

    if result_partial['interior_mi'] is not None and result_partial['boundary_mi'] is not None:
        print(f"\nPartial-dissipation Interior - Boundary gap: "
              f"{result_partial['interior_mi'] - result_partial['boundary_mi']:+.4f}")
        print("(positive gap in the same direction as the original Axiom 1 result would confirm")
        print(" causal insulation holds throughout the Turing-unstable regime, not just at full strength)")
