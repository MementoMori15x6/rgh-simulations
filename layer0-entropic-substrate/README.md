# RGH Layer 0 (Entropic Substrate Hypothesis): Simulation Findings

**Status: New hypothesis. Core result (open vs. closed system) replicated cleanly across seeds and sharpened into a precise, mechanistically-grounded claim. A separate question — whether noise source matters, independent of system openness — has now also been tested: source affects aggregate structure substantially, but not the causal-insulation signature itself. Not yet part of the main paper — held to the same evidentiary bar as every other claim in this project.**

---

## 1. Hypothesis under test

The main paper's central conclusion is that Distinction, Transformation, and Persistence describe a recurring pattern in complex systems, but are not themselves a sufficient generative engine — every real effect found required some further, specific, contingent mechanism underneath. "Layer 0" is a candidate for what that underlying mechanism might be, at least in part: the proposal that genuine non-equilibrium thermodynamic flux (real, ongoing dissipation) is what actually drives Transformation, sieves Persistence, and may be required for Distinction's boundary formation in the first place.

This document tests the narrowest, most direct piece of that claim: **does the causal-insulation result already confirmed for Axiom 1 (Distinction) actually require genuine dissipative flux, or does any comparable fluctuation produce the same result regardless of whether the system is thermodynamically open or closed?**

## 2. Method

**Substrate**: the validated Gray-Scott reaction-diffusion system used for the original Axiom 1 result (Du=0.16, Dv=0.08), with the same ignition protocol (spatially-correlated noise, amplitude 0.10, correlation length 1.0).

**Core comparison**: Condition A (dissipative, F=0.035, k=0.065 — the validated "spots" regime) against Condition B (non-dissipative, F=0, k=0 — identical diffusion and reaction nonlinearity, but thermodynamically closed rather than open). A third condition, C, is the raw noise field before any dynamics run, for reference.

**Metric**: spatial variance of the field over time. An initial attempt to reuse the causal-insulation mutual-information test (validated for the original Axiom 1 result) on Condition B was found to produce a genuine estimator artifact — Condition B's field, once collapsed, undergoes smooth monotonic relaxation rather than genuine dynamic activity, which inflates mutual information under a histogram-based estimator without reflecting any real structure. This is documented as a real methodological boundary, not glossed over: the mutual-information test does not transfer meaningfully to a system in this regime, and spatial variance is the metric relied on throughout this document instead.

## 3. Results

### 3.1 Core comparison, replicated across 15 seeds

Condition A sustains real, growing structure (mean final V-field standard deviation 0.114, seed-to-seed variation tiny — pstdev 0.0005). Condition B collapses almost completely (mean final V-std 0.0009, pstdev 0.0002) — more uniform than the raw noise baseline it started from. Every one of 15 independent seeds showed A greater than B; the paired difference (0.113) is enormous relative to the seed-to-seed noise in either condition (paired t = 769.5). This is as clean a replication as any result in this project.

### 3.2 A sharper picture: dissipation is necessary but not sufficient

A follow-up swept the dissipation strength between the two extremes (scaling F and k together from 0 to full strength) to see whether structure degrades gradually or collapses at a sharp threshold. The result revealed three distinct regimes, not a simple two-state comparison:

- **No dissipation at all (scale 0)**: the field saturates to a high, uniform value (V≈0.95) — an unconstrained reaction runaway, since nothing removes V once produced.
- **Partial dissipation (scales 0.05 through 0.80)**: genuine, ongoing, non-zero dissipative throughput is present — F and k are both nonzero — yet the field still collapses to a uniform, non-trivial fixed point (V settling around 0.34 at scale 0.10, for example). Every one of these intermediate scales produced essentially zero spatial variance, with zero seed-to-seed variation, indicating a real, stable equilibrium rather than noise.
- **Sufficient dissipation (scales above roughly 0.80–0.85)**: real spatial structure emerges and grows smoothly with increasing scale, from V-std ≈ 0.075 at scale 0.85 up to ≈ 0.117 at scale 0.97, matching the full-strength result.

This means dissipation being present is not, by itself, sufficient for structure to form. A dissipative system can still relax to a uniform state if that state happens to be dynamically stable against spatial perturbation. What matters is whether the system's dissipative regime crosses into genuine spatial instability (a Turing bifurcation) — a real, sharp threshold in parameter space, not a smooth function of "how much" dissipation is present.

### 3.3 Causal insulation confirmed within the partial-dissipation regime, not just at full strength

The original causal-insulation test was only ever run at full dissipation strength. A follow-up applied the identical, validated mutual-information methodology at scale 0.90 — comfortably inside the newly-identified Turing-unstable band, but well short of full strength. The result matched: Interior MI (0.356) exceeded Boundary MI (0.162), a gap of +0.194 — nearly identical in size to the full-strength gap (+0.199). Fewer and smaller spots formed at this reduced strength (14 versus 61), consistent with weaker overall structure, but the causal-insulation signature itself — the thing Axiom 1 actually claims — held throughout. This closes the gap noted in the previous version of this document: partial dissipation, provided it is on the unstable side of the threshold, produces the same qualitative signature as full dissipation, not merely similar variance.

