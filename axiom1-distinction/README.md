# RGH Axiom 1 (Distinction): Simulation Findings

**Status: Preliminary, single-substrate evidence chain. Not peer reviewed. Scope strictly limited to Axiom 1 — see final section for what this does NOT establish.**

---

## 1. Claim under test

RGH's Axiom 1 (Distinction) asserts that a system can spontaneously partition undifferentiated potential into "A vs. ¬A" — that structure and boundary can self-generate from a uniform substrate, without external coordination or design.

This document reports a five-stage simulation chain testing a narrow, falsifiable version of that claim on a single substrate: the Gray-Scott reaction-diffusion system. The chain moves from validating the substrate, to testing spontaneous ignition from unstructured noise, to testing what noise properties matter, to measuring whether the resulting structures are genuine causal partitions rather than just visual patterns.

## 2. Method summary

**Substrate.** Gray-Scott reaction-diffusion: two coupled chemical fields *U*, *V* on a 100×100 toroidal grid, evolving under the standard equations (∂U/∂t = D_u∇²U − UV² + F(1−U), ∂V/∂t = D_v∇²V + UV² − (F+k)V), with parameters (Du=0.16, Dv=0.08, F=0.035, k=0.065) matching the documented "spots" regime (Pearson, 1993). This is a well-established model, not a novel mechanism — used here specifically so results could be checked against known behavior.

**Validation (Stage 1).** Implementation confirmed against the standard hand-seeded demonstration: a small central patch of elevated *V* grown from a documented seed radius reproduced sustained, growing spot structure over 6,000 steps, matching textbook Gray-Scott behavior. An initial bug (seed radius too small) was caught and corrected at this stage, before any substantive test was run.

## 3. Findings

### 3.1 Ignition from unstructured noise (Stage 2)

Starting from a genuinely uniform initial condition (U=1, V=0 everywhere) plus only small Gaussian noise — no hand-placed shape, no external design — the system was run for 8,000 steps.

**Result: pure additive white noise at low amplitude (0.01) failed to ignite any structure.** V decayed to exactly zero. This is a real property of Gray-Scott, not a failure of the test: the reaction term is quadratic in V, so infinitesimal perturbations decay back to the trivial fixed point rather than growing (a subcritical instability, not a simple linear one).

### 3.2 Amplitude threshold (Stage 2, continued)

A sweep of noise amplitudes (0.01 to 0.30) found a real, narrow, **non-monotonic ignition window**:

| Noise amplitude | Outcome |
|---|---|
| 0.01 – 0.10 | No ignition (decays to zero) |
| 0.15 | **Ignites** — sustained growth (final std ~ 0.11) |
| 0.20 | Partial/marginal ignition |
| 0.25 – 0.30 | No ignition |

**Honest caveat:** noise at amplitude 0.15 is a substantial fraction of the field's dynamic range — not "microscopic" in the sense the original Axiom 1 framing invoked. This test shows self-ignition from *sufficiently large, unstructured* perturbation is possible without any designed shape, but does not show arbitrarily small noise suffices.

### 3.3 Noise character: amplitude on U doesn't matter (Stage 3)

Varying the *character* of noise applied to U (purely additive vs. concentration-scaled/multiplicative, at relative amplitudes from 0.01 to 0.20) produced **no meaningful difference** in ignition outcome or final pattern statistics, at any tested V-seed amplitude. The ignition threshold found in 3.2 was reproduced exactly under this different noise model on U, confirming that V's seed amplitude — not U's noise character — is the operative variable.

### 3.4 Spatial correlation lowers the effective threshold (Stage 4)

Testing **spatially correlated** noise on V (Gaussian-blurred noise, rescaled to match the standard deviation of an equivalent white-noise field, isolating correlation structure from amplitude) against white noise at matched amplitude:

| Amplitude | White noise | Correlated (len 1-2) | Correlated (len 8) |
|---|---|---|---|
| 0.08 | No ignition | **Ignites** (std ~ 0.11) | No ignition |
| 0.10 | Marginal | **Ignites** (std ~ 0.11-0.12) | No ignition |
| 0.12 | Marginal | **Ignites** (std ~ 0.11) | No ignition |

**Finding:** noise correlated at a length scale (1-2 grid cells) close to the system's own natural pattern wavelength ignites reliably at amplitudes where white noise fails or is marginal. Correlation length far above that scale (8 cells) fails outright at every amplitude tested — behaving more like a single large offset than genuine local structure.

**Interpretation, stated at the strength it earns:** distinction is easier to self-generate from noise that has *some* spatial coherence at roughly the scale the underlying dynamics prefer, than from purely white noise. This is a real, mechanistically sensible refinement — but it is a narrower and more specific claim than "any microscopic noise suffices." It has not been established that the specific correlation lengths tested here generalize beyond resonance with this system's own diffusion-set wavelength.

### 3.5 Emergent boundaries show genuine causal insulation (Stage 5)

Using the strongest-igniting condition (amplitude 0.10, correlation length 1.0), the resulting pattern (61 discrete, connected spot structures, confirmed via connected-component labeling — not a diffuse blob) was tested for **causal insulation** across its self-generated boundaries, using time-lagged (lag=1) mutual information between adjacent-cell V-trajectories.

