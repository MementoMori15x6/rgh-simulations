"""
STAGE 10: LOOP CLOSURE, v2 -- using a VALIDATED Distinction event.

The original loop-closure test (stage9) used raw random-soup seeding
directly into the energy-CA substrate as a "weak stand-in" for
Distinction -- explicitly flagged as weaker than the rigorous,
information-theoretically-confirmed causal-insulation result reported
for Gray-Scott under Axiom 1.

This version closes that gap using the newly-validated GoL-native
Distinction result: ignite from an all-dead grid with sparse random
perturbation (density=0.10, confirmed above the real ignition
threshold found via sweep), run PLAIN GoL (no energy mechanics) for
the same settling duration used when causal insulation was confirmed
(1500 steps) -- this is Phase 1, a genuine, validated self-organization
event, not raw noise.

HANDOFF: the resulting life-grid configuration (whatever it settled
into) becomes the STARTING STRUCTURE for Phase 2 -- energy is
initialized uniformly (1.0, matching the original protocol) over
whatever cells are alive at that point, and the validated energy-CA
substrate (Persistence-by-attrition, then E/A) runs from there.

This means Phase 2 now operates on a population that is ALREADY
validated, self-organized structure -- not undifferentiated noise
being asked to simultaneously self-organize AND survive energy
constraints, as in the original test.

Comparison: CONTROL (Phase 2 = pure attrition) vs TREATMENT (Phase 2 =
attrition + E/A from the start of Phase 2), on the same 15 held-out
seeds used throughout this project, plus a direct comparison against
the original (raw-soup) loop-closure numbers.
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
from gol_distinction_ignition import gol_step

IGNITION_DENSITY = 0.10   # validated above-threshold density from the ignition sweep
PHASE1_SETTLE_STEPS = 1500  # matches the settling duration used in the causal-insulation test
PHASE2_MAX_STEPS = 2000
RECORD_INTERVAL = 50
HELD_OUT_SEEDS = list(range(100, 115))  # SAME seeds as stage9, for direct comparability


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
    return -sum(p * math.log2(p) for p in probs if p > 0)


def phase1_distinction(seed):
    """Validated plain-GoL ignition + settling. Returns the resulting
    life grid (Phase 1's output = Phase 2's starting structure)."""
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < IGNITION_DENSITY).astype(int)
    for step in range(PHASE1_SETTLE_STEPS):
        life = gol_step(life)
        if life.sum() == 0:
            return None  # extinct during Phase 1 -- no structure to hand off
    return life


def run_control_trial(seed, conf_memory, max_steps=PHASE2_MAX_STEPS):
    life = phase1_distinction(seed)
    if life is None:
        return [{'step': 0, 'live_count': 0, 'mean_conf': None, 'diversity_entropy': None}]
    energy = np.where(life == 1, 1.0, 0.0)  # energy only where Phase 1 left live cells

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


def run_treatment_trial(seed, conf_memory, max_steps=PHASE2_MAX_STEPS,
                          exploit_rate=0.4, mutualism_cost=0.01, mutualism_bonus=0.03):
    life = phase1_distinction(seed)
    if life is None:
        return [{'step': 0, 'live_count': 0, 'mean_conf': None, 'diversity_entropy': None}]
    energy = np.where(life == 1, 1.0, 0.0)

    step_fn = make_memory_step(exploit_rate, mutualism_cost, mutualism_bonus, use_real_memory=True)
    rng = np.random.default_rng(seed + 50000)  # fresh rng for Phase 2's own randomness
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

    print(f"Phase 1 (validated Distinction) + Phase 2 CONTROL, seeds {HELD_OUT_SEEDS[0]}-{HELD_OUT_SEEDS[-1]}...")
    control_traces = {}
    for seed in HELD_OUT_SEEDS:
        control_traces[seed] = run_control_trial(seed, conf_memory)
    print("  done\n")

    print("Phase 1 (validated Distinction) + Phase 2 TREATMENT (E/A from start of Phase 2)...")
    treatment_traces = {}
    for seed in HELD_OUT_SEEDS:
        treatment_traces[seed] = run_treatment_trial(seed, conf_memory)
    print("  done\n")

    def final_state(traces, seed):
        valid = [t for t in traces[seed] if t['mean_conf'] is not None]
        return valid[-1] if valid else None

    print("=" * 90)
    print("PAIRED COMPARISON AT FINAL RECORDED STATE (matched by seed)")
    print("=" * 90)

    live_c, live_t, div_c, div_t, conf_c, conf_t = [], [], [], [], [], []
    for seed in HELD_OUT_SEEDS:
        fc = final_state(control_traces, seed)
        ft = final_state(treatment_traces, seed)
        if fc and ft:
            live_c.append(fc['live_count']); live_t.append(ft['live_count'])
            div_c.append(fc['diversity_entropy']); div_t.append(ft['diversity_entropy'])
            conf_c.append(fc['mean_conf']); conf_t.append(ft['mean_conf'])

    def paired_report(name, vals_c, vals_t):
        diffs = [t - c for c, t in zip(vals_c, vals_t)]
        d_mean = statistics.mean(diffs)
        d_std = statistics.pstdev(diffs)
        t_stat = d_mean / (d_std / (len(diffs) ** 0.5)) if d_std > 0 else float('inf')
        print(f"{name}: control_mean={statistics.mean(vals_c):.4f}, treatment_mean={statistics.mean(vals_t):.4f}, "
              f"paired_diff={d_mean:+.4f}, paired_t={t_stat:.3f}, n={len(diffs)}")

    paired_report("LIVE COUNT", live_c, live_t)
    paired_report("DIVERSITY ENTROPY", div_c, div_t)
    paired_report("MEAN CONFIDENCE", conf_c, conf_t)

    print("\nFor comparison, original (raw-soup stand-in) loop-closure result was:")
    print("  LIVE COUNT: control=15.3, treatment=78.3, paired_t=10.16")
    print("  DIVERSITY ENTROPY: control=1.014, treatment=1.991, paired_t=4.49")
    print("  MEAN CONFIDENCE: control=0.657, treatment=0.631, paired_t=-1.51")