### 3.4 Noise source: substantial effect on aggregate structure, no effect on causal insulation itself

Every test above used noise only as a one-time initial perturbation, then let the system evolve deterministically. A separate question — flagged but untested in the earlier version of this document — is whether the *noise itself* needs to be dissipation-sourced, or whether any ongoing fluctuation suffices as long as the system remains thermodynamically open. This was tested directly: ongoing per-step noise was injected throughout the run (not just at ignition), on the same open, dissipative system (F=0.035, k=0.065, unchanged), comparing two sources at matched average amplitude — noise scaling with the local reaction rate (U·V², mimicking real molecular fluctuation, which physically scales with reaction throughput) against noise injected uniformly across the grid regardless of local activity.

The two sources produced substantially different aggregate outcomes. Across a sweep of noise budgets (0.01 to 0.1), dissipation-sourced noise consistently produced a much lower mean field level (e.g., 0.026 at budget 0.05) than dissipation-independent noise (0.193 at the same budget) — a 5- to 20-fold difference, holding across every budget tested. The mechanism is direct: dissipation-sourced noise is proportional to local reaction rate, which is near-zero in quiet background regions, so those regions are barely perturbed and stay quiet. Dissipation-independent noise perturbs the entire grid uniformly, including quiet regions — and because the underlying reaction is autocatalytic, uniformly kicking previously-quiet background triggers much more widespread secondary ignition, producing a far higher overall field level and more numerous spots (507 versus 122 at matched budget).

Despite this large difference in aggregate behavior, the causal-insulation signature itself was checked directly and found intact in both conditions: Interior MI exceeded Boundary MI by a similar margin under both dissipation-sourced noise (+0.033) and dissipation-independent noise (+0.027). (Background MI was elevated in both conditions, consistent with the same low-variance estimator artifact already documented for the original Axiom 1 result — this does not affect the Interior-versus-Boundary comparison, which is the test that actually bears on the causal-insulation claim.)

## 4. What this establishes

The core finding replicates cleanly and dramatically: removing dissipation entirely, while holding everything else constant, destroys structure rather than merely weakening it. The follow-up sweep sharpens this into a more precise and more defensible claim than "dissipation is required": **genuine non-equilibrium flux is necessary for this structure to form, but it must also put the system into a regime where its own dissipative equilibrium is unstable to perturbation — dissipation alone, without that instability, produces a different, merely uniform, dissipative state.** This is consistent with, and a real instance of, established dissipative-structure theory (Prigogine), which has always required both far-from-equilibrium driving and an instability mechanism together, not throughput in isolation.

The noise-source question is now resolved in favor of the weaker of the two candidate claims: **what matters is that the system is open and driven, not where the fluctuation specifically originates.** Noise source has a real, substantial effect on aggregate field statistics (overall activity level, number and density of structures), but the specific causal-insulation signature that defines genuine Distinction in this framework forms comparably under both dissipation-sourced and dissipation-independent noise, given the same open, dissipative system underneath.

## 5. What this does NOT establish

- **This tests only one narrow piece of Layer 0** — whether Distinction's causal-insulation result requires dissipation. It says nothing yet about Transformation or Persistence, which the broader Layer 0 proposal also claims depend on this same substrate.
- **One substrate (Gray-Scott), one ignition protocol.** The dissipation-scaling sweep held F:k ratio fixed while scaling both together; a different scaling path through parameter space (e.g., varying F and k independently) might reveal a different-shaped boundary.
- **The partial-regime causal-insulation confirmation rests on a single seed**, unlike the full-strength result, which was validated with bootstrap resampling across multiple samples. The direction and magnitude match closely enough to be reported with confidence, but a multi-seed replication of this specific check has not been run.
- **The noise-source test also rests on a single seed per condition**, at one calibration (budget 0.05) chosen because both conditions showed non-degenerate structure there. A multi-seed replication, and a check across other budgets, would strengthen this result the same way Section 3.1's multi-seed replication strengthened the core comparison.
- **The background-MI artifact, already flagged for the original Axiom 1 result, reappears here** and is more pronounced under dissipation-sourced noise specifically (since it leaves background regions especially quiet) — this affects only the Background comparison, not the Interior-versus-Boundary test the conclusion rests on, but is worth keeping in mind for any follow-up using this metric.
- **This is not yet part of the main paper.** A second, independent line of evidence (e.g., testing whether the same open/closed distinction matters for Persistence or Transformation) would be a reasonable bar before folding this into the framework's supported claims.

## 6. Suggested next steps

1. Map the instability boundary more precisely (e.g., scales 0.80–0.85 in finer steps) to characterize the bifurcation itself, rather than only bracketing it.
2. Replicate the noise-source result (Section 3.4) across multiple seeds and additional noise budgets, to confirm the Interior-Boundary gap's stability holds as robustly as the core open-vs-closed comparison does.
3. Test whether the same open-vs-closed, sufficient-vs-insufficient-dissipation distinction matters for the Persistence and Transformation lines of work, not just Distinction.
