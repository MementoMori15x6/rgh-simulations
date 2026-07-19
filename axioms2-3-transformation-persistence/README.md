# RGH Axioms 2 & 3 (Transformation, Persistence): Simulation Findings

**Status: Revised. Includes a substantive new result (differential survival) that changes the interpretation of Axiom 3, not just its evidentiary support. Not peer reviewed.**

---

## 1. Claims under test

RGH's Axiom 2 (Transformation) asserts that local, computationally irreducible rules drive change in system state. Axiom 3 (Persistence) asserts that some configurations endure against entropy — that the system filters for coherence rather than dissolving into noise.

This document covers both, but the substantial content is in Persistence, where a genuine reframing occurred over the course of testing: early attempts treated Persistence as something requiring an *active operator* — a mechanism that inspects and intervenes on the system at each step. Later testing found this framing was likely wrong, and that Persistence is better understood as an *emergent statistical property* of running Transformation over time. That shift is the main finding reported here.

## 2. Transformation (Axiom 2): a framework choice, not a finding

Unchanged from the prior version of this document. Transformation was instantiated as Rule 110 (1D) and Conway's Game of Life (2D), both standard, well-documented, correctly-implemented local update rules. "The system evolves under a fixed local rule" is true by construction of any cellular automaton and is not independently testable apart from choosing a rule and observing what it produces. What that produces — with respect to Persistence — is the substance of the rest of this document.

## 3. Persistence (Axiom 3): three attempts at an active filter, then a reframe

### 3.1 Persistence as a general phenomenon — well-established, not our finding

Conway's Game of Life and Gray-Scott reaction-diffusion both demonstrate, as established prior science, that a fixed transformation rule alone is sufficient to produce enduring structure (gliders, blocks, stable spots), with no selective filter required. This was never in question; it predates RGH by decades.

### 3.2 First attempt: a crude active filter, and it backfired

The original test built a persistence filter that deleted any live cell with fewer than 2 neighbors, on the theory that this scrubs noise. Measured against a 500-step metabolic-shock-style stress test, this filter **reduced** lifespan by roughly 2,800 steps relative to no filter at all (paired t ~ -7.0) — it deleted real, functioning structure (gliders routinely have transiently low neighbor counts as part of their normal translation cycle) along with actual noise.

### 3.3 Second and third attempts: signature-based "smart" repair, on a substrate with genuine stakes

Reasoning that the crude filter failed only because it couldn't distinguish structure from noise, two more careful mechanisms were built on the validated energy-conservation Game-of-Life substrate (the same one used in the Exploitation/Adaptation work), where repair draws on a real, conserved energy budget rather than being a free action:

- **Local-signature targeting**: a coherence memory, built from unperturbed baseline runs, scored each damaged cell's immediate 3x3 neighborhood pattern by how often matching patterns historically persisted. Repair was targeted at high-confidence signatures.
- **Component-size targeting**: the same persistence criterion, but keyed on the size of the connected structure a damaged cell belonged to, rather than its immediate local pattern. This produced a much cleaner, more mechanistically legible signal -- confidence peaked sharply at component sizes 4-6 (0.57-0.75), corresponding to blocks and gliders, and fell to a stable floor (~0.2) for larger, more chaotic clusters.

Both were tested against a properly validated three-way control (no repair, random repair at matched rate, and repair guided by a **deliberately decorrelated** version of the same signal, verified via direct correlation checks rather than assumed). Both showed the same pattern, replicated at good statistical power (n=50, properly powered, confirmed via two-proportion tests):

- **Repair as a category is decisive.** No repair: 0% survival under stress, every time. Any repair mechanism -- smart, random, or even deliberately backwards -- survived at 55-70%.
- **Targeting quality made no statistically significant difference.** Smart vs. random, smart vs. shuffled, random vs. shuffled -- every pairwise comparison came back non-significant (all z < 1.1, far below the 1.96 threshold), across both the local-signature and component-size versions, and across both an unconstrained-budget design and a genuine forced-triage design (budget capped well below the number of damaged cells, specifically to rule out "the choice never mattered because there wasn't a real choice being made").

