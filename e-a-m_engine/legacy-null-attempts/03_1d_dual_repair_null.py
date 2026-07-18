"""
Fixes the mislabeling from the previous script: that version tagged memory
only as "rose" vs "didn't rise" and called the latter "homeostatic" without
ever checking return-to-baseline. This version restores the actual
tolerance-based restabilization criterion (validated last turn) and tests
BOTH repair mechanisms (temporal-copy, spatial-mirror) against it fairly,
using the same real vs exact-rate-matched-shuffled structure.
"""
import random
import statistics
import math
from collections import defaultdict, Counter

N = 300
STEPS = 200
RULE = 110
N_SEEDS = 30
WINDOW = 6
K_SHORT = 5
K_MED = 15
K_LONG = 30
INTERVENE_THRESHOLD = 0.55
BASELINE_TOLERANCE = 0.05  # calibrated last turn against actual entropy distribution

def rule_table(rule_number):
    bits = [(rule_number >> i) & 1 for i in range(8)]
    table = {}
    for i in range(8):
        left, center, right = (i >> 2) & 1, (i >> 1) & 1, i & 1
        table[(left, center, right)] = bits[i]
    return table

TABLE = rule_table(RULE)

def is_trivial(S):
    return all(b == 0 for b in S) or all(b == 1 for b in S)

def D(S, rng=None):
    if all(b == 0 for b in S):
        S = S.copy()
        pos = rng.randrange(len(S)) if rng is not None else len(S) // 2
        S[pos] = 1
        return S
    return S

def T(S):
    n = len(S)
    return [TABLE[(S[(i-1) % n], S[i], S[(i+1) % n])] for i in range(n)]

def E(S):
    n = len(S)
    return [i for i in range(n) if S[i] == 1 and S[(i+1) % n] == 0]

def P(S):
    return not is_trivial(S)

def local_entropy(S, center, window=WINDOW):
    n = len(S)
    bits = [S[(center + k) % n] for k in range(-window, window + 1)]
    c = Counter(bits)
    total = len(bits)
    ent = 0.0
    for v in c.values():
        p = v / total
        ent -= p * math.log2(p) if p > 0 else 0
    return ent

def signature(S, center, window=WINDOW):
    n = len(S)
    return tuple(S[(center + k) % n] for k in range(-window, window + 1))

# --- TRUE dual-tail memory: destabilization AND tolerance-based restabilization ---
def build_dual_memory(n_obs_seeds=30):
    memory = defaultdict(lambda: {"destab": [0, 0], "restab": [0, 0]})
    for seed in range(n_obs_seeds):
        rng = random.Random(seed)
        S = [0] * N
        trace = []
        t = 0
        alive = True
        while t < STEPS and alive:
            S = D(S, rng=rng)
            S_next = T(S)
            alive = P(S_next)
            S = S_next
            trace.append(S.copy())
            t += 1

        n_steps = len(trace)
        last_nonboundary_entropy = [None] * N
        for t_idx in range(n_steps):
            St = trace[t_idx]
            boundary_sites = set(E(St))
            for pos in range(N):
                if pos not in boundary_sites:
                    last_nonboundary_entropy[pos] = local_entropy(St, pos)

            if t_idx + K_LONG >= n_steps:
                continue

            for site in boundary_sites:
                sig = signature(St, site)
                baseline = last_nonboundary_entropy[site]
                if baseline is None:
                    continue
                h_now = local_entropy(St, site)
                h_short = local_entropy(trace[t_idx + K_SHORT], site)
                h_long = local_entropy(trace[t_idx + K_LONG], site)

                if h_short > h_now:
                    memory[sig]["destab"][1] += 1
                else:
                    memory[sig]["destab"][0] += 1

                if abs(h_long - baseline) <= BASELINE_TOLERANCE:
                    memory[sig]["restab"][0] += 1  # returned
                else:
                    memory[sig]["restab"][1] += 1  # stayed off
    return memory

def restab_confidence(memory, sig):
    d = memory.get(sig)
    if d is None:
        return 0.0
    ret, off = d["restab"]
    total = ret + off
    return (ret / total) if total > 0 else 0.0

