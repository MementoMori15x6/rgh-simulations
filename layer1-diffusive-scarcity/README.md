# RGH Layer 1: Diffusion-Limited Energy Scarcity

**Status: New architecture, first results. A genuine interior complexity optimum was found, then checked against two other rules and confirmed to be real but rule-dependent, not universal. This is a physics-only result — the ecological (multi-rule competition) extension it was built toward remains a distinct, unbuilt next stage. Not yet part of the main paper.**

---

## 1. What Layer 1 is, and why it is a different architecture, not a bigger Layer 0

Every Layer 0 test — including the Landauer-gated Transformation extension — gave each cell an independent, unconditional energy income. Structurally, no cell's activity could ever affect a neighbor's supply; there was no scarcity, no sharing, and therefore no possibility of competition. Layer 1 replaces flat independent income with a genuine shared, spatially-limited resource: a small background inflow, plus real diffusion that moves energy from higher-concentration cells to lower-concentration neighbors each step (a discrete Laplacian, exactly conserving total energy on the periodic grid apart from the background inflow term). This is a real phase change in the substrate, not a parameter extension: a region's own activity can now visibly deplete the resource its neighbors depend on.

This document reports Stage 1 only: a single rule drawing on this shared, diffusing resource, isolating whether a rule's own activity can locally deplete its own supply, before any competition between distinct rules is introduced. Testing genuine competition (two rules, or two populations, sharing one energy field) is explicitly out of scope here and is the natural next stage, not something this document claims to have done.

## 2. Method

**Mechanism**: identical Landauer gate to the Transformation extension (a proposed state transition can only execute if local energy covers `FLIP_COST`), but energy now updates via `energy += D_bg` (a small, fixed background trickle) followed by `energy += D_diff * (neighbor_average - energy)` (diffusion) each step, rather than a flat, unconditional `D` per cell.

**Primary test rule**: Brian's Brain, chosen because its mandatory two-of-three forced transitions (Firing must become Refractory; Refractory must become Ready, regardless of neighbors) already showed, in the flat-income Layer 0 test, that it cannot sustain any activity below a real energy threshold — making it the most informative candidate for testing whether local energy concentration (via diffusion) can substitute for a flat income high enough to clear that threshold on its own.

**Comparison rules**: Conway's Game of Life and Day & Night, run through the identical diffusive mechanism, to test whether any interior complexity optimum found for Brian's Brain is a general property of diffusion-limited scarcity or specific to its particular structure.

