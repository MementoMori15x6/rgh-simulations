# RGH Layer 0 Extended to Transformation: Landauer-Gated Execution

**Status: New test, resolving a question the original Layer 0 document explicitly deferred. Not yet part of the main paper. Several rule "auditions" were tried and rejected before the reported result — documented transparently, not hidden, since the rejections are themselves informative.**

---

## 1. Hypothesis under test

The original Layer 0 document found that "does Transformation require dissipation" is a category error as literally stated — Transformation is definitionally a fixed rule, not a phenomenon that occurs or fails to occur depending on energetic conditions, unlike Distinction (does a boundary form) or Persistence (does the population drift toward stable configurations). It proposed a reframed, well-posed version instead: does a rule's *computational richness* — its capacity for sustained, complex dynamics rather than simple fixed-point or periodic behavior — depend on energetic conditions?

This document tests that reframed question directly.

## 2. Method

**The mechanism, genuinely different from every prior Layer 0 test**: energy gates whether a proposed state transition can execute at all, not merely whether its result survives afterward.

1. Each step, compute what the rule proposes for every cell without applying it.
2. Any cell whose proposed state differs from its current state is a bit flip (Landauer's formulation — a state change that must be paid for; a cell that would stay the same costs nothing).
3. A cell can only execute its proposed flip if it has enough energy to pay a fixed `FLIP_COST` (1.0). If not, the cell is frozen — genuinely prevented from transitioning, not merely more likely to die afterward.
4. Energy accumulates via unconditional inflow `D` each step, with no decay term. This has a clean physical reading: at `D = FLIP_COST`, every cell earns exactly enough per step to always afford a flip (fully unconstrained); below that, flips are throttled in frequency rather than hard-gated.

**A mathematical property of this scheme, confirmed directly rather than assumed**: because updates are synchronous and a cell can flip at most once per step, `D = 1.0` is a hard ceiling — no cell can ever need more than one `FLIP_COST` per step, so every value of `D ≥ 1.0` is mathematically guaranteed to be identical to `D = 1.0`, for any rule. This was verified directly (every measured quantity was bit-for-bit identical from `D = 1.0` through `D = 8.0`) rather than assumed, and it means the entire meaningful range for this model is `D ∈ [0, 1]` — not a limitation discovered late, but a real property of the energy-accounting scheme worth knowing precisely.

**Complexity measure, and why Lempel-Ziv was deliberately not used**: the original design proposal used Lempel-Ziv complexity as the numerator of a thermodynamic efficiency ratio. This was identified as a real technical problem before building anything: LZ complexity rises monotonically with randomness — pure noise has the *highest* possible LZ complexity, not zero — so it cannot distinguish genuine structure from incoherent noise, which is exactly the distinction this test needs to make. Instead, this document reuses the validated mutual-information approach from the Axiom 1 work: mean time-lagged mutual information between each cell and its immediate neighbors' trajectories, sampled over a trailing window. This has the right shape by construction — near zero for a frozen grid (no variance to have information about) and near zero for genuinely incoherent noise (neighbors don't predict each other), positive only for real, coordinated structure.

**Three rules tested, in the order they were tried:**
- **Conway's Game of Life** (B3/S23) — the validated baseline, already known from the Persistence work to settle toward low-flip-rate stable structures.
- **Day & Night** (B3678/S34678) — chosen after three other candidates failed a basic sustained-activity check (Section 3.2).
- **Brian's Brain** — a 3-state rule (Ready → Firing → Refractory → Ready) where two of the three transitions are mandatory regardless of neighbors, chosen specifically because it cannot freeze into a static configuration the way single-state binary rules can.

## 3. Results

### 3.1 Game of Life: an early spike, verified mechanistically, then a plateau tied to the Persistence finding

Sweeping `D` from 0 to 1 (21 points, 10 seeds each): `D = 0` gives exactly zero flux and zero complexity (true freeze, confirming the basic mechanism). A sharp spike appears at `D ≈ 0.05` — both flux and complexity reach their highest values in the entire sweep, and, notably, the population *grows* past its random-soup starting density rather than declining.

