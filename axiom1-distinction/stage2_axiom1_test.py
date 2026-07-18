"""
STAGE 2: THE ACTUAL AXIOM 1 TEST.

Using the now-validated Gray-Scott implementation (confirmed against
documented spot-forming behavior with a seeded init in stage 1), run
from GENUINELY UNIFORM initial conditions -- U=1, V=0 everywhere, plus
only tiny random noise. No hand-placed patch, no external design.

The question: does structure emerge anyway?

This is the real test of Axiom 1 (Distinction): can undifferentiated
potential spontaneously partition itself into A-vs-not-A regions,
without an external designer placing anything?
"""

import numpy as np
from stage1_grayscott import gray_scott_step, uniform_init, KNOWN_REGIMES

if __name__ == "__main__":
    rng = np.random.default_rng(123)  # different seed from stage 1's sanity check
    N = 100
    STEPS = 8000

    print("AXIOM 1 TEST: genuinely uniform initial condition (U=1, V=0 + tiny noise)")
    print("NO hand-placed seed patch. NO external design.\n")

    U, V = uniform_init(N, N, rng, noise_scale=0.01)
    params = KNOWN_REGIMES["spots"]

    print(f"Initial condition check: U mean={U.mean():.4f} std={U.std():.5f}, "
          f"V mean={V.mean():.4f} std={V.std():.5f}")
    print("(should be ~1.0 and ~0.0 respectively, with std ~ noise_scale=0.01)\n")

    v_std_trace = []
    v_mean_trace = []

    for step in range(STEPS):
        U, V = gray_scott_step(U, V, **params)
        if step % 500 == 0:
            v_std_trace.append((step, V.std()))
            v_mean_trace.append((step, V.mean()))
            print(f"  step {step}: V -- min={V.min():.5f} max={V.max():.5f} "
                  f"mean={V.mean():.6f} std={V.std():.5f}")

    print(f"\nFinal V field: min={V.min():.5f} max={V.max():.5f} "
          f"mean={V.mean():.5f} std={V.std():.5f}")

    print("\n" + "="*60)
    print("VERDICT")
    print("="*60)
    initial_std = 0.01
    final_std = V.std()
    if final_std > initial_std * 3 and V.mean() > 0.001:
        print(f"STRUCTURE EMERGED: V std grew from ~{initial_std} (pure noise) to "
              f"{final_std:.5f} ({final_std/initial_std:.1f}x), with no external seed.")
        print("This supports Axiom 1: distinction (A vs not-A) can arise from")
        print("undifferentiated potential via local dynamics alone.")
    else:
        print(f"NO SUSTAINED STRUCTURE: V std stayed near noise level "
              f"({final_std:.5f} vs initial {initial_std}).")
        print("The uniform state did not spontaneously break symmetry under")
        print("these parameters -- Axiom 1 not supported by this run.")

    # save final state for visual inspection if needed
    np.save("axiom1_final_V.npy", V)
    np.save("axiom1_final_U.npy", U)
    print("\nSaved final U/V fields to axiom1_final_U.npy / axiom1_final_V.npy")
