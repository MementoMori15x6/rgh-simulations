"""
LAYER 0 TEST: does causal-insulation structure formation require genuine
non-equilibrium (dissipative) flux, or does mere fluctuation suffice?

Three conditions, same ignition protocol (correlated noise, amplitude=0.10,
correlation_length=1.0 -- the strongest-igniting condition validated in
the original Axiom 1 causal-insulation test):

  A -- DISSIPATIVE: F=0.035, k=0.065 (the validated "spots" regime).
       Real non-equilibrium throughput: the feed term F(1-U) and kill
       term (F+k)V continuously drive the system away from equilibrium.
       This is the substrate the original Axiom 1 result was confirmed on.

  B -- NON-DISSIPATIVE CONTROL: F=0, k=0. Same diffusion coefficients,
       same nonlinear reaction term (U*V^2), same correlated-noise
       ignition -- but with feed and kill removed, the system is CLOSED,
       not open. Per dissipative-structure theory (Prigogine), a closed
       system should relax toward a uniform/quiescent state rather than
       sustain structure. This is the actual falsification test: if B
       sustains structure just as well as A, mere fluctuation is
       sufficient and Layer 0 (entropic flux as a load-bearing
       requirement) fails. If B collapses toward C, Layer 0 gains
       support.

  C -- PURE NOISE BASELINE: no dynamics at all, just the initial
       correlated-noise field, for reference (the "nothing has happened
       yet" comparison point).

STAGE 1: basic structure-formation check across all three conditions,
before attempting the harder causal-insulation MI test. If B collapses
to uniform/trivial, there's no structure to run an MI test on in the
first place -- itself a real, informative result.
"""

import numpy as np
from stage1_grayscott import gray_scott_step, uniform_init
from stage4_correlated_noise import correlated_noise_v, init_with_v_noise

N = 100
STEPS = 3000
Du, Dv = 0.16, 0.08  # diffusion coefficients held constant across A and B
IGNITE_AMPLITUDE = 0.10
CORRELATION_LENGTH = 1.0


def run_condition(F, k, seed=123, steps=STEPS):
    rng = np.random.default_rng(seed)
    v_field = correlated_noise_v(N, N, rng, amplitude=IGNITE_AMPLITUDE, correlation_length=CORRELATION_LENGTH)
    U, V = init_with_v_noise(N, N, v_field, rng=rng)

    v_std_trace = []
    for step in range(steps):
        U, V = gray_scott_step(U, V, Du, Dv, F, k)
        if step % 500 == 0:
            v_std_trace.append((step, float(V.std()), float(V.mean())))

    return U, V, v_std_trace


if __name__ == "__main__":
    print("STAGE 1: basic structure-formation check\n")

    print("Condition A (DISSIPATIVE, F=0.035, k=0.065):")
    U_a, V_a, trace_a = run_condition(F=0.035, k=0.065)
    for step, std, mean in trace_a:
        print(f"  step {step:>5}: V std={std:.5f} mean={mean:.5f}")
    print(f"  FINAL: V std={V_a.std():.5f} mean={V_a.mean():.5f}\n")

    print("Condition B (NON-DISSIPATIVE CONTROL, F=0, k=0):")
    U_b, V_b, trace_b = run_condition(F=0.0, k=0.0)
    for step, std, mean in trace_b:
        print(f"  step {step:>5}: V std={std:.5f} mean={mean:.5f}")
    print(f"  FINAL: V std={V_b.std():.5f} mean={V_b.mean():.5f}\n")

    print("Condition C (PURE NOISE BASELINE, no dynamics):")
    rng = np.random.default_rng(123)
    v_field_c = correlated_noise_v(N, N, rng, amplitude=IGNITE_AMPLITUDE, correlation_length=CORRELATION_LENGTH)
    print(f"  Initial V std={v_field_c.std():.5f} mean={v_field_c.mean():.5f}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"A (dissipative)     final V std: {V_a.std():.5f}")
    print(f"B (non-dissipative) final V std: {V_b.std():.5f}")
    print(f"C (pure noise)      initial V std: {v_field_c.std():.5f}")
    print("\nIf B's std collapses toward C's (much lower than A's), that")
    print("supports Layer 0 -- structure needs real dissipative flux, not")
    print("just any fluctuation. If B ~ A, Layer 0 is falsified.")
