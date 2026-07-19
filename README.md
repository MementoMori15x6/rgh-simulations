# RGH Simulations

Simulation-based testing of the Recursive Genesis Hypothesis (RGH) — a speculative cosmological framework built on three axioms (Distinction, Transformation, Persistence) plus an Exploitation/Adaptation (E/A) mechanism, all read through the compact formula:

```
S_{t+1} = R(S_t) = P o A o E o T o D(S_t)
```

**Full paper, with inline empirical-status notes for every axiom: [RGH_V1.3_Revised.md](https://github.com/MementoMori15x6/rgh-simulations/blob/main/RGH_V1.3_Revised.md)**

This repo contains the actual code behind that paper's findings. Each folder below is self-contained with its own README (the full findings writeup for that line of testing) and the scripts that produced the reported numbers.

## Status at a glance

| Component | Status |
|---|---|
| **Axiom 1 (Distinction)** | Supported |
| **Axiom 2 (Transformation)** | Framework choice, not a finding |
| **Axiom 3 (Persistence)** | General phenomenon supported (prior CA theory). Active-filtering, tried three ways, never showed a benefit from "smart" targeting. Reframed and resolved: persistence emerges as differential survival with *no* active operator at all — see folder README, Section 3.4. |
| **Exploitation/Adaptation (E/A)** | Five nulls, then one controlled positive result under real thermodynamic stakes |
| **Loop Closure (D→T→P→E/A, one pipeline)** | E/A layered on top of pure persistence sustains ~5x the population and ~2x the structural diversity, with no significant cost to robustness (n=15, paired t=10.2 and 4.5) — first cross-axiom result in this project |

See the paper linked above for the full reasoning behind each line, or the individual folder READMEs for full experimental detail.

## Folder structure

```
RGH_V1.3_Revised.md                  <- the full paper

axiom1-distinction/
  README.md                          <- full findings writeup
  stage1_grayscott.py                <- validated Gray-Scott substrate
  stage2_axiom1_test.py              <- ignition from uniform noise
  stage3_multiplicative_noise.py     <- noise-character test
  stage4_correlated_noise.py         <- spatial correlation test
  stage5_causal_insulation.py        <- transfer-entropy boundary test

axioms2-3-transformation-persistence/
  README.md                          <- revised: full active-filter history + differential-survival resolution
  gol_substrate_validation.py        <- GoL sanity check (blinker, glider)
  entropic_decay_lifespan_test.py    <- crude filter attempt (backfired, negative result)
  smart_filter_attempt_bare_gol/     <- superseded design (local-signature, low-neighbor-count candidates)
    vectorized_signature.py
    stage1_fast.py
    stage2_smart_filter_test.py
  damage_repair_and_differential_survival/   <- the complete, final line of testing
    stage1_energy_baseline.py
    stage1_salvageability_memory.py
    stage2_damage_repair.py
    stage3_stress_test.py
    stage4_triage.py
    stage5_final_calibrated.py       <- the properly-powered (n=50) local-signature result
    stage6_component_memory.py
    stage7_component_test.py
    stage8_differential_survival.py  <- the key result: persistence with zero active operator

loop-closure/
  README.md                          <- first cross-axiom test: D (weak)->T->P->E/A in one pipeline
  stage9_loop_closure.py              <- control (T+attrition) vs treatment (T+attrition+E/A)
  ea_stage3_memory_switching.py       <- reused, validated E/A mechanic
  stage6_component_memory.py          <- reused, validated component-size memory
  (+ shared dependency files, self-contained folder)

ea-mutualism/
  README.md
  stage1_energy_baseline.py          <- energy-conservation GoL, calibrated
  stage1b_robustness_check.py        <- 20-seed robustness check
  stage2_exploit_mutualism_mechanic.py       <- ORIGINAL (has a sign bug, kept for the record)
  stage2b_exploit_mutualism_SIGN_FIXED.py    <- corrected version, used in all later results
  stage3_memory_switching_stress_test.py     <- the key result: memory-based switching vs. controls
  legacy-null-attempts/
    01_1d_bitflip_null.py
    02_1d_temporal_repair_null.py
    03_1d_dual_repair_null.py
    04_1d_rule_override_null.py
    05_2d_gol_pattern_persistence_null.py
```

## Why the null results and bugs are kept, not deleted

This project's actual evidentiary path included real dead ends and real bugs — a metabolic cost parameter that turned out to be empirically inert, an exploitation mechanic with an inverted sign error, five different repair mechanisms that failed to produce homeostasis before one, built on a fundamentally different (energy-grounded) substrate, finally worked. Those are kept here deliberately. A repo that only showed the final, working version would misrepresent how much of this took real iteration, and would hide exactly the kind of self-correction (catching a sign error, catching a density-selection confound, catching an inert parameter) that makes the final positive results trustworthy rather than convenient.

## Caveats that apply project-wide

- All of this is unpublished, not peer-reviewed, and produced through iterative human-AI collaboration rather than formal research methodology.
- Every "positive" result here has been checked against at least one plausible alternative explanation (a matched null, a density-control, a random-preference control) — but that does not make any of it settled science. Treat each README's own "what this does NOT establish" section as load-bearing, not boilerplate.
- Nothing here validates RGH's full recursive loop, reflexive self-modeling (`M`), or the bifurcation-threshold hypothesis discussed during the project but never directly tested.
