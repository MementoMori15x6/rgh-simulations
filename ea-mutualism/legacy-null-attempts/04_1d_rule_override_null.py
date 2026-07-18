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
BASELINE_TOLERANCE = 0.05
OVERRIDE_DURATION = 5

def rule_table(rule_number):
    bits = [(rule_number >> i) & 1 for i in range(8)]
    table = {}
    for i in range(8):
        left, center, right = (i >> 2) & 1, (i >> 1) & 1, i & 1
        table[(left, center, right)] = bits[i]
    return table

BASE_TABLE = rule_table(RULE)

def is_trivial(S):
    return all(b == 0 for b in S) or all(b == 1 for b in S)

def D(S, rng=None):
    if all(b == 0 for b in S):
        S = S.copy()
        pos = rng.randrange(len(S)) if rng is not None else len(S) // 2
        S[pos] = 1
        return S
    return S

def T_local(S, active_overrides):
    n = len(S)
    S_next = [0] * n
    for i in range(n):
        triple = (S[(i-1) % n], S[i], S[(i+1) % n])
        if i in active_overrides and triple == active_overrides[i]["target_triple"]:
            S_next[i] = 1 - BASE_TABLE[triple]
        else:
            S_next[i] = BASE_TABLE[triple]
    return S_next

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
            n = len(S)
            S_next = [BASE_TABLE[(S[(i-1) % n], S[i], S[(i+1) % n])] for i in range(n)]
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
                    memory[sig]["restab"][0] += 1
                else:
                    memory[sig]["restab"][1] += 1
    return memory

def restab_confidence(memory, sig):
    d = memory.get(sig)
    if d is None:
        return 0.0
    ret, off = d["restab"]
    total = ret + off
    return (ret / total) if total > 0 else 0.0

def gather_relaxation(interv_trace, states_trace, baselines_trace):
    dh_5, dh_15, dh_30 = [], [], []
    gap_30 = []
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

