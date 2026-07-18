# RGH Simulations

Simulation-based testing of the Recursive Genesis Hypothesis (RGH) — a speculative cosmological framework built on three axioms (Distinction, Transformation, Persistence) plus an Exploitation/Adaptation (E/A) mechanism, all read through the compact formula:

```
S_{t+1} = R(S_t) = P o A o E o T o D(S_t)
```

This repo contains the actual code behind three findings documents. Each folder is self-contained with its own README (the full findings writeup) and the scripts that produced the reported numbers.

## Status at a glance

| Component | Status |
|---|---|
| **Axiom 1 (Distinction)** | Supported — spontaneous, self-generated boundary formation confirmed both structurally and via a genuine information-theoretic causal-insulation test. See `axiom1-distinction/README.md`. |
| **Axioms 2 & 3 (Transformation, Persistence)** | T is a framework choice, not a finding. P's general phenomenon (fixed rule -> enduring structure) is well-supported by 80 years of prior CA theory. RGH's *stronger* claim (active filtering against entropy) remains untested in one sense and *actively contradicted* in another — our own persistence filter, once finally given real teeth, made things die faster, not slower. See `axioms2-3-transformation-persistence/README.md`. |
| **Exploitation/Adaptation (E/A)** | Five null/negative results on ungrounded (bit- or pattern-level) mechanisms, followed by one real, controlled positive result once a substrate with genuine conserved-energy thermodynamics was built: populations that learn to prefer mutualism over exploitation, based on real per-neighbor outcome tracking, show survival resilience matching populations that were cooperative from the start — far exceeding both fixed exploitation and unlearned random strategy-switching. See `ea-mutualism/README.md`. |

## Folder structure

```
axiom1-distinction/
  README.md                          <- full findings writeup
  stage1_grayscott.py                <- validated Gray-Scott substrate
  stage2_axiom1_test.py              <- ignition from uniform noise
  stage3_multiplicative_noise.py     <- noise-character test
  stage4_correlated_noise.py         <- spatial correlation test
  stage5_causal_insulation.py        <- transfer-entropy boundary test

axioms2-3-transformation-persistence/
  README.md
  gol_substrate_validation.py        <- GoL sanity check (blinker, glider)
  entropic_decay_lifespan_test.py    <- the first P-with-real-teeth test (negative result)

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
