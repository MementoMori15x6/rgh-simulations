# RGH Axioms 2 & 3 (Transformation, Persistence): Simulation Findings

**Status: Preliminary. Not peer reviewed. Much narrower evidentiary basis than the Axiom 1 document -- see Section 4 for why.**

---

## 1. Claims under test

RGH's Axiom 2 (Transformation) asserts that local, computationally irreducible rules drive change in system state. Axiom 3 (Persistence) asserts that some configurations endure against entropy -- that the system filters for coherence rather than dissolving into noise.

This document is shorter and more modest than the Axiom 1 findings, for a specific reason stated up front: unlike Axiom 1, where we built and ran a dedicated five-stage test chain, Transformation and Persistence were mostly present as *scaffolding* underneath the Exploitation/Adaptation (E/A) experiments reported elsewhere in this project, not as things we set out to test in their own right. What follows distinguishes what is genuinely established (mostly from 80 years of prior Cellular Automata theory, not from our own novel work) from what our own simulations actually exercised.

## 2. Transformation (Axiom 2): a framework choice, not a finding

Across this entire project, "T" was instantiated twice:

- **Rule 110** (1D elementary cellular automaton) -- a fixed, well-documented, Turing-complete local update rule (Wolfram Class 4).
- **Conway's Game of Life** (2D) -- a fixed, well-documented local update rule, validated in our own implementation against canonical patterns (blinker, glider) before any further work was built on it.

Both are real, standard, and correctly implemented in our simulations. But there is nothing to report as a *result* here: Transformation, as RGH frames it, is simply "the system evolves under a fixed local rule" -- this is true by construction of every cellular automaton ever built, ours included. Choosing Rule 110 or GoL's rule was a design decision, not an empirical discovery. We are not aware of a way to "test" Axiom 2 independent of picking a rule and observing what it does -- which is exactly what the rest of this project (and 80 years of CA research before it) already does.

## 3. Persistence (Axiom 3): well-supported in general, untested in RGH's specific sense

This is where a real distinction needs to be drawn between two different claims that could both be called "Persistence":

### 3.1 Persistence as a general phenomenon -- well-established, not our finding

Conway's Game of Life is one of the most thoroughly studied persistence-generating systems in existence: gliders, blinkers, blocks, and beehives all demonstrate patterns that endure far beyond the specific initial configuration that produced them, sustained purely by a fixed transformation rule with no adaptive or selective mechanism layered on top. Gray-Scott's spots (see the Axiom 1 document) demonstrate the same thing in a continuous reaction-diffusion setting. Our own Stage 1 sanity checks in both the GoL and Gray-Scott work confirmed our implementations reproduce this documented behavior exactly.

**This genuinely supports T-to-P**: a fixed local rule alone, with no exploitation-detection or adaptive-response loop, is sufficient to produce enduring structure. This is real, but it is not new -- it is among the best-established facts in CA theory, predating RGH by decades.

### 3.2 Persistence as active filtering (RGH's actual framing) -- not empirically exercised

RGH's Axiom 3, as originally formulated, describes persistence as the system actively "filtering for coherent, enduring configurations against entropy" -- implying selection, not just brute endurance under a fixed rule. This is the stronger, more specific claim, and it is the one our own `P` function was written to test.

**Finding, stated plainly: across every simulation run in this entire project -- 1D and 2D, dozens of seeds, hundreds of individual runs -- our `P` function never once filtered anything out.** `P` was defined as "reject trivial (all-zero or all-one) states," present and checked at every timestep of every experiment, and it simply never fired: every run either survived to its configured step limit or died completely (full extinction), with no run landing in an intermediate "detected as incoherent, filtered before full extinction" state that would demonstrate active selection at work.

This means we have **zero empirical evidence, from our own work, that persistence-as-active-filtering (as opposed to persistence-as-brute-endurance-under-a-fixed-rule) is doing anything distinct.** It is possible that in these substrates, at these scales, "dies completely" and "everything else survives" are the only two real outcomes, with no meaningful middle ground for a filter to act on -- which would mean Axiom 3's stronger claim may not even be well-posed for a substrate this simple, rather than merely untested.

## 4. Why this document is shorter and more cautious than the Axiom 1 document

The Axiom 1 findings were the product of a dedicated, five-stage chain built specifically to test that axiom, with real controls, bootstrap checks, and a positive result that survived scrutiny. Transformation and Persistence, by contrast, were never given that treatment -- they were assumed, used as infrastructure, and only examined in passing while building experiments aimed at E/A. This document reflects that difference in evidentiary effort honestly rather than manufacturing a comparable-looking result where none was actually pursued.

## 5. What this does NOT establish

- That RGH's specific, stronger version of Persistence (active filtering against entropy) is true or false -- it remains untested, not merely unconfirmed.
- Anything about Exploitation/Adaptation, which is documented separately and remains at five nulls.
- Anything about the recursive loop or reflexive self-modeling (`M`) -- out of scope here as in the Axiom 1 document.

## 6. Suggested next step, if continuing this line

The one genuinely open, answerable question this document surfaces: **can `P` be made to discriminate at all**, in a substrate simple enough to reason about? A concrete test would be to construct or search for CA parameter regimes (in Rule-110-like 1D rules, or GoL-like 2D rules) that reliably produce a *third* outcome -- neither full extinction nor indefinite survival, but a detectable "coherent-but-eventually-collapsing" trajectory -- and check whether a `P`-like filter can be defined that meaningfully distinguishes these cases before they fully die out. Until that exists, Axiom 3's stronger claim has no empirical foothold in this project, positive or negative.
