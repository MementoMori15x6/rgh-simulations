"""
STAGE 9: Layer 0 test, extended to Axioms 2 & 3 (Transformation, Persistence).

Layer 0 found that Distinction (Axiom 1) requires genuine dissipative
flux -- remove it, and structure collapses rather than merely
weakening. This asks the analogous question for Persistence: does the
differential-survival drift toward high-persistence-confidence
structures (the validated Axioms 2&3 finding) require real dissipation
(metabolic cost -- the direct energy-CA analog of Gray-Scott's F, k),
or does it emerge from the discrete transformation rule alone, with no
thermodynamic driving needed at all?

The sharp, testable prediction: plain Conway's Game of Life, with NO
energy concept whatsoever, is already documented to settle toward
blocks and gliders on its own -- that's a property of the discrete
rule's own logic (unstable configurations die under the rule itself),
not something requiring real thermodynamic flux. If that's right, the
NON-DISSIPATIVE condition here (metabolic_cost=0, cells only die via
GoL's own neighbor-count rule) should show the SAME drift toward high-
confidence structures as the validated DISSIPATIVE condition
(metabolic_cost=0.04) -- unlike Distinction, where removing dissipation
destroyed the effect entirely.

Reuses the exact validated differential-survival protocol and the
independently-built, held-out component-size confidence memory --
same methodology, same seeds, only metabolic_cost differs between
conditions.
"""

import numpy as np
import statistics
from stage1_salvageability_memory import gol_neighbor_count, N, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION
from stage6_component_memory import build_component_memory
from stage8_differential_survival import mean_population_confidence, SOUP_DENSITY, MAX_STEPS, RECORD_INTERVAL, HELD_OUT_SEEDS


def energy_step_variable_cost(life, energy, metabolic_cost):
    """Identical to the validated energy_step, but with metabolic_cost
    exposed as a real argument rather than a fixed default -- lets us
    run the DISSIPATIVE (0.04) and NON-DISSIPATIVE (0.0) conditions
    with the exact same underlying mechanism."""
    n_rows, n_cols = life.shape
    neighbor_count = gol_neighbor_count(life)
    survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
    born = (life == 0) & (neighbor_count == 3)

    neighbor_avg = (
        np.roll(energy, 1, 0) + np.roll(energy, -1, 0) +
        np.roll(energy, 1, 1) + np.roll(energy, -1, 1)
    ) / 4.0
    energy = energy + 0.1 * (neighbor_avg - energy)
    energy = energy + BACKGROUND_INFLOW
    energy = energy * (1 - BACKGROUND_DECAY)
    energy = np.where(life == 1, energy - metabolic_cost, energy)

    birth_cost = BIRTH_ENERGY_FRACTION * neighbor_avg
    energy = np.where(born, energy + birth_cost, energy)
    cost_share = np.zeros_like(energy)
    if born.any():
        rows, cols = np.where(born)
        for r, c in zip(rows.tolist(), cols.tolist()):
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                rr, cc = (r + dr) % n_rows, (c + dc) % n_cols
                cost_share[rr, cc] += birth_cost[r, c] / 4.0
    energy = energy - cost_share

    life_next = np.zeros_like(life)
    life_next[survives & (energy > 0)] = 1
    life_next[born & (energy > 0)] = 1
    energy_next = np.clip(energy, 0, None)

    return life_next, energy_next


def run_trial(seed, memory, metabolic_cost, max_steps=MAX_STEPS):
    rng = np.random.default_rng(seed)
    life = (rng.random((N, N)) < SOUP_DENSITY).astype(int)
    energy = np.full((N, N), 1.0)

    trace = []
    for step in range(max_steps):
        if step % RECORD_INTERVAL == 0:
            live_count = int(life.sum())
            mean_conf = mean_population_confidence(life, memory)
            trace.append({'step': step, 'live_count': live_count, 'mean_conf': mean_conf})

        life, energy = energy_step_variable_cost(life, energy, metabolic_cost)
        if life.sum() == 0:
            trace.append({'step': step + 1, 'live_count': 0, 'mean_conf': None})
            break

    return trace


def summarize(traces, label):
    print(f"\n{'='*80}\n{label}\n{'='*80}")
    print(f"{'step':>6} {'mean_conf':>10} {'mean_live':>10} {'n_alive':>8}")
    max_step = max(t['step'] for trace in traces.values() for t in trace if t['step'] % RECORD_INTERVAL == 0)
    for target_step in range(0, max_step + 1, RECORD_INTERVAL):
        confs, lives = [], []
        n_alive = 0
        for seed, trace in traces.items():
            matching = [t for t in trace if t['step'] == target_step]
            if matching and matching[0]['mean_conf'] is not None:
                confs.append(matching[0]['mean_conf'])
                lives.append(matching[0]['live_count'])
                n_alive += 1
        if confs:
            print(f"{target_step:>6} {statistics.mean(confs):>10.4f} {statistics.mean(lives):>10.1f} {n_alive:>8}")


if __name__ == "__main__":
    print("Building component-size confidence memory (seeds 0-19, as before)...")
    memory, _ = build_component_memory(n_seeds=20)
    print(f"  {len(memory)} buckets\n")

    print(f"Running DISSIPATIVE condition (metabolic_cost=0.04) on held-out seeds "
          f"{HELD_OUT_SEEDS[0]}-{HELD_OUT_SEEDS[-1]}...")
    dissipative_traces = {}
    for seed in HELD_OUT_SEEDS:
        dissipative_traces[seed] = run_trial(seed, memory, metabolic_cost=0.04)
    print("  done")

    print(f"Running NON-DISSIPATIVE condition (metabolic_cost=0.0) on the SAME seeds...")
    nondissipative_traces = {}
    for seed in HELD_OUT_SEEDS:
        nondissipative_traces[seed] = run_trial(seed, memory, metabolic_cost=0.0)
    print("  done")

    summarize(dissipative_traces, "DISSIPATIVE (metabolic_cost=0.04) -- validated baseline")
    summarize(nondissipative_traces, "NON-DISSIPATIVE (metabolic_cost=0.0) -- new test")
