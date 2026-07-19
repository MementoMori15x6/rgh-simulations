"""
STAGE 5 (FINAL CALIBRATION): the properly-calibrated local-signature
triage test whose results are quoted in the findings document.

Earlier calibration attempts either used too small a choice set (damage
rate 0.01/0.01, mean ~2 damaged cells/event -- ambiguous at n=15) or
overshot into a floor effect (0.04/0.04, mean ~10 damaged cells/event --
100% extinction regardless of repair strategy, uninformative). This
uses the calibration that actually worked: damage=0.02/0.02 (mean ~3
damaged cells/event), repair budget capped at 2 (a real, non-trivial
triage decision), n=50 trials per condition for adequate statistical
power.

Result (see README.md for full statistical analysis):
  none:     0/50  (0%)
  random:  33/50 (66%)
  smart:   32/50 (64%)
  shuffled: 28/50 (56%)
None of the pairwise differences among random/smart/shuffled reach
statistical significance (all z < 1.1).
"""

import sys
sys.path.insert(0, '.')
import statistics
import stage2_damage_repair as s2
from stage1_salvageability_memory import build_salvageability_memory
from stage4_triage import run_trial

# the calibration that actually produced a non-floor, non-ceiling,
# informative result -- see README.md section 3.3 for how this was found
s2.STRUCTURAL_DAMAGE_RATE = 0.02
s2.ENERGY_DRAIN_RATE = 0.02

REPAIR_BUDGET = 2
N_TRIALS = 50


def two_prop_z(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = (p_pool * (1 - p_pool) * (1 / n1 + 1 / n2)) ** 0.5
    z = (p1 - p2) / se if se > 0 else float('inf')
    return p1, p2, z


if __name__ == "__main__":
    print("Building salvageability memory (20 seeds)...")
    memory, total = build_salvageability_memory(n_seeds=20)
    print(f"  {len(memory)} signatures")

    shuffle_map, corr = s2.build_shuffle_map(memory, seed=0)
    print(f"  shuffle correlation={corr:.4f}\n")

    modes = ['none', 'random', 'smart', 'shuffled']
    results = {m: [] for m in modes}

    print(f"Running {N_TRIALS} trials per condition, damage=0.02/0.02, budget={REPAIR_BUDGET}...")
    for seed in range(N_TRIALS):
        for mode in modes:
            r = run_trial(mode, seed, memory, shuffle_map, budget=REPAIR_BUDGET)
            results[mode].append(r)
        if seed % 10 == 0:
            print(f"  seed {seed} done")

    print("\n" + "=" * 70)
    print(f"RESULTS (n={N_TRIALS}, damage=0.02/0.02, budget={REPAIR_BUDGET})")
    print("=" * 70)
    counts = {}
    for mode in modes:
        survived = [r['survived'] for r in results[mode]]
        n_survived = sum(survived)
        counts[mode] = n_survived
        final_live = [r['final_live'] for r in results[mode] if r['survived']]
        mean_live = statistics.mean(final_live) if final_live else 0
        print(f"{mode:>10}: survived {n_survived}/{N_TRIALS} ({100*n_survived/N_TRIALS:.0f}%), mean_live={mean_live:.1f}")

    print("\nStatistical comparisons (two-proportion z-test):")
    for name, m1, m2 in [('smart vs shuffled', 'smart', 'shuffled'),
                          ('smart vs random', 'smart', 'random'),
                          ('random vs shuffled', 'random', 'shuffled')]:
        p1, p2, z = two_prop_z(counts[m1], N_TRIALS, counts[m2], N_TRIALS)
        print(f"  {name}: {p1:.2f} vs {p2:.2f}, z={z:.3f}")