def apply_temporal_repair(S_current, S_prev, target_idx):
    S_current[target_idx] = S_prev[target_idx]

def apply_spatial_mirroring(S_current, target_idx):
    n = len(S_current)
    S_current[target_idx] = S_current[(target_idx - 1) % n]

def gather_relaxation(interv_trace, states_trace, baselines_trace):
    dh_5, dh_15, dh_30 = [], [], []
    gap_30 = []  # |h_long - baseline| -- the actual homeostasis metric
    for step_idx, samples in enumerate(interv_trace):
        baselines = baselines_trace[step_idx]
        for (target, h_now), baseline in zip(samples, baselines):
            if step_idx + K_SHORT < len(states_trace):
                dh_5.append(local_entropy(states_trace[step_idx + K_SHORT], target) - h_now)
            if step_idx + K_MED < len(states_trace):
                dh_15.append(local_entropy(states_trace[step_idx + K_MED], target) - h_now)
            if step_idx + K_LONG < len(states_trace):
                h_long = local_entropy(states_trace[step_idx + K_LONG], target)
                dh_30.append(h_long - h_now)
                gap_30.append(abs(h_long - baseline))
    return (statistics.mean(dh_5) if dh_5 else 0,
            statistics.mean(dh_15) if dh_15 else 0,
            statistics.mean(dh_30) if dh_30 else 0,
            statistics.mean(gap_30) if gap_30 else None)

def run_experiment_pair(memory, seed, repair_mode="temporal"):
    salt = 20000 if repair_mode == "temporal" else 30000

    rng_t = random.Random(seed + salt)
    S = [0] * N
    S_prev = S.copy()
    last_nonboundary_entropy = [None] * N
    t = 0
    alive = True

    targeted_interventions_history = []
    t_states_trace = []
    t_interv_sites_trace = []
    t_baselines_trace = []

    while t < STEPS and alive:
        S_current = D(S, rng=rng_t)
        boundary_sites = set(E(S_current))
        for pos in range(N):
            if pos not in boundary_sites:
                last_nonboundary_entropy[pos] = local_entropy(S_current, pos)

        S_next = T(S_current)
        sites = list(boundary_sites)

        step_interventions = 0
        step_samples = []
        step_baselines = []
        override_sites = []

        for i in sites:
            sig = signature(S_current, i)
            conf = restab_confidence(memory, sig)
            if conf > INTERVENE_THRESHOLD and rng_t.random() < conf:
                target_cell = (i + 1) % len(S)
                baseline = last_nonboundary_entropy[target_cell]
                if baseline is None:
                    continue
                override_sites.append(target_cell)
                step_samples.append((target_cell, local_entropy(S_current, target_cell)))
                step_baselines.append(baseline)
                step_interventions += 1

        for target in override_sites:
            if repair_mode == "temporal":
                apply_temporal_repair(S_next, S_prev, target)
            else:
                apply_spatial_mirroring(S_next, target)

        alive = P(S_next)
        S_prev = S_current.copy()
        S = S_next
        targeted_interventions_history.append(step_interventions)
        t_states_trace.append(S.copy())
        t_interv_sites_trace.append(step_samples)
        t_baselines_trace.append(step_baselines)
        t += 1

    rng_s = random.Random(seed + salt)
    S_s = [0] * N
    S_prev_s = S_s.copy()
    last_nonboundary_entropy_s = [None] * N
    t = 0
    alive_s = True

    s_states_trace = []
    s_interv_sites_trace = []
    s_baselines_trace = []

    while t < STEPS and alive_s:
        S_current_s = D(S_s, rng=rng_s)
        boundary_sites_s = set(E(S_current_s))
        for pos in range(N):
            if pos not in boundary_sites_s:
                last_nonboundary_entropy_s[pos] = local_entropy(S_current_s, pos)

        S_next_s = T(S_current_s)
        sites_s = list(boundary_sites_s)
        target_budget = targeted_interventions_history[t] if t < len(targeted_interventions_history) else 0

        shuffled_triggered_sites = []
        for i in sites_s:
            sig = signature(S_current_s, i)
            lookup_sig = tuple(reversed(sig))
            lookup_sig = lookup_sig[2:] + lookup_sig[:2]
            conf = restab_confidence(memory, lookup_sig)
            if conf > INTERVENE_THRESHOLD and rng_s.random() < conf:
                shuffled_triggered_sites.append((i + 1) % len(S_s))

        selected_targets = shuffled_triggered_sites[:target_budget]
        if len(selected_targets) < target_budget:
            all_possible = [(s + 1) % len(S_s) for s in sites_s]
            remaining = [s for s in all_possible if s not in selected_targets]
            needed = target_budget - len(selected_targets)
            selected_targets.extend(rng_s.sample(remaining, min(needed, len(remaining))))

        step_samples_s = []
        step_baselines_s = []
        for target in selected_targets:
            baseline = last_nonboundary_entropy_s[target]
            if baseline is None:
                continue
            step_samples_s.append((target, local_entropy(S_current_s, target)))
            step_baselines_s.append(baseline)
            if repair_mode == "temporal":
                apply_temporal_repair(S_next_s, S_prev_s, target)
            else:
                apply_spatial_mirroring(S_next_s, target)

        alive_s = P(S_next_s)
        S_prev_s = S_current_s.copy()
        S_s = S_next_s
        s_states_trace.append(S_s.copy())
        s_interv_sites_trace.append(step_samples_s)
        s_baselines_trace.append(step_baselines_s)
        t += 1

    t_5, t_15, t_30, t_gap = gather_relaxation(t_interv_sites_trace, t_states_trace, t_baselines_trace)
    s_5, s_15, s_30, s_gap = gather_relaxation(s_interv_sites_trace, s_states_trace, s_baselines_trace)

    return {"t5": t_5, "t15": t_15, "t30": t_30, "t_gap": t_gap,
            "s5": s_5, "s15": s_15, "s30": s_30, "s_gap": s_gap}


