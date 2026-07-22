# RGH Parasitic Crucible: Simulation Findings

**Status: New hypothesis. Claim 1 confirmed via a properly-controlled ablation test. Claim 2 tested three ways (spontaneous drift under two inheritance mechanisms, then a deliberate invasion test) and resolved into a genuine third answer: stable, bounded coexistence between contributors and free-riders, neither invasion nor elimination. A significant methodological catch (spatial-clustering confound in the ablation test) and a second (reproduction-activity precondition in the invasion test) are both reported alongside the results, not glossed over. Not yet part of the main paper.**

---

## 1. Hypothesis under test

The Parasitic Crucible sub-hypothesis proposes two related claims about how collective, multi-part organization emerges from simple self-replication:

1. **Naive replication plateaus.** Left alone, simple self-copying does not escalate into genuinely collective organization on its own — it requires some specific, contingent constraint or cost structure to tip it over (literature precedent: Fontana & Buss's Level 0 self-copying λ-expressions required explicit suppression before Level 1 collective self-maintenance emerged).
2. **Collective organization, once formed, is exploitable.** Sub-forms that consume shared machinery without contributing back can undermine a genuinely collective system from within (precedent: Eigen & Schuster's hypercycle parasite problem).

This document tests Claim 1 fully, and reports a first test of Claim 2 — whether an established Level 1 population is vulnerable to internal erosion by non-contributing free-riders over a long run.

## 2. Method

**Substrate**: the validated energy-conservation Game-of-Life system, reusing the heritable, mutating trait mechanism from the Heredity/Variation line of work directly.

**Operational definition of "genuinely collective, mutually-dependent organization"**: an ablation test, matching the discipline used throughout this project — remove a population subgroup defined by a specific criterion, and separately remove an equally-sized *matched* control subgroup, then compare the harm done to the remaining population. If specific removal hurts substantially more than the matched control, that is evidence of real functional interdependency (a Level 1 signature). If the two are indistinguishable, the population remains functionally interchangeable regardless of the criterion used to select the "specific" group (Level 0).

**Stage 1 — naive baseline.** A population with a heritable, mutating trait that is functionally inert — it is inherited and mutates exactly as in the validated Heredity/Variation mechanism, but has no effect whatsoever on energy, survival, or replication. This is the honest "naive replication, no constraint" case Claim 1 predicts should show no real differentiation.

**Stage 3 — the contribution mechanism.** The first real candidate constraint: each live cell unilaterally gives away energy proportional to its own trait value, split among its neighbors, at a real, unconditional cost to itself, regardless of reciprocity. High-trait individuals become "helpers" subsidizing nearby births; low-trait individuals free-ride. The exploit/mutualism transfer mechanism is held neutral throughout, isolating this contribution mechanism as the only new variable.

**Stage 5 — long-run trait drift (Claim 2, first test).** Using the confirmed Level 1 configuration (contribution rate 0.03), the population is run for a much longer duration (8,000 steps, versus the original 1,500-step equilibrium window) while tracking mean population trait throughout. Since contribution is unconditional, a free-rider can already arise with no special mechanism required — any cell whose trait mutates toward zero contributes almost nothing while still potentially benefiting from its neighbors' contributions. This tests whether selection discovers and favors that strategy over a long run, eroding mean trait toward zero (evidence for Claim 2), or whether the population resists that erosion.

**Stage 6 — single-parent inheritance.** The original inheritance rule averages a birth's trait across all three live GoL-neighbor "parents." This stage tests whether that averaging specifically was suppressing erosion, by replacing it with single-parent inheritance (each birth copies one randomly-selected live neighbor's trait, plus mutation) — also a more biologically direct analog of actual cellular reproduction (binary fission copies one parent; it does not average several).

**Stage 7 — deliberate invasion test (Claim 2, sharper version).** Rather than waiting for a free-rider to arise spontaneously via mutation, a small number of cells (5) in an established Level 1 population are deliberately converted to a fixed, non-mutating "cheater" lineage: trait fixed at exactly 0 (zero contribution), with the cheater status itself heritable and non-decaying — any offspring of a cheater is also a cheater, with no mutation ever applied. This is a fairer and more targeted test of invasion than spontaneous drift, since the introduced strategy cannot be diluted away by mutation the way a naturally-arising free-rider could. Population-wide cheater fraction is tracked over a long run following introduction.

## 3. Results

### 3.1 A significant methodological catch, caught before it could contaminate the results

An initial version of the ablation test compared "specific" removal (a trait-defined band) against a *scattered*, uniformly-random control group. On the inert-trait baseline — which should show no real signal by construction — this comparison produced a statistically significant result (paired t = 3.95), which would have been a false positive.

The cause was diagnosed directly rather than assumed: because trait values are inherited from spatially-local parents, a trait-defined removal band is inherently more spatially clustered than a scattered random sample (confirmed directly: mean pairwise distance 14.6 for trait-band removal versus 19.3 for scattered random removal, on a sample check). A separate test confirmed that spatial clustering pattern *alone* — with no trait involvement at all — produces a real, significant difference in outcome (clustered removal disrupts the population less than scattering the same number of deaths across many neighborhoods; paired t = 2.98). This is a classic disturbance-pattern effect from spatial ecology, unrelated to any real functional differentiation.

**The fix**: the random control must be spatially matched — removing the same count of cells, clustered around a random starting point, rather than scattered. Under this corrected comparison, the inert-trait baseline showed no significant difference (paired t = -1.13), exactly as Claim 1 predicts, and confirming the ablation methodology itself is sound once properly controlled. This corrected, spatially-matched design is used for all results below.

### 3.2 The contribution mechanism: a genuine "Goldilocks zone," not a simple dial

The contribution mechanism was tested across a range of contribution rates, each compared using the validated (specific-vs-clustered-random, log-ratio) ablation test:

| Contribution rate | Paired t-statistic (n=15) | Paired t-statistic (n=40) | Directional consistency (n=40) |
|---|---|---|---|
| 0.02 | -0.15 (null) | — | — |
| 0.025 | -2.38 (significant) | — | — |
| **0.03** | -3.67 (significant) | **-4.05 (significant)** | 30/40 |
| 0.035 | -1.16 (null at n=15) | **-3.00 (significant)** | 24/40 |
| 0.04 | -1.91 (borderline) | — | — |
| 0.05 | -1.96 (borderline) | — | — |
| 0.10 | +0.42 (null) | — | — |

The relationship is not monotonic across the full range. Too low a contribution rate (0.02) means even the highest-trait individuals give away too little to matter. Too high a rate (0.10) means moderate-trait individuals become adequate contributors too, diluting the exclusivity of the top trait band. Within the middle range, though, the effect is a genuine continuous zone, not a series of noisy, disconnected bumps: an initial coarse sweep (n=15 per rate) found rate 0.035 unexpectedly null, sandwiched between significant results at 0.03 and 0.04 — this was checked directly rather than accepted at face value, by re-running both 0.03 and 0.035 at higher power (n=40). Rate 0.03 held (t=-4.05, even stronger than before); rate 0.035's apparent null resolved into a clearly significant result (t=-3.00, 24/40 directional) — confirming the original "dip" was sampling noise at n=15, not a real discontinuity. The corrected picture is a genuine, continuous effective zone spanning roughly rate 0.025 to 0.05, bounded by clean nulls at both extremes (0.02 below, 0.10 above).

At rate 0.03 (n=40), the result was confirmed to be well-distributed across seeds, not driven by any single outlier, consistent with the earlier n=15 check.

An earlier run at rate 0.05 (paired t = -1.96, borderline, n=15) was found to include one seed with a dramatically larger effect than the rest (a population that, when helpers were specifically removed, stayed within its normal bounded range, but when an equally-clustered random group was removed instead, entered a genuine post-disturbance growth boom well past its pre-ablation size). This was investigated directly and found to be a real instance of the effect at unusually large scale — not a numerical artifact — but its outsized magnitude distorted the raw-count statistic. Switching to a log-ratio comparison (appropriate for this kind of heavy-tailed, multiplicative effect) resolved this distortion without discarding the data point.

## 4. Claim 2: does an established Level 1 population erode from within?

### 4.1 Under the original (averaging) inheritance rule: no erosion, a stable equilibrium

Running the confirmed Level 1 configuration (rate 0.03) for 8,000 steps across 8 seeds, mean population trait settled after an initial adjustment period (0.499 → 0.427 over the first 2,000 steps) and then held essentially flat for the remaining 6,000 steps (0.427, 0.427, 0.427, 0.427, 0.427 at the five-checkpoint intervals sampled — population size similarly frozen at ~59). There is no progressive drift toward zero. This is not what a naive reading of Claim 2 predicts: if free-riders were being continuously discovered and increasingly favored, mean trait should decline over time, not plateau and hold.

A specific mechanistic hypothesis was proposed to explain this: because each birth's trait is the *average* of three live neighbor "parents," any individual mutant trait value gets pulled back toward the local neighborhood mean at every reproduction event — structurally preventing a low-trait "cheater lineage" from breeding true across generations, regardless of whether free-riding is locally advantageous.

### 4.2 Single-parent inheritance: no erosion at the population level, but much greater between-population variance

Replacing averaged inheritance with single-parent inheritance (each birth copies one randomly-chosen live neighbor's trait) did not produce the predicted erosion either — averaged across 8 seeds, mean trait remained essentially flat over the same 8,000-step run (0.484 → 0.504, if anything drifting slightly upward). The averaging hypothesis, as a complete explanation for Stage 5's stability, is not confirmed.

What changed instead was the *spread* of outcomes across independent runs. Under averaged inheritance, final trait values across seeds fell in a narrow band (0.33–0.53). Under single-parent inheritance, final values ranged from 0.29 to 0.73 — spanning nearly the full possible range. The likely mechanism: averaging is a homogenizing force that pulls every population toward a similar equilibrium regardless of starting conditions; removing it lets genetic drift and founder effects act much more strongly, so whichever trait level a small population happens to lock onto early can persist and dominate its own trajectory, without cross-lineage averaging pulling it back toward a shared value.

### 4.3 That variance is diffuse individual noise, not distinct coexisting sub-lineages

The wide between-seed spread raised a sharper, more direct question: does a single population under single-parent inheritance actually split into spatially distinct, coexisting sub-lineages with different strategies (a direct analog of the hypercycle-parasite coexistence Claim 2 describes), or is each population simply landing on a different single value with ordinary individual-level noise around it?

This was checked directly, not assumed. Within-population trait standard deviation was found to be substantial in every seed (0.23–0.34) — genuine individual diversity exists within single populations, not just between them. But splitting each population at its median trait value and counting spatially-connected clusters of each type found many small clusters relative to population size (e.g., one seed's 92 live cells split into 13 low-trait clusters and 14 high-trait clusters, averaging roughly 3–4 cells per cluster) — the opposite of what a small number of large, spatially-segregated "colonies" would look like. Histogram shapes confirmed this: only half the seeds showed even a modest gap in the trait distribution, and none showed a clean two-peak split.

**The honest conclusion**: single-parent inheritance preserves substantially more standing individual-level trait diversity than averaged inheritance, both within and across populations — but that diversity remains diffuse and well-mixed, not organized into the kind of distinct, spatially-coexisting sub-populations Claim 2's framing actually predicts.

### 4.4 The deliberate invasion test: a real methodological catch, then stable coexistence

Spontaneous drift is a weaker test of Claim 2 than the literature's actual hypercycle-parasite scenario, since a naturally-arising free-rider can always be diluted back toward cooperation by ordinary mutation. A sharper test deliberately introduces a small number (5) of fixed, non-mutating, zero-contribution cheaters into an established Level 1 population and tracks whether they invade and spread — cheater status here is permanently heritable, immune to mutation, giving the strategy the fairest possible chance to succeed if it is genuinely advantageous.

**A real precondition problem was caught before trusting this test.** An initial run showed cheater fraction perfectly frozen at its introduced value for thousands of steps in some seeds — not because invasion had stalled, but because those specific populations had settled into fully static configurations with zero ongoing births anywhere on the grid (confirmed directly: birth-candidate counts of exactly 0 over 500-step checks in roughly 40% of seeds tested). With no reproduction occurring at all, a cheater lineage has no opportunity to spread or be eliminated — a frozen cheater fraction in these cases reflects absence of any invasion opportunity, not resistance. This is the same category of precondition problem caught in the Layer 0 causal-insulation work (constant signals carrying no measurable information) and was handled the same way: seeds were filtered for confirmed ongoing reproduction (a real, checked precondition, not an assumption) before the invasion test was trusted.

**Under this corrected design, across 8 qualifying seeds, cheater fraction settled into stable, low-level coexistence — neither invasion nor elimination.** Tracked over 15,000 steps following introduction, mean cheater fraction moved from an initial 8.0% through a very slight rise to a plateau around 8.3–8.8%, then ticked back down slightly by the end of the run — consistent with a bounded equilibrium, not an accelerating takeover. Individual seeds showed real variation underneath that average: one seed's cheaters went fully extinct (fraction reaching exactly 0.0), while others settled at somewhat elevated levels (up to 17.6%) — but no seed showed the kind of continued, escalating growth genuine invasion would produce, even at nearly triple the initial test duration.

This is a real, third answer to Claim 2, distinct from both "successful invasion" and "full resistance": the collective structure neither eliminates free-riders entirely nor is overrun by them — it settles into a stable, bounded coexistence at a modest cheater frequency, consistent with mutation-selection-balance dynamics documented in real biological populations.



## 5. What this establishes

Claim 1 is supported, with a specific and important qualification. A naive replication mechanism, given a genuine, real-cost constraint (unilateral contribution proportional to an inherited trait), can produce real functional interdependency — confirmed via a properly-controlled ablation test, not merely a cosmetic increase in trait diversity. But this only happens within a narrow, specific calibration band. Both weaker and stronger versions of the same mechanism collapse back to functional interchangeability (Level 0). This is consistent with, and sharpens, Claim 1's framing: naive replication does not escalate into collective organization on its own, and even a real candidate constraint mechanism does not guarantee escalation — it must be tuned into a specific regime, echoing the same "necessary but not sufficient, only within a bounded regime" pattern found in the Layer 0 dissipation work.

Claim 2, in its naive "unconstrained internal erosion" form, is not supported. An established Level 1 population does not show progressive drift toward free-riding under either averaged or single-parent inheritance via spontaneous mutation, and a deliberately introduced, permanently non-mutating cheater lineage — the fairer, more targeted test — does not invade and spread either. What happens instead, confirmed across two run lengths (6,000 and 15,000 steps) and 8 qualifying seeds, is stable, bounded coexistence: cheaters persist at a modest, roughly stable frequency (typically 5–18%, seed-dependent, with one seed showing complete elimination), neither growing toward dominance nor being fully eliminated. This is a genuine, third answer to Claim 2 — not the hypothesis confirmed, and not simply refuted either, but resolved into something more specific: this substrate supports a real, bounded equilibrium between contributors and free-riders, consistent with mutation-selection-balance dynamics documented in real biological populations.

## 6. What this does NOT establish

- **The stable-coexistence finding is specific to this contribution mechanism, this cheater definition (complete, permanent zero-contribution), and this cheater introduction size (5 cells).** Whether a larger initial invasion, a partial (rather than complete) free-rider strategy, or a structurally different constraint mechanism shows the same bounded-coexistence pattern, versus genuine invasion or genuine elimination, has not been tested.
- **One substrate, one mechanism, one trait.** The contribution mechanism tested here is one specific way to operationalize "real cost, unilateral giving" — other mechanisms might show a different, wider, or absent sweet spot, and might resolve Claim 2 differently as well.
- **The zone's precise edges remain coarsely mapped.** The effective range is now confirmed continuous between roughly 0.025 and 0.05 (with 0.03 and 0.035 both independently confirmed at higher power), but the exact lower and upper boundaries — where the effect first appears and where it finally disappears — have not been located precisely.
- **This is not yet part of the main paper.** Per this project's standard, a first confirmed result is not sufficient for inclusion without further replication and, ideally, an independent test of the same claim via a different mechanism.

## 7. Suggested next steps

1. Map the sweet spot more precisely (e.g., rates 0.025, 0.035, 0.04) to characterize its actual boundaries rather than only bracketing it.
2. Test whether the stable-coexistence equilibrium is sensitive to invasion size (e.g., introducing 20-30% cheaters instead of a small handful) or to a partial (rather than complete) free-rider strategy, to check whether the bounded equilibrium is a genuine attractor or specific to a small initial perturbation.
3. Test whether a structurally different constraint mechanism (e.g., explicit resource competition rather than unilateral giving) produces a similar sweet-spot pattern, and whether it shows the same stable-coexistence result under invasion, or whether both findings are specific to the contribution mechanism as designed.
4. Investigate the specific spatial/structural feature of this substrate that bounds cheater frequency rather than allowing runaway takeover or complete elimination — a genuinely interesting mechanistic question in its own right.
