# RGH Exploitation/Adaptation (E/A): Simulation Findings

**Status: Preliminary. Not peer reviewed. First positive, controlled result in the E/A line of this project after five prior null results on bit/pattern-level mechanisms (documented separately). Read Section 5 before treating this as a general validation of RGH's E/A framework.**

---

## 1. Claim under test

Does exploitation pressure trigger an adaptive response, and specifically: can a population that tracks realized outcomes of cooperative vs. exploitative strategies with specific neighbors learn to prefer cooperation (mutualism), producing measurably greater resilience than either fixed exploitation or unlearned random switching?

This is a narrower, more specific version of RGH's general E/A claim, made testable only after five prior attempts (1D cellular automaton, 2D Game of Life, four distinct repair mechanisms) failed because the underlying substrate had no genuine thermodynamic stakes — actions were free, gated only by lookup tables, with nothing to actually win or lose. This document reports the first test built on a substrate with real, conserved energy and genuine survival cost.

## 2. Substrate

Conway's Game of Life (validated implementation, canonical patterns confirmed in prior work) with a second, coupled field: a real, non-negative energy value per cell.

**Core rules, each calibrated empirically rather than assumed:**

- **Metabolic cost**: every live cell drains energy each step just to exist. An initial value (0.02) was found to be empirically inert — confirmed identical to plain GoL with no energy mechanic at all on the same seed. Recalibrated to 0.04 after a sweep found this to be the lowest value producing real, non-trivial selection (76→32 live cells vs. plain GoL on an identical seed) without total extinction.
- **Background energy inflow and decay**: an ambient energy source with a matching decay term, calibrated so the system reaches genuine equilibrium rather than growing energy without bound (an initial version lacked decay and grew unboundedly; caught and fixed before further work).
- **Birth cost**: new cells draw a real energy cost from their neighborhood, rather than receiving free energy.
- **Exploitation**: an asymmetric, energy-conserving transfer where the richer of two adjacent live cells draws disproportionately from the poorer one, capped so the poorer cell cannot be driven below zero. An initial implementation had a sign error causing the richer cell to *lose* energy — caught via an isolated two-cell test and corrected before any substantive results were trusted.
- **Mutualism**: both cells in an interaction pay a small fixed cost and both receive a larger bonus — a genuine positive-sum, energy-conserving exchange, not a relabeled version of exploitation or diffusion.

## 3. Findings, in sequence

### 3.1 Baseline robustness (energy-CA works)

Across 20 independent random-soup seeds, the energy-constrained substrate reached stable equilibrium in every case (no blowups, no universal collapse), with real, substantial population culling relative to plain GoL — confirming metabolic cost was doing genuine work, not merely present in the code.

### 3.2 Fixed-strategy comparison: mutualism produces more energy surplus (weak effect)

Across 15 seeds, populations using pure mutualism reached a modestly but reliably higher energy equilibrium (mean 0.705) than populations using pure exploitation (mean 0.683); paired t = 4.9. This confirmed the mechanism works as intended, but the effect on population *count* alone was negligible — GoL's own birth/survival topology, not energy abundance, was found to be the dominant factor in raw population size. This meant population count was the wrong metric to test the effect; energy reserve was the right one.

### 3.3 Stress test: the real, substantial finding

Populations were allowed to reach equilibrium under normal metabolic cost, then subjected to a metabolic shock (cost raised from 0.04 to 0.09, a level that reliably kills unconstrained populations, for 500 steps). Across 15 identical seeds:

| Condition | Shock survival rate |
|---|---|
| Pure exploitation | 7/15 |
| Pure mutualism | **15/15** |
| Memoryless 50/50 random choice | 5/15 |
| Random-preference control (same switching structure, no real learning) | 7/15 |
| **Memory-based strategy switching** | **15/15** |

Pure mutualism populations not only survived universally but retained substantial populations post-shock (28–113 cells). Pure exploitation populations that did survive often barely held on (4–8 cells), and nearly half went fully extinct.

### 3.4 Memory-based switching matches pure mutualism, and the effect is isolated to real learning

A mechanism was built where each cell tracks a running average of realized energy outcome from mutualism vs. exploitation, separately per neighbor-relative-position, and chooses the historically better-performing strategy with a 10% exploration rate (to avoid permanently locking in after one unrepresentative early outcome).

**This mechanism matched pure mutualism's 15/15 survival rate exactly** — a striking result, given it starts with no bias toward either strategy and must discover the advantage of cooperation through realized experience alone.

**Critical control, run specifically to rule out a false positive**: a structurally identical mechanism (same exploration rate, same switching logic) but with the "preferred" strategy chosen **randomly rather than from learned history** was tested. This control survived at only 7/15 — matching pure exploitation and the earlier memoryless-random condition, and far below the memory-based result. This isolates the effect specifically to genuine outcome-tracking, not to the exploration/switching structure itself.

## 4. What this establishes

Within this substrate and protocol: exploitation pressure, combined with a simple mechanism for tracking realized per-neighbor outcomes, leads a population to discover and commit to mutualistic cooperation, and this discovery produces genuine, substantial survival advantage under environmental stress — matching the resilience of a population that was cooperative from the start, and clearly exceeding both fixed exploitation and unlearned random strategy-switching.

This is the first positive, controlled result across the entire E/A line of this project. Unlike an earlier apparent positive result in 2D Game of Life work (which was later traced to a density-selection artifact upon proper controls), this result has already been tested against the specific alternative explanation most likely to produce a false positive (exploration/switching structure alone), and survived that test.

## 5. What this does NOT establish — scope limits

- **This is one substrate, one protocol, one set of calibrated parameters.** The metabolic cost, exploitation rate, and mutualism bonus/cost values were each found via sweeps to sit in a specific working range; whether the qualitative finding holds across a wider parameter space, different grid sizes, or different shock severities has not been tested.
- **Memory here is simple and position-anchored** (tied to relative neighbor direction, not persistent entity identity, since GoL cells have no lineage across birth/death) — a deliberate, flagged approximation, not a claim about how real biological memory or identity works.
- **This does not validate RGH's full recursive framework**, the bifurcation-threshold hypothesis, or reflexive self-modeling (`M`) — this document tests a single mechanism (learned strategy-switching under real energetic stakes) in isolation.
- **The exploration rate (10%) and running-average decision rule were chosen as reasonable defaults, not derived or swept.** Whether the result is sensitive to these specific choices is an open, answerable question, not yet addressed.

## 6. Suggested next steps

1. Sweep the exploration rate and shock severity to check whether the 15/15-vs-7/15 gap is robust across a range of conditions, or specific to the exact parameters tested here.
2. Test whether the population's realized exploit/mutualism choice ratio actually shifts toward mutualism over time under the memory-based mechanism, to directly confirm the mechanism of the effect rather than infer it from the survival outcome alone.
3. Test at larger grid sizes and with more seeds to strengthen confidence that this is not itself subject to a selection artifact of the kind found and corrected in the earlier 2D Game of Life pattern-persistence work.
