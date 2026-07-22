"""
STAGE 1: Gray-Scott reaction-diffusion substrate.

Standard, well-documented model (Pearson 1993 and many since):
  dU/dt = Du * Laplacian(U) - U*V^2 + F*(1-U)
  dV/dt = Dv * Laplacian(V) + U*V^2 - (F+k)*V

U and V are two chemical concentration fields on a 2D grid. Du, Dv are
diffusion rates (U diffuses faster than V -- this asymmetry is what
makes Turing patterns possible at all). F (feed rate) and k (kill rate)
are the two parameters that determine which pattern regime you get
(spots, stripes, mazes, or nothing).

This is NOT a novel mechanism -- these exact parameter values and their
associated pattern types are well-documented in the Gray-Scott literature
(e.g. Pearson's 1993 Science paper cataloguing pattern regimes). We use
known-good parameter sets specifically so we can sanity-check our
implementation against documented behavior before trusting anything it
produces.

CRITICAL for Axiom 1: initial condition must be genuinely uniform plus
only TINY random noise -- no hand-drawn shapes, no external design. If
patterns emerge from this, that's the whole point: distinction arising
from an undifferentiated substrate, not from us placing anything.
"""

import numpy as np

def laplacian(Z):
    """Standard 5-point discrete Laplacian with toroidal wrap."""
    return (
        np.roll(Z, 1, axis=0) + np.roll(Z, -1, axis=0) +
        np.roll(Z, 1, axis=1) + np.roll(Z, -1, axis=1) -
        4 * Z
    )

def gray_scott_step(U, V, Du, Dv, F, k, dt=1.0):
    Lu = laplacian(U)
    Lv = laplacian(V)
    uvv = U * V * V
    U_next = U + dt * (Du * Lu - uvv + F * (1 - U))
    V_next = V + dt * (Dv * Lv + uvv - (F + k) * V)
    # clip to valid concentration range to avoid numerical blowup
    return np.clip(U_next, 0, 1), np.clip(V_next, 0, 1)

def uniform_init(n_rows, n_cols, rng, noise_scale=0.01):
    """
    Genuinely uniform base state (U=1, V=0 everywhere -- the standard
    Gray-Scott 'trivial' steady state) plus only tiny random noise.
    No shapes, no design, no external structure -- this is the
    'undifferentiated potential' condition Axiom 1 needs to start from.
    """
    U = np.ones((n_rows, n_cols)) + rng.normal(0, noise_scale, (n_rows, n_cols))
    V = np.zeros((n_rows, n_cols)) + rng.normal(0, noise_scale, (n_rows, n_cols))
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    return U, V

def small_seed_init(n_rows, n_cols, rng, noise_scale=0.01, seed_radius=16):
    """
    ALTERNATE init used ONLY for sanity-checking our implementation
    against documented Gray-Scott behavior: a small central seed patch,
    which is the standard way these systems are demonstrated in the
    literature. This IS externally designed -- it's a validation check,
    not the Axiom 1 test itself. We use it here only to confirm our
    equations/parameters produce the textbook result before trusting
    the uniform-noise version.

    NOTE: seed_radius=16 matches documented reference implementations.
    An earlier version of this file used radius=5, which was too small
    to sustain the reaction at this grid size/parameter set -- the
    reaction extinguished within ~150 steps regardless of dt. This was
    a bug in the sanity-check's seed size, not in the underlying
    equations or parameters, confirmed by testing against the
    documented radius.
    """
    U, V = uniform_init(n_rows, n_cols, rng, noise_scale)
    cy, cx = n_rows // 2, n_cols // 2
    r = seed_radius
    U[cy-r:cy+r, cx-r:cx+r] = 0.50
    V[cy-r:cy+r, cx-r:cx+r] = 0.25
    return U, V


# Well-documented Gray-Scott parameter regimes (Pearson 1993 and
# standard references). Used here ONLY to validate our implementation
# reproduces known pattern types -- not invented by us.
KNOWN_REGIMES = {
    "spots":   dict(Du=0.16, Dv=0.08, F=0.035, k=0.065),
    "stripes": dict(Du=0.16, Dv=0.08, F=0.030, k=0.060),
    "mazes":   dict(Du=0.16, Dv=0.08, F=0.029, k=0.057),
}


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    N = 100
    STEPS = 6000  # extended -- growth was still ongoing at 4000 in the fixed version

    print("SANITY CHECK: seeded init (radius=16, matching reference), known 'spots' parameters")
    print("(validates our equations/params against documented Gray-Scott behavior)\n")

    U, V = small_seed_init(N, N, rng)
    params = KNOWN_REGIMES["spots"]

    for step in range(STEPS):
        U, V = gray_scott_step(U, V, **params)
        if step % 1000 == 0:
            print(f"  step {step}: V field -- min={V.min():.4f} max={V.max():.4f} "
                  f"mean={V.mean():.4f} std={V.std():.4f}")

    print(f"\nFinal V field stats: min={V.min():.4f} max={V.max():.4f} "
          f"mean={V.mean():.4f} std={V.std():.4f}")

    print(f"\nIf this is a real 'spots' pattern, std should be well above the")
    print(f"initial noise_scale (0.01) and the pattern should be STABLE (not")
    print(f"decaying to zero) over the run -- confirms non-trivial, sustained structure.")

    if V.std() > 0.03 and V.mean() > 0.005:
        print("PASS: V field shows substantial, sustained structure.")
    else:
        print("WARNING: V field looks close to uniform or has decayed -- check parameters/steps.")
