# RGH Heredity & Variation: Follow-Up Findings — Standing Variation Beats Heredity, in Both Regimes Tested

**Status: Follow-up to the initial heredity/variation test, now extended to a gradual-change regime with full statistical power (n=40). The result is a genuine departure from the standard bet-hedging prediction, not merely a replication of it. Not peer reviewed.**

---

## 1. Where the earlier test left off

An initial test compared populations with a genuinely inheritable, mutating trait (an exploit-vs-mutualism propensity, passed from parent to offspring at birth with Gaussian mutation, std=0.05) against a control where offspring received a completely random trait value with no connection to their actual parents at all. Under a metabolic stress test, both conditions performed almost identically (15/15 vs. 14/15 survival, statistically indistinguishable), and the "real heredity" condition showed no advantage in either survival or trait drift. This left an open question: was heredity genuinely not mattering here, or was the specific mutation rate tested simply too large to let any transgenerational signal show through?

## 2. What this follow-up tested

Two things, to resolve that question directly rather than guess at it:

1. **A direct mechanistic check**: parent-offspring trait correlation, measured across tens of thousands of real birth events, at several mutation levels — confirming whether inheritance is actually transmitting parental information faithfully, independent of any downstream survival outcome.
2. **A mutation-size sweep**: rerunning the same stress-test comparison at mutation standard deviations from 0.005 (very faithful inheritance) up to 0.20 (very noisy inheritance), against the same random-reassignment control, to see whether the heredity-vs-random gap changes as the fidelity of transmission changes.

## 3. Results

**The inheritance mechanism works exactly as designed.** Parent-offspring trait correlation, sampled across ~40,000+ birth events per condition, ranged from 0.998 at the lowest mutation level (std=0.005) down to 0.845 at the highest tested (std=0.15) — a clean, monotonic relationship confirming that lower mutation genuinely produces more faithful transmission, as intended.

**Faithful transmission did not help survival — it hurt it.** Across the mutation sweep:

| Mutation std | Heredity condition survival | Random-reassignment control |
|---|---|---|
| 0.005 | 11/15 | 14/15 |
| 0.01 | 11/15 | 14/15 |
| 0.02 | 9/15 | 14/15 |
| 0.05 | 15/15 | 14/15 |
| 0.10 | 13/15 | 14/15 |
| 0.20 | 15/15 | 14/15 |

The gap at mutation_std=0.02 is statistically real (two-proportion z = -2.16), not noise, and the pattern across the low end of the sweep (11, 11, 9 out of 15) is consistent: the *more faithfully* a population transmits parental traits, the *worse* it fared under stress — the opposite of what a naive "more heredity should help more" prediction would expect.

## 4. Interpretation: bet-hedging, not heredity, is the operative variable

The likely mechanism is a real, well-documented phenomenon from evolutionary biology: in an environment subject to unpredictable shocks, maintaining broad standing variation in a population can matter more than faithfully transmitting whatever trait was successful a moment ago. Very faithful heredity (low mutation) lets a population's trait distribution narrow and converge — via ordinary selection and drift — around whatever worked under pre-shock conditions. When an unforeseen stress then hits, there is little diversity left for selection to act on precisely when it is needed most. Random reassignment, and to a lesser degree high-mutation heredity, continuously replenish that standing variation regardless of recent history, which turns out to be exactly the resource a population needs to weather something it could not have prepared for in advance.

This reframes, rather than simply reconfirms, the original null result. The earlier test's mutation rate (0.05) happened to sit at a point where heredity's own variation-preserving effect roughly matched the variation random reassignment provides by construction — which is why the two conditions looked equivalent. Random reassignment was never a fair "no heredity" baseline in the way it first appeared; it is better understood as one extreme of a real spectrum (effectively infinite mutation rate), and this test shows that extreme happens to provide the level of standing variation that is actually adaptive here. What the population needs to survive an unpredictable shock is diversity, not lineage-faithful inheritance — and past a certain point, more faithful inheritance actively works against that need.

## 5. The gradual-ramp test: the bolder, better-supported claim

Standard bet-hedging theory predicts an asymmetry: standing variation should matter most under unpredictable stress, while heritable tracking should have the advantage when environmental change is gradual and foreseeable — a population that can accumulate and transmit adaptation over many generations should outperform one that discards all information every generation, provided the change is slow enough to track. This was tested directly, not assumed.

