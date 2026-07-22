"""
STAGE 6 (interpretation-b test): does the noise ITSELF need to be
dissipation-sourced, or does any ongoing noise suffice as long as the
SYSTEM is thermodynamically open?

Every prior Layer 0 test used noise only as a ONE-TIME initial
perturbation, then let the system evolve deterministically. This test
introduces ONGOING noise injection during the run itself, on the SAME
open, dissipative system (F=0.035, k=0.065 -- already confirmed to
support structure), comparing:

  C1 -- DISSIPATION-SOURCED: injected noise amplitude at each point
        scales with the LOCAL reaction rate (U*V^2, the term actually
        being consumed/converted by the reaction) -- mimicking real
        molecular/thermal noise, which physically scales with reaction
        throughput (the same logic behind stochastic chemical kinetics).

  C2 -- DISSIPATION-INDEPENDENT: same total noise "budget" injected
        across the grid on average, but at a FIXED, spatially-uniform
        amplitude, unrelated to local reaction rate.

Both conditions keep the system open (F, k nonzero, unchanged from the
validated dissipative regime) -- this isolates NOISE SOURCE specifically,
not system openness, which was already tested and confirmed separately.

If C1 and C2 produce similar structure/causal insulation, that supports
"any noise suffices in an open system" (system openness is what matters,
not noise origin). If C1 clearly outperforms C2, that supports the
stronger claim that noise itself must be dissipation-sourced.
"""

import numpy as np
from stage1_grayscott import gray_scott_step, uniform_init
from stage4_correlated_noise import correlated_noise_v, init_with_v_noise

N = 100
Du, Dv = 0.16, 0.08
F, k = 0.035, 0.065   # the validated dissipative "spots" regime, held fixed throughout
STEPS = 3000
IGNITE_AMPLITUDE = 0.10   # initial ignition, same as prior tests, so structure has a real start
CORRELATION_LENGTH = 1.0
ONGOING_NOISE_BUDGET = 0.001  # per-step noise injection scale, calibration flagged


def inject_dissipation_sourced_noise(U, V, rng, budget=ONGOING_NOISE_BUDGET):
    """Noise amplitude at each cell scales with local reaction rate (U*V^2)."""
    reaction_rate = U * V * V
    # normalize so the average injected noise matches the target budget
    mean_rate = reaction_rate.mean()
    if mean_rate < 1e-12:
        scale = np.zeros_like(reaction_rate)
    else:
        scale = (reaction_rate / mean_rate) * budget
    noise = rng.normal(0, 1, V.shape) * scale
    return V + noise


def inject_dissipation_independent_noise(U, V, rng, budget=ONGOING_NOISE_BUDGET):
    """Fixed, spatially-uniform noise amplitude, same average budget as the sourced version."""
    noise = rng.normal(0, budget, V.shape)
    return V + noise


def run_condition(noise_mode, seed=123, steps=STEPS):
    rng = np.random.default_rng(seed)
    v_field = correlated_noise_v(N, N, rng, amplitude=IGNITE_AMPLITUDE, correlation_length=CORRELATION_LENGTH)
    U, V = init_with_v_noise(N, N, v_field, rng=rng)

    v_std_trace = []
    for step in range(steps):
        U, V = gray_scott_step(U, V, Du, Dv, F, k)
        if noise_mode == 'sourced':
            V = inject_dissipation_sourced_noise(U, V, rng)
        elif noise_mode == 'independent':
            V = inject_dissipation_independent_noise(U, V, rng)
        # noise_mode == 'none' -> no ongoing injection (matches original Condition A)
        V = np.clip(V, 0, 1)
        if step % 500 == 0:
            v_std_trace.append((step, float(V.std())))

    return U, V, v_std_trace


if __name__ == "__main__":
    print("STAGE 6: noise-source control -- basic structure check first\n")

    for mode in ['none', 'sourced', 'independent']:
        print(f"Condition: ongoing noise = {mode}")
        U, V, trace = run_condition(mode)
        for step, std in trace:
            print(f"  step {step:>5}: V std={std:.5f}")
        print(f"  FINAL: V std={V.std():.5f} mean={V.mean():.5f}\n")
