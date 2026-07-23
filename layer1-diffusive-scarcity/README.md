# RGH Layer 1: Diffusion-Limited Energy Scarcity — Synthesis

**Status: New architecture. Contains one major self-correction, made and reported transparently rather than smoothed over: an initial "rule-dependent, not universal" conclusion was overturned by a calibration check, and a later "thermodynamic parasitism" hypothesis was proposed, then directly tested and rejected in favor of a more modest, better-supported mechanism. Both corrections are preserved here as part of the record. Not yet part of the main paper.**

---

## 1. What Layer 1 is, and why it is a different architecture, not a bigger Layer 0

Every Layer 0 test — including the Landauer-gated Transformation extension — gave each cell an independent, unconditional energy income. Structurally, no cell's activity could ever affect a neighbor's supply. Layer 1 replaces flat independent income with a genuine shared, spatially-limited resource: a small background inflow (`D_bg`), plus real diffusion (`D_diff`) that moves energy from higher-concentration cells to lower-concentration neighbors each step (a discrete Laplacian, exactly conserving total energy on the periodic grid apart from the background inflow term). A region's own activity can now visibly deplete the resource its neighbors depend on — a real phase change in the substrate, not a parameter extension.

This document covers two stages: Stage 1, a single rule drawing on this shared resource (isolating whether a rule's own activity can deplete its own local supply), and Stage 2, genuine competition between two distinct rules sharing one energy field (the actual ecological question this architecture was built toward).

## 2. Method

**Mechanism**: the same Landauer gate as the Transformation extension (a proposed state transition executes only if local energy covers `FLIP_COST`), with energy updating via `energy += D_bg` followed by diffusion each step, rather than flat unconditional income.

**Stage 1 rules tested**: Brian's Brain (chosen first because its mandatory transitions already showed, in Layer 0, that it cannot sustain any activity below a real flat-income threshold), then Conway's Game of Life and Day & Night for comparison, all on the identical mechanism.

**Stage 2**: Game of Life and Brian's Brain, sharing one energy field, with rules kept **mutually blind** — each species' survival/birth/ignition logic counts only same-species neighbors, never the other species. This is deliberate: the only channel through which one species can affect the other is energy depletion and diffusion, not direct topological interference, so any competitive outcome is unambiguously about the shared resource. Cells occupied by either species evaluate only their own transition logic (no mid-state takeovers — a cell must return to OFF before being recolonized by the other species). Contested OFF cells (simultaneously eligible for a GoL birth and a Brian's Brain ignition) are resolved by a neutral 50/50 coin flip, not by relative neighbor count, since the two rules' neighbor-count conventions are not on a comparable scale. Both species pay identical `FLIP_COST = 1.0`, isolating rule topology (facultative vs. obligate) as the sole variable in this first competitive test. Both species start at equal density (10% each), randomly interspersed, to avoid any home-field starting advantage.

## 3. Stage 1 results: a real interior complexity peak, initially miscalibrated, then corrected

### 3.1 Brian's Brain: the initial, clean result

A fine-grained sweep (`D_diff` 0 to 1.0, background inflow fixed at 0.05, 8-10 seeds per point) found a sharp, three-part signature for Brian's Brain: a hard extinction threshold between `D_diff = 0.03` and `0.04` (exactly zero flux, complexity, and population below it), a genuine interior peak in complexity rising from 0.31 at threshold to 0.63 around `D_diff ≈ 0.10–0.12`, then a smooth decline to 0.22 by `D_diff = 1.0` — all while flux stayed remarkably flat across the entire active range. A direct check confirmed the underlying "wake" mechanism rather than assuming it: active cells consistently showed measurably lower local energy than quiet cells (e.g., 0.65 versus 1.05 at `D_diff = 0.1`).

### 3.2 An initial cross-rule comparison, and a real miscalibration caught before it reached the repo in final form

Game of Life and Day & Night were run through the identical mechanism at the same background inflow (0.05) used for Brian's Brain, to test whether the interior peak was general or rule-specific. Neither showed anything close to Brian's Brain's dramatic signature: both sustained substantial activity even at `D_diff = 0` (no diffusion needed at all), Game of Life showed only a modest ~20% relative rise before declining, and Day & Night showed no rise away from zero at all — its highest complexity occurred at `D_diff = 0`, declining from there. **This was initially reported and repo'd as "the interior peak is rule-dependent, specific to mandatory-cycling rules."**

That conclusion did not survive a calibration check, and the check is worth describing because it is the actual finding. Background inflow of 0.05 sits close to Brian's Brain's own threshold, but it does not sit close to Game of Life's or Day & Night's — both rules can sustain themselves comfortably above their own marginal zones at that level, muting any threshold-adjacent effect. A dedicated sweep of `D_bg` at `D_diff = 0` found each rule's own much lower marginal zone (noisy and non-monotonic rather than sharply threshold-like, but real): roughly `D_bg ≈ 0.01` for Game of Life and `D_bg ≈ 0.015` for Day & Night. Re-running the `D_diff` sweep at these rule-matched background rates overturned the earlier conclusion: **Game of Life showed a dramatic interior peak** (complexity rising from 0.086 at `D_diff = 0.01` to 0.196 at `D_diff ≈ 0.03–0.04`, roughly a 128% increase, confirmed stable at n=20 seeds), and **Day & Night also showed a real, confirmed peak** (0.450 to 0.503 at `D_diff ≈ 0.03`, a more modest ~12% relative rise from an already-high floor, also confirmed at n=20).

**The corrected conclusion**: the interior complexity optimum is present in all three rules tested, once each is evaluated near its own energetic threshold rather than at one calibration borrowed from a different rule's threshold. The magnitude and character of the peak differ meaningfully across rules (Game of Life's dramatic relative swing from a near-zero floor; Day & Night's modest rise from an already-substantial floor; Brian's Brain's large absolute swing tied to its all-or-nothing activation), but the qualitative shape — rise from a marginal floor to an interior maximum, then decline as diffusion homogenizes the resource — appears to be a genuine property of diffusion-limited scarcity itself, not a special feature of mandatory-cycling rules specifically. This plausibly replicates a well-established phenomenon from a different field — excitable media (the same broad class as cardiac tissue or the Belousov-Zhabotinsky reaction) are well documented to have an intermediate-diffusion sweet spot for sustaining coherent traveling waves — rather than constituting a new principle; that the framework reproduces this shape independently is a point in its favor, not evidence of novelty.

## 4. Stage 2 results: genuine competition, and a second self-correction

### 4.1 Brian's Brain decisively wins territory, contrary to the pre-registered hypothesis

The original hypothesis proposed that Game of Life, as a low-maintenance "weed," would starve Brian's Brain's higher-maintenance waves by drawing down shared ambient energy. Tested at `D_bg = 0.05` (both species able to activate from the start) across a `D_diff` sweep (n=10 seeds per point), the result was the opposite: **Brian's Brain won 55.6% to 96.7% of contested territory**, increasing with diffusion rate, while Game of Life's share shrank correspondingly. The boundary energy gap consistently showed *Game of Life's* neighborhood at higher ambient energy than Brian's Brain's (e.g., 2.26 versus 0.89 at `D_diff = 0.01`) at every point tested — Brian's Brain was never the energy-rich competitor, and still won decisively.

Re-tested at `D_bg = 0.01` (Game of Life's own calibrated threshold, hypothesized to favor the "efficient" static species under extreme scarcity), the result did not reverse: Brian's Brain won even more decisively (94.7–96.0% territory), and neither species went extinct at any diffusion rate tested — notably, Brian's Brain survived at a background rate below what it needed to survive at all when alone on the grid.

### 4.2 A proposed "thermodynamic parasitism" mechanism, directly tested and rejected

The consistent direction of the boundary energy gap (Game of Life's neighborhood always richer) suggested a specific hypothesis: that Brian's Brain was actively draining Game of Life's reserves through diffusion — a form of structural exploitation, with Game of Life's accumulated energy subsidizing Brian's Brain's expansion. This was checked directly rather than accepted as a plausible story: mean energy among Game-of-Life-occupied cells was compared between Game of Life running alone and Game of Life competing with Brian's Brain, at matched `D_bg` and `D_diff`.

**The result contradicted the hypothesis.** Game of Life's own cells showed *higher* mean energy when competing with Brian's Brain than when alone on the grid, at every diffusion rate tested (e.g., 1.28 versus 0.78 at `D_diff = 0.01`) — the opposite of what draining or mining would predict. A direct measurement of flux at the contested species boundary confirmed energy does flow from the Game-of-Life side toward the Brian's-Brain side (positive at every point tested), so half of the original mechanism is real. But the conclusion drawn from that flux — that this measurably harms Game of Life — does not survive direct measurement of Game of Life's own energy budget.

**The better-supported mechanism**: Game of Life, driven into a small territorial footprint (4–8% of the grid) by Brian's Brain's more aggressive space-filling, experiences reduced intra-species competition for the same local background trickle. A smaller surviving population sharing the same per-cell inflow, with less contest for it, ends up in a comparatively resource-rich refuge — not because Brian's Brain is feeding it, but because Brian's Brain's dominance elsewhere leaves Game of Life's remaining pocket relatively uncontested. This is a real, specific, and still interesting finding — a "refuge effect" from competitive displacement — but it is a more modest claim than parasitism or structural exploitation, and the more dramatic framing should be treated as rejected, not merely unconfirmed.

## 5. Interpretation

Three genuine findings survive scrutiny here, each corrected at least once along the way to its final form:

1. **An interior complexity optimum under diffusion-limited scarcity is a real, general property across all three rules tested**, once each is evaluated near its own energetic threshold — initially mistaken for a special property of Brian's Brain's mandatory cycling specifically, a conclusion overturned by proper calibration.
2. **Under genuine competition for a shared, diffusing resource, a rule that cannot stop moving outcompetes a rule that settles into stasis for territory** — regardless of which one operates on the richer local energy margin. Efficiency did not confer competitive advantage in either scarcity regime tested; the capacity to continuously contest new territory did.
3. **Displacement into a smaller territory is not the same as being drained by the competitor that caused it** — an appealing "parasitism" narrative was proposed, tested directly, and rejected in favor of a more modest refuge-effect explanation.

## 6. What this does NOT establish

- **One pairing tested (Game of Life vs. Brian's Brain).** Day & Night has not been tested in competition, nor has any pairing with symmetric rule character (e.g., two facultative rules, or two obligate rules with different parameters).
- **Only symmetric metabolic cost has been tested.** Both species pay identical `FLIP_COST`; a calibrated-cost version (each species paying according to its own baseline threshold) remains untested and was explicitly deferred to isolate rule topology as the sole variable in this first experiment.
- **The refuge-effect mechanism (Section 4.2) is a plausible, better-supported alternative to parasitism, not independently verified beyond the single check reported here** (comparing alone versus shared mean energy at matched parameters). A direct measurement of intra-species competition intensity (e.g., local Game-of-Life population density in the refuge versus when alone) would strengthen this further.
- **One grid size, one set of protocol parameters**, matching earlier Layer 0/1 work for comparability, not independently optimized for the competitive architecture.
- **The excitable-medium connection (Section 3.2) remains a plausible, structurally-motivated interpretation, not a verified quantitative match** to a specific published result.
- **Any broader ecological, economic, or "socio-political thermodynamics" framing of these results is a suggestive analogy, not a validated claim.** The mechanisms here are specific to this substrate, this pairing, and these parameters; extending the interpretation to real biological or social systems would require substantially more evidence than this document provides.
- **This is not yet part of the main paper.**

## 7. Suggested next steps

1. Test a calibrated-cost version of the Stage 2 competition (each species paying a `FLIP_COST` proportional to its own baseline threshold), to check whether Brian's Brain's territorial dominance survives when its higher metabolic demand is explicitly priced in, rather than treated as free.
2. Test at least one more rule pairing (e.g., Day & Night vs. Brian's Brain, or Game of Life vs. Day & Night) to check whether "kinetic dispersal beats static efficiency" generalizes beyond this one pairing, or is specific to Brian's Brain's particular mandatory-cycle structure.
3. Directly measure intra-species competition intensity in Game of Life's refuge pocket (Section 4.2), to strengthen the refuge-effect explanation beyond the single alone-versus-shared energy comparison already run.
4. Quantitatively compare the Stage 1 interior-peak shape to a specific published excitable-medium result, to move Section 3.2's interpretation from plausible to verified.
