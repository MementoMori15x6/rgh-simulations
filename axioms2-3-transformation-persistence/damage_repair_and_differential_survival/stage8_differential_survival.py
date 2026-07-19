"""
STAGE 8: pure differential-survival test.

No filter. No repair. No invented damage. Just the validated energy-CA
substrate (T + real metabolic cost + real energy dynamics) running on
its own, exactly as it would with no P mechanism of any kind.

The question: does the population's STRUCTURAL COMPOSITION drift over
time toward high-persistence configurations (as independently measured
by the component-size salvageability memory, built in stage6) purely
through ordinary attrition -- fragile structures dying under T's own
dynamics, robust ones (blocks, gliders) simply lasting longer -- with
NOTHING acting as an explicit selector?

This directly tests the reframe: persistence as an emergent STATISTIC
of running T over time, not as a discrete operator P that does
something at each step.

METHODOLOGICAL CARE: the component-size memory used to SCORE the
population here was built from seeds 0-19 (see stage6). This test uses
HELD-OUT seeds (100+) that were never used to build that memory, so the
confidence score is a genuinely independent measure of each trajectory,
not circular with what we're testing.
"""

import numpy as np
import statistics
from stage1_salvageability_memory import (
    gol_neighbor_count, N, BACKGROUND_INFLOW, BACKGROUND_DECAY,
    BIRTH_ENERGY_FRACTION, METABOLIC_COST, energy_step
)
from stage6_component_memory import build_component_memory, component_size_grid, bucket_size

SOUP_DENSITY = 0.25
MAX_STEPS = 2000
RECORD_INTERVAL = 50
HELD_OUT_SEEDS = list(range(100, 115))  # disjoint from memory-building seeds 0-19


def mean_population_confidence(life, memory):
    """
    For every currently-live cell, look up its component size's
    historical persistence confidence (from the independently-built
    memory), and return the population-weighted mean. This is the
    key metric: does this rise over time with NO explicit filter?
    """
    if life.sum() == 0:
        return None
    comp_grid = component_size_grid(life)
    rs, cs = np.where(life == 1)
    confs = []
    for r, c in zip(rs.tolist(), cs.tolist()):
        size = bucket_size(int(comp_grid[r, c]))
        d = memory.get(size)
        if d is not None and (d[0] + d[1]) > 0:
            confs.append(d[0] / (d[0] + d[1]))
    return statistics.mean(confs) if confs else None


def run_differential_survival_trial(seed, memory, max_steps=MAX_STEPS):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.full((N, N), 1.0)

    trace = []
    for step in range(max_steps):
        if step % RECORD_INTERVAL == 0:
            live_count = int(life.sum())
            mean_conf = mean_population_confidence(life, memory)
            trace.append({'step': step, 'live_count': live_count, 'mean_conf': mean_conf})

        life, energy = energy_step(life, energy)
        if life.sum() == 0:
            trace.append({'step': step + 1, 'live_count': 0, 'mean_conf': None})
            break

    return trace


if __name__ == "__main__":
    print("Building component-size memory from seeds 0-19 (as before)...")
    memory, total = build_component_memory(n_seeds=20)
    print(f"  {len(memory)} buckets\n")

    print(f"Running differential-survival trajectories on HELD-OUT seeds {HELD_OUT_SEEDS[0]}-{HELD_OUT_SEEDS[-1]}...")
    all_traces = {}
    for seed in HELD_OUT_SEEDS:
        trace = run_differential_survival_trial(seed, memory)
        all_traces[seed] = trace

    print("\n" + "=" * 80)
    print("MEAN POPULATION CONFIDENCE OVER TIME (averaged across held-out seeds)")
    print("(rising trend = differential survival naturally increases persistence-quality,")
    print(" with ZERO explicit filter or repair)")
    print("=" * 80)

    # align by recorded step (RECORD_INTERVAL), average across seeds where data exists
    max_recorded_step = max(t['step'] for trace in all_traces.values() for t in trace if t['step'] % RECORD_INTERVAL == 0)
    for target_step in range(0, max_recorded_step + 1, RECORD_INTERVAL):
        confs = []
        live_counts = []
        n_seeds_alive = 0
        for seed, trace in all_traces.items():
            matching = [t for t in trace if t['step'] == target_step]
            if matching and matching[0]['mean_conf'] is not None:
                confs.append(matching[0]['mean_conf'])
                live_counts.append(matching[0]['live_count'])
                n_seeds_alive += 1
        if confs:
            print(f"  step {target_step:>5}: mean_conf={statistics.mean(confs):.4f} "
                  f"(n_seeds_alive={n_seeds_alive}/{len(HELD_OUT_SEEDS)}, "
                  f"mean_live_count={statistics.mean(live_counts):.1f})")