This was checked mechanistically rather than reported at face value. Direct measurement at `D = 0.05` found that death-transitions (a live cell's rule-proposed transition to dead) are attempted more than twice as often as birth-transitions (98,199 versus 45,833 over 200 steps), but succeed at less than half the rate (15.3% versus 33.5%). Net effect: cells that "should" die under Game of Life's rule are being frozen alive more often than cells that "should" be born are being frozen dead — a real, reproducible asymmetry, confirmed by exact energy accounting, not a bug. Why birth outperforms death proportionally at this specific energy level was not fully traced to a deeper cause and is reported as a genuine, verified, but not completely explained phenomenon.

Past this spike, flux and complexity decline through a transition region (`D ≈ 0.1–0.25`) as the anomalous population growth reverses, then settle into a long, flat plateau from `D ≈ 0.25` to `D = 1.0`, with flux, complexity, and population all sitting in a narrow, stable band regardless of how much further `D` increases. This directly connects to the validated Persistence finding: once energy is sufficient to stop meaningfully throttling the rule, Game of Life simply does what it already does on its own — converges toward low-flip-rate blocks and gliders — and additional available energy goes unused because the system isn't asking for more transitions than it already gets.

### 3.2 Finding a genuine high-turnover comparison rule: three rejections before Day & Night

To test whether Game of Life's early-saturation behavior is general or rule-specific, a second rule with a genuinely different character was needed — one that does not settle into a low-flip-rate attractor. Three candidates were tried and rejected before finding one that worked, and the rejections are informative in their own right:

- **B3/S1234** (birth on 3, survival on 1–4 neighbors): despite a folk reputation as "chaotic," direct measurement showed it rapidly fills the grid and settles into a dense, near-frozen configuration (flip count falling from 772 at step 0 to a steady 11 per step by step 25) — the same qualitative behavior as Game of Life, just at a higher density.
- **B3/S∅** (birth on 3, no survival condition — every living cell dies every step by construction): this guarantees maximum turnover but crashed to total extinction by step 10, since a population with zero memory cannot sustain replacement-level births.
- **Replicator, B1357/S1357**: sustained substantial, genuine activity (~2,000+ flips per step) for roughly 35 steps, then collapsed to exact, total extinction — a known parity/cancellation sensitivity documented in this rule family, not a random failure.

**Day & Night** (B3678/S34678) was the first candidate that neither froze nor crashed: its raw, ungated behavior settles into a small, persistent, actively-oscillating remnant (roughly 25–29 cells, with nearly 100% of survivors flipping every step, holding steady from step ~100 onward). Under the Landauer-gated sweep, Day & Night showed the same qualitative low-`D` spike as Game of Life, more extreme (`η_T = 5.99` at `D = 0.05`, population growing to 2,710 from a starting ~1,025) — but unlike Game of Life, it did not find a stable plateau afterward. Flux and complexity continued declining well past the transition region, becoming sparse and volatile (mean population dropping to single digits around `D = 0.45`) before settling into a low, noisy floor from `D ≈ 0.5` onward, at values similar to or below Game of Life's own plateau.

**Neither binary rule sustains genuine, open-ended energy demand.** Both eventually find a low-flux attractor once sufficiently unthrottled — Game of Life a moderate-density, stable one; Day & Night a sparser, noisier one — but neither continues demanding more as more energy becomes available. This is consistent with, and sharpens, a specific structural point: deterministic, memoryless, single-state Life-like rules always have *some* configuration in which every cell's proposed transition matches its current state, and attrition dynamics reliably find such configurations given enough time, regardless of how much energy is available to spend.

### 3.3 Brian's Brain: a hard threshold, then genuinely sustained, monotonically-increasing demand

Brian's Brain's raw, ungated behavior was confirmed first: flip count stabilizes at a substantial, sustained level (roughly 300–370 per step) rather than declining toward zero or crashing to extinction — a genuinely different character from both binary rules.

Under the Landauer-gated sweep, Brian's Brain showed a sharp, hard threshold rather than a gradual one: every measured quantity is **exactly zero** for `D` from 0 through 0.25 — complete extinction during warmup, not merely reduced activity. At `D ≈ 0.3`, activity switches on and never returns to zero for the remainder of the sweep.

**Past this threshold, flux and complexity do not plateau or decline — they rise monotonically all the way to the model's own hard ceiling at `D = 1.0`.** This is the central result: no early saturation, no decline, no low-flux attractor found within the entire viable range. Thermodynamic efficiency (`η_T = C / Φ`) stays in a meaningfully higher, more stable band throughout (roughly 0.85–1.9) than either binary rule's settled value (Game of Life: ~0.4–0.5; Day & Night: low and noisy). Extending the sweep well past `D = 1.0` (up to `D = 8.0`) confirmed every value is bit-for-bit identical to the `D = 1.0` result — the genuine ceiling of the rule's demand coincides exactly with the model's own mathematical maximum, rather than saturating somewhere below it the way both binary rules did.

## 4. Interpretation

The reframed Transformation question is now answered, within this scope: **a rule's sustained computational demand under energetic constraint depends on a specific structural property — whether the rule's own dynamics permit a configuration where no further transitions are needed.** Game of Life and Day & Night, both single-state rules where "stay the same" is always an available outcome, reliably find such configurations once sufficiently unthrottled, and further energy goes unused. Brian's Brain, where two of three states have no "stay the same" option at all, cannot find such a configuration — every Firing or Refractory cell is mechanically forced to attempt a transition every step, and the rule's demand for energy scales with however much is available, right up to the point where the model itself can represent no further scaling.

This is a genuine, specific answer — not simply "yes, Transformation needs dissipation" or "no, it doesn't," but a precise account of *which structural property of a rule* determines the answer, mirroring the same pattern found for Distinction and Persistence: Layer 0's relevance is real but conditional, not a uniform fact about all systems alike.

## 5. What this does NOT establish

- **The `D = 1.0` ceiling is a mathematical property of this specific energy-accounting scheme** (flat per-step inflow, synchronous updates, at most one flip per cell per step), not a general physical law. A different accounting scheme (continuous-time updates, multiple flips permitted per step, a different cost function) could show different ceiling behavior, and whether Brian's Brain's demand would continue rising past what this model can represent is not addressed here.
- **The Game of Life `D ≈ 0.05` spike mechanism (death/birth flip-success asymmetry) was verified directly for Game of Life specifically, not independently re-verified for Day & Night**, which showed a more extreme version of the same qualitative spike. The two are presumed to share a mechanism given the structural similarity, but this was not directly confirmed for Day & Night.
- **One grid size (64×64), one set of protocol parameters** (FLIP_COST, warmup length, window length, MI sampling count) — not swept for sensitivity.
- **One complexity metric.** Mean pairwise mutual information was chosen deliberately over Lempel-Ziv for principled reasons stated in Section 2, but other structure-sensitive complexity measures (logical depth, statistical complexity) might characterize the three rules differently.
- **Three rules tested, one of each rejected-candidate type.** The claim that single-state Life-like rules "always" find a low-flux attractor rests on three candidates (Game of Life, Day & Night, plus the three rejected auditions) — a real, informative pattern, not an exhaustive survey of the rule space.
- **This is not yet part of the main paper.**

## 6. Suggested next steps

1. Test whether Brian's Brain's demand genuinely continues past what this model can represent, using a modified accounting scheme that permits more than one flip's worth of energy consumption per cell per step (e.g., asynchronous updates, or a fractional/continuous-time formulation).
2. Independently verify the death/birth flip-asymmetry mechanism for Day & Night, to confirm it shares Game of Life's specific mechanism rather than arriving at a similar-looking spike by a different route.
3. Test a fourth rule structurally similar to Brian's Brain (mandatory multi-step cycling) but with different neighbor-counting rules, to check whether "cannot freeze by construction" is the operative property in general, or something more specific to Brian's Brain's particular transition structure.
