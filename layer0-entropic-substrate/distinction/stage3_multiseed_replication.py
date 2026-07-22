"""
STAGE 3: multi-seed replication.

The original Layer 0 test (Stage 1) ran a single seed per condition.
This replicates the core structural finding -- Condition A (dissipative)
sustains/grows structure, Condition B (non-dissipative) collapses it --
across multiple independent seeds, using ONLY the structural variance
metric (V std), since that metric is trustworthy (unlike the MI test,
which was shown not to transfer meaningfully to Condition B's monotonic-
relaxation regime).
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
N_SEEDS = 15


def run_condition(F, k, seed, steps=STEPS):
    rng = np.random.default_rng(seed)
    v_field = correlated_noise_v(N, N, rng, amplitude=IGNITE_AMPLITUDE, correlation_length=CORRELATION_LENGTH)
    U, V = init_with_v_noise(N, N, v_field, rng=rng)
    for step in range(steps):
        U, V = gray_scott_step(U, V, Du, Dv, F, k)
    return float(V.std()), float(V.mean())


if __name__ == "__main__":
    print(f"Replicating across {N_SEEDS} seeds...\n")

    a_stds, b_stds = [], []
    print(f"{'seed':>5} {'A_std':>10} {'A_mean':>10} {'B_std':>10} {'B_mean':>10}")
    for seed in range(N_SEEDS):
        a_std, a_mean = run_condition(F=0.035, k=0.065, seed=seed)
        b_std, b_mean = run_condition(F=0.0, k=0.0, seed=seed)
        a_stds.append(a_std)
        b_stds.append(b_std)
        print(f"{seed:>5} {a_std:>10.5f} {a_mean:>10.5f} {b_std:>10.5f} {b_mean:>10.5f}")

    print(f"\n{'='*60}")
    print(f"A (dissipative)     mean final V_std: {statistics.mean(a_stds):.5f} (std {statistics.pstdev(a_stds):.5f})")
    print(f"B (non-dissipative) mean final V_std: {statistics.mean(b_stds):.5f} (std {statistics.pstdev(b_stds):.5f})")

    diffs = [a - b for a, b in zip(a_stds, b_stds)]
    d_mean = statistics.mean(diffs)
    d_std = statistics.pstdev(diffs)
    t_stat = d_mean / (d_std / (len(diffs) ** 0.5)) if d_std > 0 else float('inf')
    print(f"\nPaired difference (A - B): {d_mean:+.5f} (std {d_std:.5f})")
    print(f"Paired t-statistic: {t_stat:.3f}")
    print(f"\nAll {N_SEEDS} seeds show A > B?", all(a > b for a, b in zip(a_stds, b_stds)))
