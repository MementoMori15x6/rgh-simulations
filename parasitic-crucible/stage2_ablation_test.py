"""
STAGE 2: ablation test on the naive (inert-trait) baseline.

At equilibrium, remove a specific trait-band (lowest-trait individuals,
a fixed count K) vs. an equal-sized RANDOM subset of the live
population, then run forward and compare downstream harm.

Since the baseline's trait is functionally inert (Stage 1), this MUST
show no meaningful difference between the two removal types -- if it
did, that would mean our ablation methodology itself is biased, not
that real interdependency exists. This run validates the test before
we trust it on any real candidate mechanism.
"""

import numpy as np
import statistics
from stage1_naive_baseline import step_naive, N
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
        life, energy, trait = step_naive(life, energy, trait, rng)
        if life.sum() == 0:
            return None
    return life, energy, trait, rng


def apply_ablation(life, energy, trait, mode, rng):
    """mode: 'specific' (remove lowest-trait band), 'random' (scattered,
    uniformly random subset), or 'clustered_random' (spatially-clustered
    but trait-independent -- removes the K nearest live cells to a
    random starting point, matching specific-removal's spatial pattern
    without using trait at all). Returns modified (life, energy)."""
    live_rs, live_cs = np.where(life == 1)
    n_live = len(live_rs)
    k = int(round(REMOVAL_FRACTION * n_live))
    if k == 0:
        return life.copy(), energy.copy()

    life = life.copy()
    energy = energy.copy()

    if mode == 'specific':
        live_traits = trait[live_rs, live_cs]
        order = np.argsort(live_traits)
        remove_idx = order[:k]
    elif mode == 'clustered_random':
        n_grid = life.shape[0]
        center_idx = rng.integers(0, n_live)
        center_r, center_c = live_rs[center_idx], live_cs[center_idx]
        dr = np.minimum(np.abs(live_rs - center_r), n_grid - np.abs(live_rs - center_r))
        dc = np.minimum(np.abs(live_cs - center_c), n_grid - np.abs(live_cs - center_c))
        dist = dr**2 + dc**2
        remove_idx = np.argsort(dist)[:k]
    else:  # random (scattered)
        remove_idx = rng.choice(n_live, size=k, replace=False)

    life[live_rs[remove_idx], live_cs[remove_idx]] = 0
    energy[live_rs[remove_idx], live_cs[remove_idx]] = 0.0

    return life, energy


def run_post_ablation(life, energy, trait, rng, steps=POST_ABLATION_STEPS):
    for step in range(steps):
        life, energy, trait = step_naive(life, energy, trait, rng)
        if life.sum() == 0:
            return 0
    return int(life.sum())


if __name__ == "__main__":
    print(f"Ablation test on NAIVE baseline (inert trait), {N_SEEDS} seeds")
    print(f"Three conditions: specific (trait-band), scattered random, clustered random (spatial-matched)\n")
    print(f"{'seed':>5} {'pre':>6} {'k':>5} {'specific':>10} {'scattered':>11} {'clustered':>11}")

    specific_results, scattered_results, clustered_results = [], [], []
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

        rng2 = np.random.default_rng(seed + 90000)
        life_r, energy_r = apply_ablation(life0, energy0, trait0, 'random', rng2)
        post_scattered = run_post_ablation(life_r.copy(), energy_r.copy(), trait0.copy(), rng2)

        rng3 = np.random.default_rng(seed + 190000)
        life_c, energy_c = apply_ablation(life0, energy0, trait0, 'clustered_random', rng3)
        post_clustered = run_post_ablation(life_c.copy(), energy_c.copy(), trait0.copy(), rng3)

        specific_results.append(post_specific)
        scattered_results.append(post_scattered)
        clustered_results.append(post_clustered)
        print(f"{seed:>5} {pre_count:>6} {k:>5} {post_specific:>10} {post_scattered:>11} {post_clustered:>11}")

    print(f"\n{'='*70}")
    print(f"Mean post-ablation: specific={statistics.mean(specific_results):.1f}, "
          f"scattered_random={statistics.mean(scattered_results):.1f}, "
          f"clustered_random={statistics.mean(clustered_results):.1f}")

    def paired_stats(a, b, label):
        diffs = [x - y for x, y in zip(a, b)]
        d_mean = statistics.mean(diffs)
        d_std = statistics.pstdev(diffs)
        t_stat = d_mean / (d_std / (len(diffs) ** 0.5)) if d_std > 0 else float('inf')
        print(f"{label}: diff={d_mean:+.2f} (std {d_std:.2f}), paired-t={t_stat:.3f}")

    print()
    paired_stats(specific_results, scattered_results, "specific vs scattered_random")
    paired_stats(specific_results, clustered_results, "specific vs clustered_random  <-- the real test")
    paired_stats(clustered_results, scattered_results, "clustered_random vs scattered_random (spatial-pattern effect alone)")
    print("\nIf 'specific vs clustered_random' is near zero/not significant, the original")
    print("specific-vs-scattered gap was a spatial-clustering artifact, not real trait-based")
    print("interdependency -- exactly as Claim 1 (naive plateau) predicts for this baseline.")