def run_experiment_pair(memory, seed):
    rng_t = random.Random(seed + 40000)
    S = [0] * N
    last_nonboundary_entropy = [None] * N
    active_overrides = {}
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

        expired = []
        for idx in active_overrides:
            active_overrides[idx]["timer"] -= 1
            if active_overrides[idx]["timer"] <= 0:
                expired.append(idx)
        for idx in expired:
            del active_overrides[idx]

        sites = list(boundary_sites)
        step_interventions = 0
        step_samples = []
        step_baselines = []

        for i in sites:
            sig = signature(S_current, i)
            conf = restab_confidence(memory, sig)
            if conf > INTERVENE_THRESHOLD and rng_t.random() < conf:
                target_cell = (i + 1) % N
                baseline = last_nonboundary_entropy[target_cell]
                if baseline is None:
                    continue
                triple = (S_current[(target_cell-1) % N], S_current[target_cell], S_current[(target_cell+1) % N])
                active_overrides[target_cell] = {"timer": OVERRIDE_DURATION, "target_triple": triple}
                step_samples.append((target_cell, local_entropy(S_current, target_cell)))
                step_baselines.append(baseline)
                step_interventions += 1

        S_next = T_local(S_current, active_overrides)
        alive = P(S_next)
        S = S_next
        targeted_interventions_history.append(step_interventions)
        t_states_trace.append(S.copy())
        t_interv_sites_trace.append(step_samples)
        t_baselines_trace.append(step_baselines)
        t += 1

    rng_s = random.Random(seed + 40000)
    S_s = [0] * N
    last_nonboundary_entropy_s = [None] * N
    active_overrides_s = {}
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

        expired_s = []
        for idx in active_overrides_s:
            active_overrides_s[idx]["timer"] -= 1
            if active_overrides_s[idx]["timer"] <= 0:
                expired_s.append(idx)
        for idx in expired_s:
            del active_overrides_s[idx]

        sites_s = list(boundary_sites_s)
        target_budget = targeted_interventions_history[t] if t < len(targeted_interventions_history) else 0

        shuffled_triggered_sites = []
        for i in sites_s:
            sig = signature(S_current_s, i)
            lookup_sig = tuple(reversed(sig))
            lookup_sig = lookup_sig[2:] + lookup_sig[:2]
            conf = restab_confidence(memory, lookup_sig)
            if conf > INTERVENE_THRESHOLD and rng_s.random() < conf:
                shuffled_triggered_sites.append((i + 1) % N)

        selected_targets = shuffled_triggered_sites[:target_budget]
        if len(selected_targets) < target_budget:
            all_possible = [(s + 1) % N for s in sites_s]
            remaining = [s for s in all_possible if s not in selected_targets]
            needed = target_budget - len(selected_targets)
            selected_targets.extend(rng_s.sample(remaining, min(needed, len(remaining))))

        step_samples_s = []
        step_baselines_s = []
        for target in selected_targets:
            baseline = last_nonboundary_entropy_s[target]
            if baseline is None:
                continue
            triple_s = (S_current_s[(target-1) % N], S_current_s[target], S_current_s[(target+1) % N])
            active_overrides_s[target] = {"timer": OVERRIDE_DURATION, "target_triple": triple_s}
            step_samples_s.append((target, local_entropy(S_current_s, target)))
            step_baselines_s.append(baseline)

        S_next_s = T_local(S_current_s, active_overrides_s)
        alive_s = P(S_next_s)
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
    print("Building dual-tail memory arrays...")
    memory = build_dual_memory(N_SEEDS)

    print("Running parallel paired-variant experiments...")
    results = [run_experiment_pair(memory, seed) for seed in range(N_SEEDS)]
    valid = [r for r in results if r["t_gap"] is not None and r["s_gap"] is not None]

    t5_vals = [r["t5"] for r in results]
    t15_vals = [r["t15"] for r in results]
    t30_vals = [r["t30"] for r in results]
    s5_vals = [r["s5"] for r in results]
    s15_vals = [r["s15"] for r in results]
    s30_vals = [r["s30"] for r in results]

    tgaps = [r["t_gap"] for r in valid]
    sgaps = [r["s_gap"] for r in valid]
    diffs = [t - s for t, s in zip(tgaps, sgaps)]

    dm = statistics.mean(diffs)
    dsd = statistics.pstdev(diffs) if len(diffs) > 1 else 0
    paired_t = dm / (dsd / (len(diffs) ** 0.5)) if dsd > 0 else 0

    print("\n" + "="*60)
    print("REPAIR MODE: PROCESS-LEVEL RULE OVERRIDE")
    print("="*60)
    print(f"Valid seeds: {len(valid)}/{N_SEEDS}\n")
    print("  RELAXATION VECTOR (dH):")
    print(f"  TARGETED dH @ K=5 : {statistics.mean(t5_vals):+.4f} (std {statistics.pstdev(t5_vals):.4f})   SHUFFLED: {statistics.mean(s5_vals):+.4f} (std {statistics.pstdev(s5_vals):.4f})")
    print(f"  TARGETED dH @ K=15: {statistics.mean(t15_vals):+.4f} (std {statistics.pstdev(t15_vals):.4f})   SHUFFLED: {statistics.mean(s15_vals):+.4f} (std {statistics.pstdev(s15_vals):.4f})")
    print(f"  TARGETED dH @ K=30: {statistics.mean(t30_vals):+.4f} (std {statistics.pstdev(t30_vals):.4f})   SHUFFLED: {statistics.mean(s30_vals):+.4f} (std {statistics.pstdev(s30_vals):.4f})\n")
    print("  HOMEOSTASIS METRIC |h_long - true_baseline|:")
    print(f"  TARGETED: {statistics.mean(tgaps):.4f} (std {statistics.pstdev(tgaps):.4f})   SHUFFLED: {statistics.mean(sgaps):.4f} (std {statistics.pstdev(sgaps):.4f})")
    print(f"  Paired diff (targeted-shuffled): {dm:+.4f} (std {dsd:.4f})  ")
    print(f"  Paired-t statistic: {paired_t:.3f}")
