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
| **Axiom 1 (Distinction)** | Supported on Gray-Scott (causal insulation confirmed), and now replicated on the Game-of-Life substrate itself (8/8 seeds, unanimous direction) — see `axiom1-distinction/gol_substrate_extension/` |
| **Axiom 2 (Transformation)** | Framework choice, not a finding |
| **Axiom 3 (Persistence)** | General phenomenon supported (prior CA theory). Active-filtering, tried three ways, never showed a benefit from "smart" targeting. Reframed and resolved: persistence emerges as differential survival with *no* active operator at all — see folder README, Section 3.4. |
| **Exploitation/Adaptation (E/A)** | Five nulls, then one controlled positive result under real thermodynamic stakes |
| **Loop Closure (D→T→P→E/A, one pipeline)** | Revised: the original "E/A adds complexity" result (5x population, 2x diversity) was largely an artifact of not separating Distinction from the metabolic collapse phase. Once corrected with a validated Distinction event, the effect collapses to statistical noise — see folder README for the full correction. |
| **Layer 0 (Entropic Substrate Hypothesis)** | New hypothesis. Structure requires genuine dissipative flux, not mere fluctuation — a clean 15-seed replication (paired t=769.5), refined into a sharper claim: dissipation is necessary but not sufficient, the system must also cross into a genuinely unstable (Turing) regime. Causal insulation confirmed at full strength, within the partial-dissipation unstable band, and under both dissipation-sourced and dissipation-independent ongoing noise. Extended to Persistence: Distinction requires dissipation outright, Persistence-by-attrition does not (dissipation sharpens it, as a threshold not a gradient). Extended to Transformation via a genuinely different mechanism (Landauer-gated execution, energy gates whether a proposed transition can even happen): sustained energetic demand depends on whether a rule permits a "no transition needed" state to exist — Game of Life and Day & Night both find one and stop demanding energy; Brian's Brain (mandatory multi-step transitions) never does, rising to the model's own mathematical ceiling. All three axioms now tested. Summarized in the main paper, Section 4.1. |
| **Layer 1 (Diffusion-Limited Energy Scarcity)** | New architecture — flat independent income replaced with a genuine shared, diffusing resource. Stage 1: all three rules tested (Brian's Brain, GoL, Day & Night) show a real interior complexity peak once each is calibrated near its own energetic threshold — an initial "rule-dependent" conclusion was caught and corrected via proper calibration. Stage 2: genuine competition (GoL vs. Brian's Brain, mutually blind, shared energy field) found the mandatory-cycling rule decisively wins territory in both scarcity regimes tested, contrary to the pre-registered hypothesis — and a follow-up "thermodynamic parasitism" hypothesis was proposed, directly tested, and rejected in favor of a more modest refuge-effect explanation. Both corrections preserved transparently in the write-up. Not yet part of the main paper. |
| **Heredity & Variation** | Real heredity (parent-average + mutation) was initially indistinguishable from random reassignment at every tested mutation size. A follow-up found this wasn't because heredity doesn't matter — very faithful heredity (low mutation) actually *underperforms* random reassignment under sudden stress (statistically real, z=-2.16). A well-powered (n=40) gradual-ramp test sharpened this into a bolder claim: even under slow, predictable change — where heredity should have the advantage — random reassignment still significantly beats it (z=-3.18), despite heredity genuinely, confirmedly tracking the change. Standing variation appears to dominate lineage-based tracking in both regimes tested, a real departure from the standard bet-hedging prediction. Summarized in the main paper, Section 4.2. |
| **Parasitic Crucible** | New hypothesis. Naive replication plateaus without a real cost constraint (confirmed via a properly-controlled ablation test — caught and fixed a spatial-clustering confound along the way). A specific "helper contribution" mechanism, tuned into a narrow rate band (~0.025–0.05), produces genuine functional interdependency. Claim 2 (parasitic exploitability) tested three ways — spontaneous drift under two inheritance mechanisms, then a deliberate invasion test — and resolved into a genuine third answer: stable, bounded coexistence between contributors and free-riders, neither invasion nor elimination. Summarized in the main paper, Section 4.3. |

See the paper linked above for the full reasoning behind each line, or the individual folder READMEs for full experimental detail.

