"""
STAGE 3: Multiplicative (concentration-scaled) noise, vs. the additive
noise tested in stage 2.

Physical motivation, stated honestly: real chemical concentration
fluctuations from molecular shot noise scale with sqrt(N) where N is
particle count -- i.e. relative fluctuation size shrinks as concentration
grows, and absolute fluctuation size shrinks as concentration shrinks
toward zero. Since our V field starts at exactly 0, pure multiplicative
noise on V (noise proportional to V) would be identically zero everywhere
V=0 -- it could never ignite anything from a state where V=0 everywhere.
This is a real physical/mathematical fact, not a technicality to route
around: any noise model that is purely multiplicative on a field sitting
at an exact zero cannot break that field's symmetry by itself.

So the honest, well-posed version of "multiplicative noise" here is:
  U_noise = U * epsilon_U   (relative fluctuation in U, which starts at 1 --
                              this one is well-defined and non-trivial)
  V_noise = additive noise only, since V starts at 0 and needs SOME
            nonzero seed to have anything to multiply
This is not cheating -- it reflects a real asymmetry in the physical
setup (U is the abundant background field, V is the trace species that
must be nucleated from nothing). We test whether making U's fluctuations
concentration-scaled (rather than a fixed additive amount) changes the
ignition threshold, while keeping V's necessarily-additive seed as small
as we can while still testing multiple amplitudes.
"""

import numpy as np
from stage1_grayscott import gray_scott_step, KNOWN_REGIMES

def multiplicative_noise_init(n_rows, n_cols, rng, u_rel_noise, v_abs_noise):
    """
    U: multiplicative/relative noise around the uniform base state U=1.
       U = 1 * (1 + eps), eps ~ N(0, u_rel_noise)
    V: additive noise around V=0 (necessarily -- see module docstring).
       V = 0 + eps, eps ~ N(0, v_abs_noise)
    """
    U = 1.0 * (1.0 + rng.normal(0, u_rel_noise, (n_rows, n_cols)))
    V = 0.0 + rng.normal(0, v_abs_noise, (n_rows, n_cols))
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    return U, V

def additive_noise_init(n_rows, n_cols, rng, noise_scale):
    """Same additive-on-both-fields noise as stage 2, for direct comparison."""
    U = np.ones((n_rows, n_cols)) + rng.normal(0, noise_scale, (n_rows, n_cols))
    V = np.zeros((n_rows, n_cols)) + rng.normal(0, noise_scale, (n_rows, n_cols))
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    return U, V


if __name__ == "__main__":
    N = 100
    STEPS = 3000
    params = KNOWN_REGIMES["spots"]

    print("COMPARISON: additive noise (stage 2 baseline) vs multiplicative-on-U noise")
    print("Same V-seed amplitude in both cases, for fair comparison.\n")

    v_seed_amplitudes = [0.10, 0.15, 0.20]
    u_rel_amplitudes = [0.01, 0.05, 0.10, 0.15, 0.20]

    print(f"{'V_amp':>8} {'U_mode':>20} {'U_param':>8} {'final_mean':>12} {'final_std':>12} {'ignited?':>10}")
    print("-" * 76)

    for v_amp in v_seed_amplitudes:
        # baseline: additive noise on U at the SAME scale as V (as in stage 2)
        rng = np.random.default_rng(123)
        U, V = additive_noise_init(N, N, rng, noise_scale=v_amp)
        for step in range(STEPS):
            U, V = gray_scott_step(U, V, **params)
        ignited = V.std() > 3 * v_amp * 0.1  # heuristic: std well above trivial noise floor
        print(f"{v_amp:>8.2f} {'additive (baseline)':>20} {v_amp:>8.2f} "
              f"{V.mean():>12.5f} {V.std():>12.5f} {str(ignited):>10}")

        # multiplicative-on-U variants, same V seed amplitude, sweep U's relative noise
        for u_amp in u_rel_amplitudes:
            rng = np.random.default_rng(123)
            U, V = multiplicative_noise_init(N, N, rng, u_rel_noise=u_amp, v_abs_noise=v_amp)
            for step in range(STEPS):
                U, V = gray_scott_step(U, V, **params)
            ignited = V.std() > 3 * v_amp * 0.1
            print(f"{v_amp:>8.2f} {'multiplicative-on-U':>20} {u_amp:>8.2f} "
                  f"{V.mean():>12.5f} {V.std():>12.5f} {str(ignited):>10}")
        print()
