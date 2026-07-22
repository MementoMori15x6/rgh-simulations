"""
STAGE 4: ablation test on the contribution/helper mechanism.

Same validated methodology as Stage 2 (specific vs. clustered_random,
NOT scattered random -- scattered comparison was shown to be confounded
by spatial-clustering pattern alone). Here "specific" removal targets
the HIGH-TRAIT individuals (best helpers/contributors), since the
hypothesis under test is that helpers are doing real, hard-to-replace
structural work -- their removal should hurt disproportionately if a
genuine Level 1 (collective, mutually-dependent) organization has
formed.
"""

import numpy as np
import statistics
from stage3_contribution_mechanism import step_with_contribution, CONTRIBUTION_RATE
from stage1_energy_baseline import N
from stage1b_robustness_check import random_soup_seed

EQUILIBRIUM_STEPS = 1500
POST_ABLATION_STEPS = 500
REMOVAL_FRACTION = 0.20
N_SEEDS = 15


def run_to_equilibrium(seed):
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.25, rng)
    trait = rng.random((N, N))
    for step in range(EQUILIBRIUM_STEPS):
        life, energy, trait = step_with_contribution(life, energy, trait, rng)
        if life.sum() == 0:
            return None
    return life, energy, trait, rng


def apply_ablation(life, energy, trait, mode, rng):
    """mode: 'specific' (remove HIGHEST-trait band -- the best helpers)
    or 'clustered_random' (spatially-matched, trait-independent)."""
    live_rs, live_cs = np.where(life == 1)
    n_live = len(live_rs)
    k = int(round(REMOVAL_FRACTION * n_live))
    if k == 0:
        return life.copy(), energy.copy()

    life = life.copy()
    energy = energy.copy()

    if mode == 'specific':
        live_traits = trait[live_rs, live_cs]
        order = np.argsort(-live_traits)  # HIGHEST trait first (best helpers)
        remove_idx = order[:k]
    else:  # clustered_random
        n_grid = life.shape[0]
        center_idx = rng.integers(0, n_live)
        center_r, center_c = live_rs[center_idx], live_cs[center_idx]
        dr = np.minimum(np.abs(live_rs - center_r), n_grid - np.abs(live_rs - center_r))
        dc = np.minimum(np.abs(live_cs - center_c), n_grid - np.abs(live_cs - center_c))
        dist = dr**2 + dc**2
        remove_idx = np.argsort(dist)[:k]

    life[live_rs[remove_idx], live_cs[remove_idx]] = 0
    energy[live_rs[remove_idx], live_cs[remove_idx]] = 0.0

    return life, energy


def run_post_ablation(life, energy, trait, rng, steps=POST_ABLATION_STEPS):
    for step in range(steps):
        life, energy, trait = step_with_contribution(life, energy, trait, rng)
        if life.sum() == 0:
            return 0
    return int(life.sum())


if __name__ == "__main__":
    print(f"Ablation test on CONTRIBUTION mechanism (rate={CONTRIBUTION_RATE}), {N_SEEDS} seeds")
    print(f"'specific' = remove HIGHEST-trait (best helper) individuals\n")
    print(f"{'seed':>5} {'pre':>6} {'k':>5} {'specific':>10} {'clustered_rand':>15}")

    specific_results, clustered_results = [], []
    for seed in range(N_SEEDS):
        eq = run_to_equilibrium(seed)
        if eq is None:
            print(f"{seed:>5}  EXTINCT before ablation, skipped")
            continue
        life0, energy0, trait0, rng = eq
        pre_count = int(life0.sum())
        k = int(round(REMOVAL_FRACTION * pre_count))

        life_s, energy_s = apply_ablation(life0, energy0, trait0, 'specific', rng)
        post_specific = run_post_ablation(life_s.copy(), energy_s.copy(), trait0.copy(), rng)

        rng3 = np.random.default_rng(seed + 190000)
        life_c, energy_c = apply_ablation(life0, energy0, trait0, 'clustered_random', rng3)
        post_clustered = run_post_ablation(life_c.copy(), energy_c.copy(), trait0.copy(), rng3)

        specific_results.append(post_specific)
        clustered_results.append(post_clustered)
        print(f"{seed:>5} {pre_count:>6} {k:>5} {post_specific:>10} {post_clustered:>15}")

    print(f"\n{'='*60}")
    print(f"Mean post-ablation: specific(helpers removed)={statistics.mean(specific_results):.1f}, "
          f"clustered_random={statistics.mean(clustered_results):.1f}")

    diffs = [s - c for s, c in zip(specific_results, clustered_results)]
    d_mean = statistics.mean(diffs)
    d_std = statistics.pstdev(diffs)
    t_stat = d_mean / (d_std / (len(diffs) ** 0.5)) if d_std > 0 else float('inf')
    print(f"Paired difference (specific - clustered_random): {d_mean:+.2f} (std {d_std:.2f})")
    print(f"Paired t-statistic: {t_stat:.3f}")
    print("\nNegative and significant = removing helpers hurts MORE than removing an equally-")
    print("clustered random group -- real functional interdependency (Level 1 signature).")
    print("Near zero / not significant = still functionally interchangeable (Level 0),")
    print("despite the contribution mechanism being present.")
