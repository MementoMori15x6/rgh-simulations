"""
STAGE 3: memory-based exploit/mutualism strategy switching, stress-tested.

This is the key positive result of the E/A line of this project. It
tests whether a population that tracks realized per-neighbor outcomes
of exploitation vs. mutualism, and switches strategy toward whichever
has paid off better, discovers a genuine survival advantage under
environmental stress -- compared against four other conditions:
pure exploitation, pure mutualism, memoryless random choice, and a
critical control (same switching structure, but the "preferred"
strategy is random rather than learned).

Protocol: populations reach equilibrium under normal metabolic cost,
then are subjected to a metabolic shock (cost raised to a level that
reliably kills unconstrained populations) for a fixed duration.
Shock survival rate across many seeds is the outcome measure.

Result (15 seeds each, see RGH_EA_Findings.md for full writeup):
  Pure exploitation:        7/15 survived
  Pure mutualism:          15/15 survived
  Memoryless 50/50:         5/15 survived
  Random-preference control: 7/15 survived
  Memory-based switching:  15/15 survived  <-- matches pure mutualism
"""

import numpy as np
from stage1_energy_baseline import gol_neighbor_count, N, BACKGROUND_INFLOW, BACKGROUND_DECAY, BIRTH_ENERGY_FRACTION
from stage2b_exploit_mutualism_SIGN_FIXED import DIFFUSION_RATE
from stage1b_robustness_check import random_soup_seed

EXPLORATION_PROB = 0.1
EQUILIBRIUM_STEPS = 1000
SHOCK_METABOLIC = 0.09
SHOCK_STEPS = 500


def make_memory_step(exploit_rate, mutualism_cost, mutualism_bonus, use_real_memory=True):
    """
    use_real_memory=True: the standard memory-based mechanism -- each
      cell tracks a running average payoff per strategy, per relative
      neighbor direction, and prefers whichever has paid off better,
      with EXPLORATION_PROB chance of trying the other option anyway.
    use_real_memory=False: the ISOLATING CONTROL -- identical switching
      structure and exploration rate, but the "preferred" strategy is
      chosen randomly rather than from learned history. This is what
      rules out "exploration/switching structure alone" as the source
      of any observed effect.
    """
    def transfer_with_memory(energy, life, rng, mutual_avg, exploit_avg, mutual_count, exploit_count):
        n_rows, n_cols = life.shape
        energy_delta = np.zeros_like(energy)

        for dr, dc in [(0, 1), (1, 0)]:
            neighbor_life = np.roll(np.roll(life, -dr, axis=0), -dc, axis=1)
            neighbor_energy = np.roll(np.roll(energy, -dr, axis=0), -dc, axis=1)
            both_alive = (life == 1) & (neighbor_life == 1)

            key = (dr, dc)
            m_avg = mutual_avg[key]
            e_avg = exploit_avg[key]
            m_cnt = mutual_count[key]
            e_cnt = exploit_count[key]

            if use_real_memory:
                has_history = (m_cnt > 0) & (e_cnt > 0)
                prefers_mutualism = m_avg > e_avg
                no_history_choice = rng.random(life.shape) < 0.5
                chooses_mutualism_pref = np.where(has_history, prefers_mutualism, no_history_choice)
            else:
                chooses_mutualism_pref = rng.random(life.shape) < 0.5

            explore_roll = rng.random(life.shape)
            explores = explore_roll < EXPLORATION_PROB
            chooses_mutualism = both_alive & np.where(explores, ~chooses_mutualism_pref, chooses_mutualism_pref)
            chooses_exploit = both_alive & ~chooses_mutualism

            this_gain_mutual = -mutualism_cost + mutualism_bonus
            energy_delta = np.where(chooses_mutualism, energy_delta + this_gain_mutual, energy_delta)
            neighbor_delta_mutualism = np.where(chooses_mutualism, this_gain_mutual, 0.0)

            this_richer = energy > neighbor_energy
            uncapped_draw = exploit_rate * (energy - neighbor_energy)
            capped_draw = np.minimum(uncapped_draw, np.maximum(neighbor_energy, 0.0))
            this_gain_exploit = np.where(this_richer, capped_draw, -DIFFUSION_RATE * (energy - neighbor_energy))
            flow_to_this = np.where(chooses_exploit, this_gain_exploit, 0.0)
            energy_delta = energy_delta + flow_to_this
            neighbor_delta_exploit = -flow_to_this

            not_both_alive = ~both_alive
            diffusion_flow = np.where(not_both_alive, DIFFUSION_RATE * (neighbor_energy - energy), 0.0)
            energy_delta = energy_delta + diffusion_flow
            neighbor_delta_diffusion = -diffusion_flow

            total_neighbor_delta = np.where(chooses_mutualism, neighbor_delta_mutualism,
                                     np.where(chooses_exploit, neighbor_delta_exploit, neighbor_delta_diffusion))
            scattered = np.roll(np.roll(total_neighbor_delta, dr, axis=0), dc, axis=1)
            energy_delta = energy_delta + scattered

            if use_real_memory:
                new_m_cnt = m_cnt + chooses_mutualism.astype(float)
                new_e_cnt = e_cnt + chooses_exploit.astype(float)
                safe_new_m_cnt = np.maximum(new_m_cnt, 1)
                safe_new_e_cnt = np.maximum(new_e_cnt, 1)
                new_m_avg = np.where(chooses_mutualism, m_avg + (this_gain_mutual - m_avg) / safe_new_m_cnt, m_avg)
                new_e_avg = np.where(chooses_exploit, e_avg + (this_gain_exploit - e_avg) / safe_new_e_cnt, e_avg)
                mutual_avg[key] = new_m_avg
                exploit_avg[key] = new_e_avg
                mutual_count[key] = new_m_cnt
                exploit_count[key] = new_e_cnt

        return energy + energy_delta

    def step(life, energy, rng, metabolic_cost, mem_state):
        n_rows, n_cols = life.shape
        neighbor_count = gol_neighbor_count(life)
        survives = (life == 1) & ((neighbor_count == 2) | (neighbor_count == 3))
        born = (life == 0) & (neighbor_count == 3)

        energy = transfer_with_memory(energy, life, rng, *mem_state)

        energy = energy + BACKGROUND_INFLOW
        energy = energy * (1 - BACKGROUND_DECAY)
        energy = np.where(life == 1, energy - metabolic_cost, energy)
        neighbor_energy_avg = (
            np.roll(energy, 1, 0) + np.roll(energy, -1, 0) +
            np.roll(energy, 1, 1) + np.roll(energy, -1, 1)
        ) / 4.0
        birth_cost = BIRTH_ENERGY_FRACTION * neighbor_energy_avg
        energy = np.where(born, energy + birth_cost, energy)
        cost_share = np.zeros_like(energy)
        if born.any():
            rows, cols = np.where(born)
            for r, c in zip(rows.tolist(), cols.tolist()):
                for ddr, ddc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    rr, cc = (r + ddr) % n_rows, (c + ddc) % n_cols
                    cost_share[rr, cc] += birth_cost[r, c] / 4.0
        energy = energy - cost_share
        life_next = np.zeros_like(life)
        life_next[survives & (energy > 0)] = 1
        life_next[born & (energy > 0)] = 1
        energy = np.clip(energy, 0, None)
        return life_next, energy

    return step


