"""
Performance fix: pattern_reappears_nearby previously recomputed a fresh
3x3 signature (Python loop, per cell) for every position it checked
within the search radius, for every single candidate cell, every step.
That's the same category of bottleneck we hit and fixed in the 2D E/A
work (there it was local_entropy being recomputed cell-by-cell).

Fix: encode each cell's 3x3 neighborhood as a SINGLE INTEGER (9 bits,
values 0-511) for the WHOLE GRID AT ONCE using vectorized shifts, same
technique validated for entropy in the E/A work. Then "does this pattern
reappear nearby" becomes a single vectorized comparison against a slice
of the precomputed integer grid, not a nested Python loop recomputing
signatures one cell at a time.
"""

import numpy as np


def encode_signature_grid(grid, window=1):
    """
    Returns an integer array, same shape as grid, where each entry
    encodes the (2*window+1)^2 neighborhood as a single integer
    (bit i = 1 if that offset position is alive). This is the same
    signature space as the tuple-based signature() function, just
    encoded as an int for fast vectorized lookup instead of tuple
    comparison in a Python loop.
    """
    n_rows, n_cols = grid.shape
    sig_grid = np.zeros_like(grid, dtype=np.int64)
    bit = 0
    for dr in range(-window, window + 1):
        for dc in range(-window, window + 1):
            shifted = np.roll(np.roll(grid, -dr, axis=0), -dc, axis=1)
            sig_grid = sig_grid | (shifted.astype(np.int64) << bit)
            bit += 1
    return sig_grid


def signature_to_int(sig_tuple):
    """Convert a tuple-based signature (as used in the original,
    unvectorized code) to the same integer encoding as encode_signature_grid,
    for consistency between the two representations."""
    val = 0
    for i, bit_val in enumerate(sig_tuple):
        val |= (bit_val << i)
    return val


def pattern_reappears_nearby_vectorized(sig_grid, center_r, center_c, target_sig_int, radius):
    """
    Vectorized replacement for pattern_reappears_nearby: checks whether
    target_sig_int appears anywhere in a (2*radius+1)^2 neighborhood of
    (center_r, center_c) in the PRECOMPUTED sig_grid, using a single
    numpy slice + comparison instead of a nested Python loop.
    """
    n_rows, n_cols = sig_grid.shape
    row_idx = np.arange(center_r - radius, center_r + radius + 1) % n_rows
    col_idx = np.arange(center_c - radius, center_c + radius + 1) % n_cols
    window = sig_grid[np.ix_(row_idx, col_idx)]
    return bool(np.any(window == target_sig_int))


if __name__ == "__main__":
    # Sanity check: vectorized encoding + lookup must match the original
    # tuple-based signature() and pattern_reappears_nearby() exactly.
    import sys
    sys.path.insert(0, '.')
    from stage1_coherence_memory import signature, pattern_reappears_nearby

    rng = np.random.default_rng(0)
    grid = (rng.random((30, 30)) < 0.3).astype(int)

    sig_grid = encode_signature_grid(grid, window=1)

    mismatches = 0
    for r in range(30):
        for c in range(30):
            tuple_sig = signature(grid, r, c, window=1)
            int_sig = signature_to_int(tuple_sig)
            if sig_grid[r, c] != int_sig:
                mismatches += 1

    print(f"Signature encoding mismatches (should be 0): {mismatches}")
    assert mismatches == 0, "FAIL: vectorized signature encoding doesn't match original"

    # check pattern_reappears_nearby agreement on a sample of cells
    radius = 5
    disagreements = 0
    for r, c in [(5, 5), (10, 12), (20, 3), (0, 0), (29, 29)]:
        target_tuple = signature(grid, r, c, window=1)
        target_int = signature_to_int(target_tuple)

        original_result = pattern_reappears_nearby(grid, r, c, target_tuple, radius)
        vectorized_result = pattern_reappears_nearby_vectorized(sig_grid, r, c, target_int, radius)

        if original_result != vectorized_result:
            disagreements += 1
            print(f"  MISMATCH at ({r},{c}): original={original_result}, vectorized={vectorized_result}")

    print(f"pattern_reappears_nearby disagreements (should be 0): {disagreements}")
    assert disagreements == 0, "FAIL: vectorized pattern search doesn't match original"
    print("PASS: vectorized signature encoding and pattern search match the original exactly.")