**Metrics**: flux (`Φ`, total realized flip cost per cell per step) and complexity (`C`, mean time-lagged mutual information between neighboring cells' trajectories — the same measure validated and justified over Lempel-Ziv complexity in the Transformation extension), plus a direct measurement of the energy gap between active and quiet regions, to confirm any "wake" effect rather than assume it.

## 3. Results

### 3.1 The wake effect is real, confirmed directly before trusting anything downstream

At `D_diff = 0` (background inflow only, no diffusion), Brian's Brain went completely extinct — consistent with the Layer 0 finding that flat income of 0.05 is far below the ~0.25–0.3 threshold this rule needs. The moment diffusion was introduced, a direct check confirmed the hypothesized mechanism rather than assuming it: active (Firing or Refractory) cells consistently showed lower local energy than quiet (Ready) cells across every diffusion rate tested (e.g., mean energy 0.65 in active regions versus 1.05 in quiet regions at `D_diff = 0.1`) — a genuine, measurable "wake" where sustained activity locally depletes the shared resource faster than diffusion resupplies it.

### 3.2 A genuine interior complexity peak for Brian's Brain

A fine-grained sweep (`D_diff` from 0 to 1.0, 8 seeds per point, background inflow fixed at 0.05) found a sharp, three-part signature:

- **A hard extinction threshold** between `D_diff = 0.03` and `0.04` — exactly zero flux, complexity, and population below it; real, substantial activity immediately above it.
- **A genuine interior peak in complexity**, rising from 0.31 at the threshold to 0.63 around `D_diff ≈ 0.10–0.12` (population peaking similarly, around `D_diff ≈ 0.08`) — roughly double the complexity at threshold.
- **A smooth decline** past the peak, complexity falling to 0.22 by `D_diff = 1.0`, while flux (`Φ`) stays remarkably flat (≈ 0.05) across the *entire* active range from threshold to `D_diff = 1.0`.

The wake gap itself traces the same story: large near the threshold (0.90 at `D_diff = 0.04`), staying substantial through the rising-complexity region, then collapsing to a small, steady residual (≈ 0.11–0.13) once past the peak. The likely mechanism: near the threshold, energy stays locally concentrated enough to sustain genuinely coherent, spatially-correlated wave structure; as diffusion increases further, the same fixed energy budget (flux stays flat) gets spent in an increasingly decorrelated, less spatially-organized way, because the concentration gradients that sustained coherence get smoothed away faster than they can be exploited.

### 3.3 Confirmed rule-dependent, not universal: GoL and Day & Night do not show the same signature

The same diffusive mechanism was run on Game of Life and Day & Night to test whether this interior peak is a general property of diffusion-limited scarcity or specific to Brian's Brain. It is not general.

**Neither rule shows Brian's Brain's extinction-then-dramatic-peak shape.** Both sustain substantial activity even at `D_diff = 0` — consistent with the Layer 0 finding that both can function on flat income alone at levels far below what Brian's Brain requires; diffusion is not necessary for either to reach activity at all, unlike Brian's Brain, for which it was essential.

**Game of Life shows a real but much smaller peak**: complexity rises modestly from 0.176 (no diffusion) to approximately 0.21 around `D_diff ≈ 0.06` — a genuine, non-trivial rise of roughly 20% — before declining to approximately 0.08 at high diffusion. Real, but roughly an order of magnitude smaller in relative terms than Brian's Brain's swing.

**Day & Night shows no interior peak at all.** Its highest complexity value in the entire sweep occurs at `D_diff = 0` (0.30), fluctuating within a fairly flat, noisy band (0.22–0.24) through the low-to-mid diffusion range before declining at high diffusion (to approximately 0.08–0.09). There is no rise away from zero to identify as a peak — only an overall decline from an already-high starting point.

## 4. Interpretation

The interior complexity optimum is real, but it is not a universal signature of "any rule under diffusion-limited scarcity" — it is specifically pronounced for a rule whose own survival requirement cannot be met without spatial energy concentration in the first place. Brian's Brain's mandatory, inescapable cycling genuinely cannot function on any flat, undiffused income tested; diffusion is not merely helpful to it, it is the only way the rule can reach activity at all, and the resulting peak reflects a genuine tradeoff between "enough concentration to reach threshold and sustain coherent structure" and "so much diffusion that the concentration gradients coherence depends on get smoothed away." Rules that can already sustain themselves on flat income (Game of Life, Day & Night) show either a much weaker version of this tradeoff or none at all, because they never needed spatial concentration to survive in the first place — diffusion is optional scaffolding for them, not a precondition.

This connects to, and plausibly replicates, a well-established phenomenon from a different field rather than constituting a wholly new discovery: Brian's Brain, structurally, is an example of an *excitable medium* — the same broad mathematical family as cardiac tissue or the Belousov-Zhabotinsky reaction, both real physical systems where sustaining coherent traveling waves is well documented to depend on a specific, intermediate diffusion rate, with fragmentation below it and homogenization above it. That this project's independently-built, energy-accounting framework reproduces that same qualitative shape is a point in favor of the framework's soundness, not evidence of a new principle — the honest framing is "our thermodynamic-gating approach replicates a known excitable-medium result," not "we discovered a new universal law of computation."

**What this is not**: this remains a single-rule test. A single process depleting and being resupplied by its own local footprint is not yet competition, and is not yet ecology in the sense of distinct entities contesting a shared resource. That bridge — Stage 2, testing whether an active region genuinely starves a neighboring quiet region occupied by a *different* rule or population — has not been built, and this document's results should not be read as having already crossed it.

## 5. What this does NOT establish

- **This tests one background inflow rate (`D_bg = 0.05`).** Whether Game of Life or Day & Night would show a clearer peak at a different, more finely-tuned background rate — one closer to their own respective activity thresholds, the way 0.05 sits close to Brian's Brain's — has not been tested. The absence of a clear peak for these two rules at this specific calibration does not rule out a peak existing at another calibration.
- **One grid size, one set of protocol parameters**, matching the Transformation extension for direct comparability, not independently optimized for this architecture.
- **This is a single-rule test only.** No genuine competition (two rules or two populations sharing one energy field) has been built or tested. The "ecological" framing this architecture was motivated by remains aspirational until that stage exists.
- **The excitable-medium connection is offered as a plausible, structurally-motivated interpretation, not an independently verified mechanistic match** to specific published results from that literature — the qualitative shape is consistent with what that field documents, but no direct, quantitative comparison to a specific published excitable-medium model has been made.
- **This is not yet part of the main paper.**

## 6. Suggested next steps

1. Sweep background inflow rate itself for Game of Life and Day & Night, to test whether a calibration closer to each rule's own activity threshold reveals a clearer interior peak — checking whether the muted signal found here is genuine rule-dependence or an artifact of using one calibration tuned around Brian's Brain's specific threshold.
2. Build the actual competitive extension: two distinct rules, or two distinct populations of the same rule with different trait values, drawing on one shared, diffusing energy field, to test whether an active region measurably starves a neighboring one — the genuine ecological question this architecture was built to eventually reach.
3. Directly compare the Brian's Brain diffusion-rate peak location and shape to a specific, published excitable-medium result, to move the connection in Section 4 from "plausibly consistent" to an actual quantitative check.