def fresh_memory_state():
    return (
        {(dr, dc): np.zeros((N, N)) for dr, dc in [(0, 1), (1, 0)]},
        {(dr, dc): np.zeros((N, N)) for dr, dc in [(0, 1), (1, 0)]},
        {(dr, dc): np.zeros((N, N)) for dr, dc in [(0, 1), (1, 0)]},
        {(dr, dc): np.zeros((N, N)) for dr, dc in [(0, 1), (1, 0)]},
    )


def run_memory_stress_test(seed, use_real_memory=True):
    step_fn = make_memory_step(0.4, 0.01, 0.03, use_real_memory=use_real_memory)
    rng = np.random.default_rng(seed)
    life, energy = random_soup_seed(N, 0.15, rng)
    mem_state = fresh_memory_state()

    for i in range(EQUILIBRIUM_STEPS):
        life, energy = step_fn(life, energy, rng, metabolic_cost=0.04, mem_state=mem_state)
        if life.sum() == 0:
            return {'pre_shock_live': 0, 'survived_shock': False, 'post_shock_live': 0}

    pre_shock_live = int(life.sum())
    extinct = False
    for i in range(SHOCK_STEPS):
        life, energy = step_fn(life, energy, rng, metabolic_cost=SHOCK_METABOLIC, mem_state=mem_state)
        if life.sum() == 0:
            extinct = True
            break

    return {
        'pre_shock_live': pre_shock_live,
        'survived_shock': not extinct,
        'post_shock_live': int(life.sum()) if not extinct else 0,
    }


if __name__ == "__main__":
    N_SEEDS = 15

    print(f"MEMORY-BASED STRATEGY SWITCHING (real learning), stress test, {N_SEEDS} seeds")
    print(f"{'seed':>5} {'pre_shock':>10} {'survived?':>10} {'post_shock':>11}")
    memory_survivals = []
    for seed in range(N_SEEDS):
        r = run_memory_stress_test(seed, use_real_memory=True)
        memory_survivals.append(r['survived_shock'])
        print(f"{seed:>5} {r['pre_shock_live']:>10} {str(r['survived_shock']):>10} {r['post_shock_live']:>11}")
    print(f"\nMemory-based (real learning) shock survival: {sum(memory_survivals)}/{N_SEEDS}\n")

    print(f"RANDOM-PREFERENCE CONTROL (same structure, no real learning), {N_SEEDS} seeds")
    print(f"{'seed':>5} {'pre_shock':>10} {'survived?':>10} {'post_shock':>11}")
    control_survivals = []
    for seed in range(N_SEEDS):
        r = run_memory_stress_test(seed, use_real_memory=False)
        control_survivals.append(r['survived_shock'])
        print(f"{seed:>5} {r['pre_shock_live']:>10} {str(r['survived_shock']):>10} {r['post_shock_live']:>11}")
    print(f"\nRandom-preference control shock survival: {sum(control_survivals)}/{N_SEEDS}")

    print(f"\n{'='*60}")
    print(f"SUMMARY: memory-based={sum(memory_survivals)}/{N_SEEDS}, "
          f"random-preference control={sum(control_survivals)}/{N_SEEDS}")
    print("If memory-based clearly exceeds the control, the effect is due to")
    print("genuine learning, not the exploration/switching structure alone.")
