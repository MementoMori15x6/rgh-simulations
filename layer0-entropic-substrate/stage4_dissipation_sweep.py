"""
STAGE 4: intermediate dissipation sweep.

Does structure collapse gradually as dissipation (F, k) is scaled down
from full strength toward zero, or is there a sharp threshold -- the
same kind of question asked of the noise-amplitude sweep in the
original Axiom 1 work?

Scales F and k together (preserving their ratio, since the ratio F:k
determines which Gray-Scott pattern regime you're in -- scaling them
together moves toward/away from equilibrium without changing regime
identity).
"""

import numpy as np
import statistics
from stage1_grayscott import gray_scott_step
from stage4_correlated_noise import correlated_noise_v, init_with_v_noise

N = 100
STEPS = 3000
Du, Dv = 0.16, 0.08
IGNITE_AMPLITUDE = 0.10
CORRELATION_LENGTH = 1.0
F_FULL, K_FULL = 0.035, 0.065
N_SEEDS = 8


def run_condition(scale, seed, steps=STEPS):
    F, k = F_FULL * scale, K_FULL * scale
    rng = np.random.default_rng(seed)
    v_field = correlated_noise_v(N, N, rng, amplitude=IGNITE_AMPLITUDE, correlation_length=CORRELATION_LENGTH)
    U, V = init_with_v_noise(N, N, v_field, rng=rng)
    for step in range(steps):
        U, V = gray_scott_step(U, V, Du, Dv, F, k)
    return float(V.std())


if __name__ == "__main__":
    scales = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

    print(f"Dissipation scale sweep (F,k scaled together, {N_SEEDS} seeds each)\n")
    print(f"{'scale':>8} {'F':>8} {'k':>8} {'mean_V_std':>12} {'std_across_seeds':>16}")

    for scale in scales:
        stds = [run_condition(scale, seed) for seed in range(N_SEEDS)]
        mean_std = statistics.mean(stds)
        seed_std = statistics.pstdev(stds)
        print(f"{scale:>8.2f} {F_FULL*scale:>8.4f} {K_FULL*scale:>8.4f} {mean_std:>12.5f} {seed_std:>16.5f}")