Cell pairs were classified into three categories: INTERIOR (both cells inside a spot), BOUNDARY (one cell inside a spot, adjacent cell in background), BACKGROUND (both cells far — >=3 cells — from any spot).

| Category | Mean MI (bootstrap-stable) |
|---|---|
| INTERIOR | 0.442 |
| **BOUNDARY** | **0.230** |
| BACKGROUND | 0.532 |

Bootstrap resampling (20 trials, 300 pairs each) confirmed this is a stable, non-noise result: paired t-statistics of 22.4 (Interior vs. Boundary) and 43.2 (Background vs. Boundary).

**Finding: boundary cells show roughly half the information coupling of interior cells.** This is a genuine information-theoretic signature of a causal partition, not merely a visual or statistical one — the system's self-generated boundary corresponds to a measurable reduction in predictive coupling exactly where the boundary sits.

**Honest caveat:** BACKGROUND showed the *highest* MI of the three categories, higher than INTERIOR — plausibly an artifact of the histogram-based MI estimator on low-variance, near-zero signals (two quiet trajectories both sitting near a floor value can appear highly "coupled" under binned MI without genuine dynamic information transfer). This oddity does not undermine the central BOUNDARY vs. INTERIOR comparison, which is the direct test of the causal-insulation claim, but it means the three-way ordering should not be over-interpreted as a clean monotonic story.

### 3.6 Extension: the same test on the Game-of-Life substrate (see `gol_substrate_extension/`)

Every result above was built on Gray-Scott — a continuous-field substrate, separate from the discrete Game-of-Life substrate the rest of this project (Persistence, Exploitation/Adaptation, Loop Closure) actually runs on. A follow-up, documented in `gol_substrate_extension/`, ran the same ignition-threshold and causal-insulation methodology directly on Game of Life, closing that substrate gap. Summary: a real, sharp, monotonic ignition threshold (density ~0.05-0.08), and — restricted to the subset (~10%) of outcomes that retain genuine dynamic content after settling, since fully static remnants are trivially untestable — a clean, unanimous (8/8 seeds) causal-insulation result, cleaner in ordering than the Gray-Scott version. See that folder's README for full detail and scope limits.

## 4. What this establishes

Across five stages, with one bug caught and corrected before results were trusted, and one internal caveat (background MI) surfaced rather than smoothed over:

- Structure can self-generate from unstructured (though not arbitrarily small) noise, with no external design — confirmed.
- The relevant lever is the amplitude and spatial correlation of the reactive species' own noise, not the character of noise in the background field — confirmed.
- Physically-motivated noise (spatially correlated, as any real continuous medium would produce) ignites structure at lower amplitude than idealized white noise — confirmed, with the caveat that "physically motivated" here means "correlated near the system's own pattern scale," not a general claim about arbitrary correlation lengths.
- The resulting structures are genuine causal partitions, evidenced by reduced information coupling across their boundaries relative to their interiors — confirmed, with a noted estimator caveat on the background comparison.

This is, to date, the cleanest positive result in the RGH simulation project.

## 5. What this does NOT establish — scope limits

This document reports results on **Axiom 1 only**, on **one substrate** (Gray-Scott reaction-diffusion), from **one instance** of pattern formation, not a recursive process.

Explicitly out of scope:

- **Axioms 2 and 3 (Transformation, Persistence) as RGH frames them.** See the dedicated Axioms 2 & 3 findings document — the general phenomenon is well-supported, but RGH's active-filtering framing was tested and revised there; this document does not speak to that separately.
- **Exploitation/Adaptation (E/A).** See the dedicated E/A findings document. As of this writing, E/A has one genuine, controlled positive result (learned cooperative strategy provides real resilience advantage under environmental stress, on a substrate with real thermodynamic stakes) reached only after five prior negative attempts. This document does not test E/A and should not be read as bearing on its status either way.
- **The recursive loop.** RGH's core formula posits repeated composition (R^infinity) with reflexive self-modeling above a complexity threshold. This document tests a single instance of Distinction; it does not test recursion, self-modeling, or the bifurcation-threshold hypothesis discussed earlier in this project.
- **Generalization beyond Gray-Scott.** Partially addressed — see Section 3.6 and `gol_substrate_extension/`, which replicates the causal-insulation methodology on a second, discrete substrate (Game of Life) with a positive, if smaller-sample, result. Generalization to substrates beyond these two remains untested.

## 6. Suggested next steps, if continuing this line

1. Test whether the causal-insulation finding (3.5) replicates across multiple independent ignition seeds, not just the single strongest-igniting condition reported here.
2. Resolve the background-MI estimator caveat (try a non-binned MI estimator, e.g. k-nearest-neighbor based, to check whether the BACKGROUND > INTERIOR ordering survives a different estimation method).
3. If E/A is revisited, any future substrate should have genuine conserved-quantity thermodynamics (as discussed separately), since every bit/pattern-level mechanism tested to date has failed to produce homeostasis.