This is a real, convergent, three-times-replicated result: **an active filter that intervenes and chooses -- however well-informed that choice is -- does not demonstrate the stabilizing benefit Axiom 3, in its "active filter" reading, predicts.** The category of intervention (repair vs. none) matters enormously; the intelligence of the intervention does not, in any design tested.

### 3.4 The reframe: persistence as differential survival, not active filtering

The pattern across 3.2 and 3.3 -- active intervention either backfiring or not showing measurable benefit from being "smart" -- prompted a different question: does persistence require an active mechanism at all, or does it emerge simply from running Transformation over time, with no filter, no repair, and no intervention whatsoever?

**Method**: the validated energy-conservation substrate was run with *zero* additional mechanism -- no filter, no repair, no invented damage -- from 15 held-out random-soup seeds (disjoint from the seeds used to build the independent persistence-confidence memory, to avoid circularity). At intervals, the population's live cells were scored using the *same* component-size confidence memory from 3.3 -- a measure of how often, historically, a structure of that size went on to persist -- and the population-weighted mean was tracked over 2,000 steps.

**Result**: mean population confidence rose essentially monotonically, from 0.405 at the start (raw random soup) to a stable plateau of 0.657, reached and held from step ~1,550 onward, in **all 15 of 15 held-out seeds**, with zero extinctions. Population size fell from a mean of ~628 live cells to a stable ~15 over the same period.

**Why this is a clean result, not a tautology**: the confidence score was not "how big is this structure now" -- it was "how often, across an entirely disjoint set of trajectories, did a structure of this size go on to persist." The population wasn't just shrinking and mechanically scoring higher by definition; historically fragile configurations (large, chaotic clusters, confidence ~0.2) were dying off while historically robust ones (blocks and gliders, confidence 0.57-0.75) were the ones still standing at the end. The final plateau value (0.657) sits precisely in the confidence range independently assigned to blocks and gliders -- and matches a well-documented phenomenon in Game of Life research generally: random soup reliably "settles" into a population dominated by still lifes, oscillators, and gliders. This test reproduced that known phenomenon using an independently-built, held-out statistical measure, without being told what to look for.

## 4. What this means for RGH's formula

The compact recursive formula treats Persistence (`P`) as a discrete operator in a composition chain -- something that acts on the system's state at each step, alongside `D`, `T`, `E`, `A`. Three separate, carefully-controlled attempts to build that operator either made things worse or showed no measurable advantage over unintelligent intervention. The one test that produced a clean, strong, fully-replicated (15/15 seeds) result was the one with **no operator at all** -- persistence emerged as a population-level statistic of ordinary attrition under Transformation.

This suggests a specific, substantive revision to how RGH should model Persistence: not as a discrete filtering step in the composition chain, but as an emergent property that can be measured *after the fact* by observing which configurations a system's own dynamics leave behind over time. Whether this generalizes beyond the Game-of-Life substrate tested here, and whether it holds once Exploitation/Adaptation dynamics are layered on top (rather than the quiescent baseline used here), remain open.

## 5. What this does NOT establish

- That active persistence-filtering is impossible in general -- three specific designs failed to show a benefit; that is real, convergent evidence against those designs, not a proof that no active mechanism could ever work.
- That differential survival generalizes beyond Conway's Game of Life or beyond the quiescent (undamaged, unstressed) condition tested here. The result was deliberately measured on the *baseline* dynamics, precisely to isolate whether Transformation alone is sufficient -- it has not yet been tested under ongoing stress or in combination with the Exploitation/Adaptation mechanisms documented separately.
- Anything about the recursive loop, reflexive self-modeling (`M`), or the bifurcation-threshold hypothesis discussed earlier in this project -- out of scope here, as in the other findings documents.

## 6. Suggested next steps

1. Test whether the differential-survival trend holds under the same kind of stress (structural damage, energy drain) used in the active-filter tests -- does the population's mean confidence still rise, or does sustained damage overwhelm the passive selection effect?
2. Test whether combining differential survival with the Exploitation/Adaptation mutualism mechanism changes the trend -- does a population that's also learning to cooperate show faster, slower, or different convergence toward high-persistence structure?
3. If RGH's formula is revised to treat `P` as an emergent statistic rather than an operator, work out what that means concretely for the compact notation -- likely a reframing of `P` from an operation applied at each step to a property measured over a trajectory.
