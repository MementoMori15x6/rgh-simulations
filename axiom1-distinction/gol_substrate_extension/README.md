# Axiom 1 (Distinction) on the Game-of-Life Substrate

The main Axiom 1 findings (see parent README) were built entirely on Gray-Scott
reaction-diffusion — a continuous-field substrate. Everything else in this
project (Persistence, Exploitation/Adaptation, Loop Closure) runs on Game of
Life — discrete and binary. This subfolder closes that substrate gap by
running the same causal-insulation methodology directly on Game of Life.

## Method and results

**`stage1_ignition_sweep.py`** — the GoL analog of the Gray-Scott noise-amplitude
sweep: start from an all-dead grid, perturb with sparse random noise at varying
density, and find the threshold between "dies back to nothing" and "structure
persists." Result: a clean, sharp, monotonic threshold — below ~0.05 density,
everything dies; at 0.08 and above, structure reliably persists (30-107 final
live cells across every seed tested up to density 0.30). Notably cleaner and
more monotonic than the Gray-Scott result, which had a narrow, non-monotonic
ignition window.

**`stage2_causal_insulation.py`** — the actual Distinction test: ignite at
density 0.10 (comfortably above threshold), let the population settle for
1,500 steps, then test whether the resulting structure shows genuine reduced
information coupling (time-lagged mutual information) across its boundary
relative to its interior — the same test validated on Gray-Scott's spots.

**Important methodological finding, required before the test could run
meaningfully**: only about 10% of seeds (2 of 20 checked) retain any dynamic
content (oscillation or motion) after settling — the large majority freeze
into purely static remnants (still lifes only). A fully static population has
zero variance in its trajectory, and mutual information between constant
signals is trivially zero — not evidence of anything, just an untestable
case. The causal-insulation test therefore requires filtering for seeds whose
settled population retains genuine dynamics before running it — a real
precondition check, not cherry-picking a result.

**Result, on 8 qualifying dynamic-content seeds**: a clean, fully monotonic
ordering — interior (mean MI 0.148) > boundary (0.029) > background (0.015) —
and critically, **every one of the 8 seeds individually showed interior >
boundary**, not just the average. Paired t = 2.74 (n=8, small sample, but a
unanimous direction across every trial). This is a cleaner ordering than the
Gray-Scott result, which had an anomalous background-highest artifact.

## What this establishes

Distinction, tested with the same rigorous causal-insulation methodology used
for Gray-Scott, now has a real, positive result on the Game-of-Life substrate
that the rest of this project's Persistence, E/A, and Loop Closure work
actually runs on — not just on a separate substrate used in isolation.

## What this does NOT establish

- The 8-seed sample is small; this should be treated as a promising, real,
  but not yet heavily-powered result.
- The finding only applies to the ~10% of outcomes that retain dynamic
  content — the majority (static remnants) are not, and cannot be, tested by
  this specific method.
- This does not test causal insulation on the energy-conservation substrate
  (with metabolic cost) used elsewhere in this project — only on plain,
  unmodified Game of Life.
