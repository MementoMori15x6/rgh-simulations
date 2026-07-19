"""
STAGE 9: LOOP CLOSURE TEST.

Control: pure T + attrition (no filter, no repair, no E/A) -- exactly
the stage8_differential_survival.py protocol, reused unchanged.

Treatment: the SAME substrate, SAME held-out seeds, but with the
validated memory-based exploit/mutualism mechanic (from the E/A work)
active from t=0. Per discussion: the exploit mechanic self-gates on
actual energy differences (uncapped_draw = exploit_rate * (energy_self
- energy_neighbor)), which are ~zero at t=0 since all cells start with
identical energy -- so there's no need to manually delay E/A's start;
it will be naturally near-inert until real inequality emerges from the
dynamics themselves.

Two metrics tracked at matching timesteps in both conditions:
  1. Mean population persistence-confidence (as in stage8) -- for
     continuity with the prior result.
  2. NEW: Shannon entropy of the component-size distribution (by
     component COUNT, not cell count) -- "richness of the zoo": how
     varied is the population's structural composition, using only the
     already-validated component_size_grid machinery. This does not
     distinguish different SHAPES of the same size (a known,
     deliberately-accepted limitation) -- it is a coarse but honest,
     already-buildable proxy for structural diversity.

METHODOLOGICAL CARE: component-size memory used for the confidence
metric was built from seeds 0-19 (stage6). This test uses the SAME
held-out seeds as stage8 (100-114), disjoint from the memory-building
seeds, preserving the no-circularity property of the original result.
"""

import numpy as np
import statistics
import math
from collections import Counter
from scipy import ndimage
from stage1_salvageability_memory import (
    N, energy_step, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION, METABOLIC_COST
)
from stage6_component_memory import build_component_memory, component_size_grid, bucket_size, LABEL_STRUCTURE
from ea_stage3_memory_switching import make_memory_step, fresh_memory_state

SOUP_DENSITY = 0.25
MAX_STEPS = 2000
RECORD_INTERVAL = 50
HELD_OUT_SEEDS = list(range(100, 115))  # same 15 seeds as stage8, disjoint from memory-building seeds 0-19


def mean_population_confidence(life, memory):
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


def structural_diversity_entropy(life):
    """
    Shannon entropy of the component-SIZE distribution, counted by
    number of DISTINCT COMPONENTS (not cells) at each bucketed size.
    Higher = more varied structural composition ('richer zoo').
    Returns None if no live cells.
    """
    if life.sum() == 0:
        return None
    labeled, n_components = ndimage.label(life, structure=LABEL_STRUCTURE)
    if n_components == 0:
        return None
    sizes = ndimage.sum(life, labeled, index=np.arange(1, n_components + 1))
    bucketed = [bucket_size(int(s)) for s in sizes]
    counts = Counter(bucketed)
    total = sum(counts.values())
    probs = [c / total for c in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    return entropy


def run_control_trial(seed, conf_memory, max_steps=MAX_STEPS):
    """Pure T + attrition -- identical protocol to stage8_differential_survival.py."""
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.full((N, N), 1.0)

    trace = []
    for step in range(max_steps):
        if step % RECORD_INTERVAL == 0:
            trace.append({
                'step': step,
                'live_count': int(life.sum()),
                'mean_conf': mean_population_confidence(life, conf_memory),
                'diversity_entropy': structural_diversity_entropy(life),
            })
        life, energy = energy_step(life, energy)
        if life.sum() == 0:
            trace.append({'step': step + 1, 'live_count': 0, 'mean_conf': None, 'diversity_entropy': None})
            break

    return trace


def run_treatment_trial(seed, conf_memory, max_steps=MAX_STEPS,
                          exploit_rate=0.4, mutualism_cost=0.01, mutualism_bonus=0.03):
    """T + attrition + memory-based E/A mutualism mechanic, active from t=0."""
    step_fn = make_memory_step(exploit_rate, mutualism_cost, mutualism_bonus, use_real_memory=True)
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.full((N, N), 1.0)
    mem_state = fresh_memory_state()

    trace = []
    for step in range(max_steps):
        if step % RECORD_INTERVAL == 0:
            trace.append({
                'step': step,
                'live_count': int(life.sum()),
                'mean_conf': mean_population_confidence(life, conf_memory),
                'diversity_entropy': structural_diversity_entropy(life),
            })
        life, energy = step_fn(life, energy, rng, metabolic_cost=METABOLIC_COST, mem_state=mem_state)
        if life.sum() == 0:
            trace.append({'step': step + 1, 'live_count': 0, 'mean_conf': None, 'diversity_entropy': None})
            break

    return trace


if __name__ == "__main__":
    print("Building component-size confidence memory (seeds 0-19, as before)...")
    conf_memory, total = build_component_memory(n_seeds=20)
    print(f"  {len(conf_memory)} buckets\n")

    print(f"Running CONTROL (T+attrition only) on held-out seeds {HELD_OUT_SEEDS[0]}-{HELD_OUT_SEEDS[-1]}...")
    control_traces = {}
    for seed in HELD_OUT_SEEDS:
        control_traces[seed] = run_control_trial(seed, conf_memory)
    print("  done\n")

    print(f"Running TREATMENT (T+attrition+E/A from t=0) on the SAME seeds...")
    treatment_traces = {}
    for seed in HELD_OUT_SEEDS:
        treatment_traces[seed] = run_treatment_trial(seed, conf_memory)
    print("  done\n")

    def summarize(traces, label):
        max_recorded = max(t['step'] for trace in traces.values() for t in trace if t['step'] % RECORD_INTERVAL == 0)
        print(f"\n{'='*90}")
        print(f"{label}")
        print(f"{'='*90}")
        print(f"{'step':>6} {'mean_conf':>10} {'diversity_H':>12} {'mean_live':>10} {'n_alive':>8}")
        for target_step in range(0, max_recorded + 1, RECORD_INTERVAL):
            confs, divs, lives = [], [], []
            n_alive = 0
            for seed, trace in traces.items():
                matching = [t for t in trace if t['step'] == target_step]
                if matching and matching[0]['mean_conf'] is not None:
                    confs.append(matching[0]['mean_conf'])
                    divs.append(matching[0]['diversity_entropy'])
                    lives.append(matching[0]['live_count'])
                    n_alive += 1
            if confs:
                print(f"{target_step:>6} {statistics.mean(confs):>10.4f} {statistics.mean(divs):>12.4f} "
                      f"{statistics.mean(lives):>10.1f} {n_alive:>8}")

    summarize(control_traces, "CONTROL: T + attrition only (no E/A)")
    summarize(treatment_traces, "TREATMENT: T + attrition + E/A mutualism (active from t=0)")
