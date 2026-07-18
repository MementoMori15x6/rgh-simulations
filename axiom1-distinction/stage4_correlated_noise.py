"""
STAGE 4: spatially-correlated noise on V vs white noise on V.

Rationale: real microscopic fluctuations aren't perfectly decorrelated
cell-to-cell -- diffusion itself, and any physical granularity below our
grid resolution, would produce some spatial correlation length. If V's
noise having spatial correlation (rather than being independent per
cell) lowers the amplitude needed to ignite the reaction, that's a
meaningful finding: it would mean "physically plausible" noise (which
is never perfectly white in a real continuous medium) ignites more
easily than the idealized white-noise case, at the same nominal
amplitude.

Method: generate correlated noise by taking white noise and applying a
Gaussian spatial filter (blur) with a given correlation length, then
RESCALE the result to have the same standard deviation as an equivalent
white-noise field. This isolates the effect of CORRELATION STRUCTURE
from the effect of AMPLITUDE -- both noise fields have identical std,
so any ignition difference is attributable to spatial correlation, not
just "more noise."
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from stage1_grayscott import gray_scott_step, KNOWN_REGIMES

def white_noise_v(n_rows, n_cols, rng, amplitude):
    return rng.normal(0, amplitude, (n_rows, n_cols))

def correlated_noise_v(n_rows, n_cols, rng, amplitude, correlation_length):
    """
    Generate spatially correlated noise with a given correlation length,
    then rescale to match `amplitude` as its standard deviation -- so
    it's directly comparable to white_noise_v at the same amplitude,
    differing ONLY in spatial correlation structure.
    """
    raw = rng.normal(0, 1, (n_rows, n_cols))
    # toroidal-safe blur: pad with wrap mode so correlation doesn't leak
    # incorrectly across the periodic boundary
    blurred = gaussian_filter(raw, sigma=correlation_length, mode='wrap')
    # rescale to target amplitude (std)
    current_std = blurred.std()
    if current_std > 0:
        blurred = blurred * (amplitude / current_std)
    return blurred

def init_with_v_noise(n_rows, n_cols, v_noise_field, u_noise_scale=0.01, rng=None):
    U = np.ones((n_rows, n_cols)) + (rng.normal(0, u_noise_scale, (n_rows, n_cols)) if rng is not None else 0)
    V = np.zeros((n_rows, n_cols)) + v_noise_field
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    return U, V


if __name__ == "__main__":
    N = 100
    STEPS = 3000
    params = KNOWN_REGIMES["spots"]

    print("Comparing WHITE noise vs SPATIALLY-CORRELATED noise on V,")
    print("at MATCHED standard deviation (amplitude), varying correlation length.\n")

    # test at and below the white-noise ignition threshold found earlier
    # (0.10 failed, 0.15 ignited) -- focus on whether correlation helps
    # BELOW the white-noise threshold
    amplitudes = [0.08, 0.10, 0.12]
    correlation_lengths = [0.5, 1.0, 2.0, 4.0, 8.0]

    print(f"{'amplitude':>10} {'corr_len':>10} {'final_mean':>12} {'final_std':>12} {'ignited?':>10}")
    print("-" * 58)

    for amp in amplitudes:
        # white noise baseline at this amplitude
        rng = np.random.default_rng(123)
        v_field = white_noise_v(N, N, rng, amplitude=amp)
        U, V = init_with_v_noise(N, N, v_field, rng=rng)
        for step in range(STEPS):
            U, V = gray_scott_step(U, V, **params)
        ignited = V.std() > 0.03
        print(f"{amp:>10.2f} {'white':>10} {V.mean():>12.5f} {V.std():>12.5f} {str(ignited):>10}")

        for corr_len in correlation_lengths:
            rng = np.random.default_rng(123)
            v_field = correlated_noise_v(N, N, rng, amplitude=amp, correlation_length=corr_len)
            U, V = init_with_v_noise(N, N, v_field, rng=rng)
            for step in range(STEPS):
                U, V = gray_scott_step(U, V, **params)
            ignited = V.std() > 0.03
            print(f"{amp:>10.2f} {corr_len:>10.1f} {V.mean():>12.5f} {V.std():>12.5f} {str(ignited):>10}")
        print()
