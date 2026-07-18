"""
RGH v1 -- smallest possible concrete instantiation.

Substrate: 1D binary ring of length N.
Goal: implement D, T, E, A, P as ACTUAL functions on this substrate,
and be explicit about which ones are principled and which are invented.
"""

import random

N = 60          # ring length
STEPS = 40      # iterations of R
RULE = 110      # Class 4, Turing-complete elementary CA rule

# ---------- helpers ----------

def rule_table(rule_number):
    """Standard elementary CA rule table: maps 3-bit neighborhood -> next bit."""
    bits = [(rule_number >> i) & 1 for i in range(8)]
    table = {}
    for i in range(8):
        left, center, right = (i >> 2) & 1, (i >> 1) & 1, i & 1
        table[(left, center, right)] = bits[i]
    return table

TABLE = rule_table(RULE)

def hamming_weight(S):
    return sum(S)

def is_trivial(S):
    """All zero, or fully periodic with period 1 (all same value)."""
    return all(b == 0 for b in S) or all(b == 1 for b in S)


# ---------- D: Distinction ----------
def D(S):
    """
    Partition undifferentiated potential into A vs not-A.
    Concretely: from an all-zero ring, flip exactly one bit.
    NOTE: this is a ONE-TIME symmetry-breaking event, not a repeatable
    general operation. Once S is already differentiated, D is a no-op.
    This already reveals a problem: in the compact formula, D(S) is applied
    every iteration inside the composition, but D only does real work at t=0.
    """
    if all(b == 0 for b in S):
        S = S.copy()
        S[len(S) // 2] = 1
        return S
    return S  # no-op once differentiated -- is this legitimate, or a dodge?


# ---------- T: Transformation ----------
def T(S):
    """
    Apply local, computationally irreducible rule (elementary CA, Rule 110).
    This is the one operation with an unambiguous, well-established
    mathematical meaning. No invention needed here.
    """
    n = len(S)
    return [TABLE[(S[(i-1) % n], S[i], S[(i+1) % n])] for i in range(n)]


# ---------- E: Exploitation gradient ----------
def E(S):
    """
    INVENTED. RGH's prose: 'identifies lower-cost extraction pathways from
    accumulated value gradients.' There is no canonical bitstring analog of
    'value' or 'cost'. I am choosing a definition, not discovering one:

    Define local 'value' as density of 1s in a window (arbitrary choice --
    could as easily be defined as density of 0s, or of a specific motif).
    Define an 'exploitation site' as a position where a block of 1s sits
    adjacent to a block of 0s -- i.e. a boundary where 'copying' the 1-block
    into the 0-block would be the cheapest way to increase local value.

    Returns a list of boundary indices flagged as exploitable.
    """
    n = len(S)
    sites = []
    for i in range(n):
        if S[i] == 1 and S[(i+1) % n] == 0:
            sites.append(i)
    return sites


# ---------- A: Adaptation ----------
def A(S, sites):
    """
    INVENTED. RGH's prose: 'evolves stronger boundaries, encryption,
    cooperation in response to E.' I need some observable response to
    exploitation sites. Choice made: at each flagged boundary, with some
    probability, insert a 'defensive' pattern (a 0 immediately after the
    boundary stays 0 -- i.e. resist the 1-block's expansion) by forcing
    that bit low on the NEXT step only. This is implemented as a mask
    that overrides T's output at those positions.

    This is the weakest-justified function in the whole model. There is no
    principled reason 'adaptation' should look like this rather than any
    of a hundred other rules I could have picked.
    """
    n = len(S)
    override = {}
    for i in sites:
        j = (i+1) % n
        if random.random() < 0.5:
            override[j] = 0
    return override


# ---------- P: Persistence ----------
def P(S):
    """
    Filter for coherent, enduring configurations against entropy.
    Concretely: reject (flag as 'dead') states that are trivial
    (all-0 or all-1). This is well-defined given a state, but note:
    'filtering' implies selection among ALTERNATIVES, and we only have
    one trajectory here -- there's nothing to select FROM. Real selection
    would require running an ensemble and comparing. I'm flagging this,
    not fixing it in v1.
    """
    return not is_trivial(S)


# ---------- R: one iteration ----------
def R(S):
    S = D(S)
    S_next = T(S)
    sites = E(S)
    override = A(S, sites)
    for idx, val in override.items():
        S_next[idx] = val
    alive = P(S_next)
    return S_next, alive, sites


def run():
    S = [0] * N
    history = [S.copy()]
    exploitation_counts = []
    alive = True
    t = 0
    while t < STEPS and alive:
        S, alive, sites = R(S)
        history.append(S.copy())
        exploitation_counts.append(len(sites))
        t += 1
    return history, exploitation_counts, alive, t


if __name__ == "__main__":
    random.seed(7)
    history, exploitation_counts, alive, t_final = run()

    print(f"Ran {t_final} steps. Died early (hit P filter): {not alive}\n")
    for row in history:
        print("".join("#" if b else "." for b in row))

    print("\nExploitation-site count per step:", exploitation_counts)