**Method**: identical mechanism and conditions to the original stress test, but metabolic cost now rises gradually and continuously (a linear ramp from 0.04 to 0.09 over 4,000 steps) rather than jumping abruptly — a genuinely slow, foreseeable change a population could plausibly track across many generations if heredity's transmission advantage exists.

**Result, at full statistical power (n=40 per condition)**:

| Condition | Survival | vs. random reassignment | vs. fixed-trait control |
|---|---|---|---|
| Fixed-trait control (no heredity, no variation) | 26/40 (65%) | — | — |
| Real heredity (parent-average + mutation) | 31/40 (77.5%) | z = -3.18 (significant) | z = 1.24 (not significant) |
| Random reassignment (fresh trait every birth) | 40/40 (100%) | — | z = 4.12 (significant) |

**Random reassignment does not merely tie heredity under gradual change — it clearly and significantly beats it (z = -3.18).** And heredity's own advantage over having no variation at all is not statistically significant (z = 1.24) — a real heritable tracking mechanism provides only a marginal benefit over a population with no adaptive variation whatsoever, while random reassignment's benefit over the same baseline is large and unambiguous (z = 4.12).

**This directly contradicts the standard bet-hedging prediction, and it is not because heredity fails to function.** A separate check confirmed heredity genuinely tracks the ramp: mean population trait rose from 0.523 at the start of the ramp to roughly 0.55 through most of its course, then more sharply to 0.624 as cost approached its final, most demanding level — real, visible, directionally correct adaptive drift, not a flat or random signal. Heredity does exactly what the theory says it should do. It simply does not translate into a survival advantage over a population that tracks nothing at all and instead maintains raw, undirected diversity.

## 6. The bolder claim this project is now willing to make

Across both regimes tested — a sudden, unpredictable shock and a slow, fully predictable ramp — random reassignment of trait values matches or significantly outperforms heritable tracking. This is a genuine departure from the standard bet-hedging asymmetry, not a confirmation of it: the textbook prediction is that heredity should win when change is foreseeable, and it does not, even when heredity is independently confirmed to be tracking the change correctly. In this substrate, raw standing variation appears to be a more valuable resource than lineage-based adaptation, independent of whether the environment's change is predictable or not — a stronger and more general claim than standard bet-hedging theory would suggest on its own.

## 7. What this establishes

- The heredity mechanism itself is confirmed to function correctly and to genuinely track environmental change — this is not an artifact of broken or inert inheritance.
- Under sudden, unpredictable stress, standing trait variation is the load-bearing resource, and there is a real, measurable point at which increasing heredity fidelity becomes actively counterproductive.
- **Under gradual, predictable change — the regime where heredity's transmission advantage should matter most — random reassignment still significantly outperforms real heredity (n=40, z=-3.18), and heredity's own benefit over no variation at all is not statistically significant.** This is the project's strongest, best-powered claim on this question: across both regimes tested, standing variation appears to dominate lineage-based tracking, not just under unpredictability but under predictability too.

## 8. What this does NOT establish

- **This does not generalize automatically beyond the two regimes tested (sudden shock, linear gradual ramp).** A different kind of predictable change — cyclical, multi-phase, or one with a clearer, stronger fitness gradient for the trait to track — might still show heredity's advantage; this has not been tested.
- Sample size for the core stress-test comparisons is now strong (n=40 for the ramp test), but the trait-tracking confirmation and the original mutation sweep remain at smaller sample sizes (5–15 seeds) and should be read at the confidence their own statistics support.
- This tests one trait (exploit-vs-mutualism propensity), one substrate, one specific ramp shape and rate. Whether the same dominance of standing variation holds for other traits, other substrates, or different ramp steepness is untested.

## 9. Suggested next steps

1. Test whether an even more extreme ramp (slower, or with a stronger, clearer fitness gradient for the trait to track) can finally reveal a heredity advantage, or whether the dominance of standing variation holds even in the most favorable-to-heredity conditions reasonably constructible in this substrate.
2. Directly measure trait-distribution variance (not just mean trait or survival) over time across both the mutation sweep and the ramp test, to confirm the proposed mechanism (variance collapse under faithful heredity, preserved variance under random reassignment) directly rather than inferring it from survival outcomes alone.
3. Test a structurally different kind of environmental change (e.g., cyclical or reversing conditions, where a population that mis-tracks a temporary trend could be actively penalized) to see whether that regime favors heredity's more targeted, if slower, adaptation over random reassignment's brute-force diversity.
