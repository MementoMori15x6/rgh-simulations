"""
STAGE 5: long-run trait drift (Claim 2, first test).

The established Level 1 population (contribution rate=0.03, confirmed
via ablation to have real functional interdependency) is run for a much
longer duration than the original 1500-step equilibrium window, tracking
mean population trait throughout.

The trait mechanism already supports a "free-rider" arising naturally,
with no special mechanism required: any cell whose trait mutates toward
0 contributes almost nothing to its neighbors while still potentially
benefiting from ITS neighbors' contributions. This is the most direct,
least assumption-laden test of Claim 2 (collective organization is
exploitable from within): does selection discover and favor this
free-riding strategy over a long run, eroding the mean trait toward
zero, or does the population resist this erosion?

  - Trait decaying toward 0 over the long run = evidence FOR Claim 2:
    the collective structure is vulnerable to internal erosion by
    non-contributing sub-forms (the hypercycle-parasite pattern).
  - Trait remaining stable (or rising) = evidence AGAINST this specific
    vulnerability for this mechanism -- worth reporting honestly either way.
"""

import numpy as np
import statistics
from stage3_contribution_mechanism import step_with_contribution, CONTRIBUTION_RATE
from stage1_energy_baseline import N
from stage1b_robustness_check import random_soup_seed

LONG_RUN_STEPS = 8000
RECORD_INTERVAL = 200
N_SEEDS = 8
CONFIRMED_RATE = 0.03  # the validated sweet-spot rate from Stage 4 -- do NOT rely on
                       # stage3's module-level CONTRIBUTION_RATE default (0.05), which
                       # was the original pre-sweep guess, not the confirmed value.
                       # This was a real bug caught before trusting the first run of
                       # this script: it silently ran at rate=0.05 instead of 0.03.


def run_long_trial(seed, rate=CONFIRMED_RATE, steps=LONG_RUN_STEPS):
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.25, rng)
    trait = rng.random((N, N))

    trace = []
    for step in range(steps):
        if step % RECORD_INTERVAL == 0:
            live_mask = life == 1
            mean_trait = trait[live_mask].mean() if live_mask.any() else None
            trace.append({'step': step, 'live_count': int(life.sum()), 'mean_trait': mean_trait})

        life, energy, trait = step_with_contribution(life, energy, trait, rng, contribution_rate=rate)
        if life.sum() == 0:
            trace.append({'step': step + 1, 'live_count': 0, 'mean_trait': None})
            break

    return trace


if __name__ == "__main__":
    print(f"Long-run trait drift test, rate={CONFIRMED_RATE}, {LONG_RUN_STEPS} steps, {N_SEEDS} seeds\n")

    all_traces = {}
    for seed in range(N_SEEDS):
        trace = run_long_trial(seed)
        all_traces[seed] = trace
        final = [t for t in trace if t['mean_trait'] is not None]
        status = "extinct" if trace[-1]['mean_trait'] is None else "survived"
        if final:
            print(f"seed {seed}: {status}, initial_trait~0.50, final_trait={final[-1]['mean_trait']:.4f}, "
                  f"final_live={final[-1]['live_count']}")
        else:
            print(f"seed {seed}: extinct before any valid trait reading")

    print(f"\n{'='*80}")
    print("MEAN TRAIT OVER TIME (averaged across surviving seeds)")
    print(f"{'='*80}")

    max_step = max(t['step'] for trace in all_traces.values() for t in trace if t['step'] % RECORD_INTERVAL == 0)
    for target_step in range(0, max_step + 1, RECORD_INTERVAL * 5):  # print every 5th recorded point
        traits, lives = [], []
        n_alive = 0
        for seed, trace in all_traces.items():
            matching = [t for t in trace if t['step'] == target_step]
            if matching and matching[0]['mean_trait'] is not None:
                traits.append(matching[0]['mean_trait'])
                lives.append(matching[0]['live_count'])
                n_alive += 1
        if traits:
            print(f"  step {target_step:>5}: mean_trait={statistics.mean(traits):.4f} "
                  f"(n_alive_seeds={n_alive}/{N_SEEDS}, mean_live_count={statistics.mean(lives):.1f})")