## Folder structure

```
RGH_V1.3_Revised.md                  <- the full paper

axiom1-distinction/
  README.md                          <- includes reference to the GoL extension below
  stage1_grayscott.py                <- validated Gray-Scott substrate
  stage2_axiom1_test.py              <- ignition from uniform noise
  stage3_multiplicative_noise.py     <- noise-character test
  stage4_correlated_noise.py         <- spatial correlation test
  stage5_causal_insulation.py        <- transfer-entropy boundary test (Gray-Scott)
  gol_substrate_extension/           <- closes the Gray-Scott/GoL substrate gap
    README.md
    stage1_ignition_sweep.py         <- GoL's own ignition threshold (cleaner than Gray-Scott's)
    stage2_causal_insulation.py      <- same MI methodology, on GoL (8/8 seeds, unanimous)

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
  README.md                          <- REVISED: original result + corrected follow-up test
  stage9_loop_closure.py              <- original test (weak Distinction stand-in, superseded)
  gol_distinction_ignition.py         <- validated GoL ignition, reused from axiom1-distinction
  stage10_loop_closure_v2.py           <- corrected test (validated Distinction handoff)
  ea_stage3_memory_switching.py       <- reused, validated E/A mechanic
  stage6_component_memory.py          <- reused, validated component-size memory
  (+ shared dependency files, self-contained folder)

layer0-entropic-substrate/
  README.md                          <- Distinction + Persistence: dissipation requirement, noise-source resolution
  distinction/                        <- Gray-Scott based (all Distinction tests)
    stage1_basic_check.py, stage1_grayscott.py, stage2_full_mi_test.py,
    stage3_multiseed_replication.py, stage4_correlated_noise.py, stage4_dissipation_sweep.py,
    stage5_mi_partial_regime.py, stage6_noise_source_control.py, stage7_mi_noise_source.py
  persistence/                        <- energy-CA based (Persistence extension)
    stage1_salvageability_memory.py, stage6_component_memory.py,
    stage8_differential_survival.py, stage9_persistence_dissipation_test.py, vectorized_signature.py
  transformation/                     <- Landauer-gated execution (Transformation extension)
    README.md                        <- three rejected rule candidates, then the real result
    stage1_landauer_gate.py, stage2_chaotic_comparison.py, stage3_brians_brain.py

heredity-variation/
  README.md                          <- bet-hedging reframe: variation matters, not lineage transmission
  stage1_heredity_mechanism.py        <- inheritable, mutating exploit/mutualism trait
  stage2_heredity_stress_test.py      <- heritable vs fixed vs random-reassignment comparison
  stage3_mutation_sweep.py            <- mutation-size sweep + parent-offspring correlation diagnostic
  stage4_gradual_ramp.py              <- gradual ramp test: standing variation beats heredity even here
  (+ shared energy-CA dependency files)

parasitic-crucible/
  README.md                          <- naive-plateau + Level 1 interdependency + resolved Claim 2 (stable coexistence)
  stage1_naive_baseline.py            <- inert-trait baseline (Claim 1 control)
  stage2_ablation_test.py             <- ablation methodology + the spatial-clustering confound catch/fix
  stage3_contribution_mechanism.py    <- unilateral helper-contribution mechanism
  stage4_contribution_ablation.py     <- confirms Level 1 interdependency, maps the rate sweet spot
  stage5_long_run_drift.py            <- Claim 2: long-run trait stability (no spontaneous erosion)
  stage6_single_parent.py             <- single-parent inheritance variant + spatial diversity check
  stage7_invasion_test.py             <- deliberate invasion test: resolves into stable coexistence
  (+ shared energy-CA dependency files)

layer1-diffusive-scarcity/
  README.md                          <- corrected synthesis: universal peak + competition + rejected parasitism
  stage1_diffusive_brians_brain.py    <- diffusive Landauer gate, single rule (Brian's Brain), the real peak
  stage2_diffusive_rule_comparison.py <- same mechanism generalized to GoL/Day & Night, calibration correction
  stage2_gol_vs_brians_brain.py       <- genuine competition: mutually blind, coin-flip, boundary flux + refuge check

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