if __name__ == "__main__":
    print("Building TRUE dual-tail memory (destab + tolerance-based restab)...")
    memory = build_dual_memory(30)

    for mode in ["temporal", "spatial"]:
        print(f"\n{'='*60}\nREPAIR MODE: {mode.upper()}\n{'='*60}")
        results = [run_experiment_pair(memory, seed, mode) for seed in range(N_SEEDS)]
        valid = [r for r in results if r["t_gap"] is not None and r["s_gap"] is not None]
        print(f"Valid seeds: {len(valid)}/{N_SEEDS}")

        for key, label in [("t5","dH @ K=5"),("t15","dH @ K=15"),("t30","dH @ K=30")]:
            tvals = [r[key] for r in results]
            svals = [r["s"+key[1:]] for r in results]
            tm, ts = statistics.mean(tvals), statistics.pstdev(tvals)
            sm, ss = statistics.mean(svals), statistics.pstdev(svals)
            print(f"  TARGETED {label}: {tm:+.4f} (std {ts:.4f})   SHUFFLED: {sm:+.4f} (std {ss:.4f})")

        if valid:
            tgaps = [r["t_gap"] for r in valid]
            sgaps = [r["s_gap"] for r in valid]
            tm, ts = statistics.mean(tgaps), statistics.pstdev(tgaps) if len(tgaps)>1 else 0
            sm, ss = statistics.mean(sgaps), statistics.pstdev(sgaps) if len(sgaps)>1 else 0
            print(f"\n  HOMEOSTASIS METRIC |h_long - true_baseline|:")
            print(f"  TARGETED: {tm:.4f} (std {ts:.4f})   SHUFFLED: {sm:.4f} (std {ss:.4f})")
            diffs = [t-s for t,s in zip(tgaps, sgaps)]
            dm = statistics.mean(diffs)
            dsd = statistics.pstdev(diffs) if len(diffs)>1 else 0
            paired_t = dm/(dsd/(len(diffs)**0.5)) if dsd>0 else (float('inf') if dm!=0 else 0)
            print(f"  Paired diff (targeted-shuffled): {dm:+.4f} (std {dsd:.4f})  paired-t={paired_t:.3f}")
            print("  (negative diff = targeted closer to true baseline = real homeostasis)")
