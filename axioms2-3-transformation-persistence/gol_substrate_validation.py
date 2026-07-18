"""
STAGE 1: 2D Game of Life substrate.

Before porting any E/A/memory machinery, verify the core step function
is correct against well-known GoL patterns: a blinker (period-2 oscillator)
and a glider (period-4 translating pattern). If these don't behave exactly
as documented, nothing built on top of this substrate is trustworthy.
"""

import numpy as np

def step(grid):
    """
    Standard GoL rules on a toroidal (wrapping) grid, using numpy roll
    for neighbor counting -- this is the well-established, easily-verified
    way to implement GoL, not a novel mechanism.
    Rules: live cell with 2-3 neighbors survives; dead cell with exactly
    3 neighbors becomes alive; all other cases -> dead.
    """
    neighbor_count = sum(
        np.roll(np.roll(grid, dx, axis=0), dy, axis=1)
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        if (dx, dy) != (0, 0)
    )
    return ((grid == 1) & ((neighbor_count == 2) | (neighbor_count == 3))) | \
           ((grid == 0) & (neighbor_count == 3))

def grid_to_str(grid):
    return "\n".join("".join("#" if c else "." for c in row) for row in grid)


def test_blinker():
    """Blinker: 3 cells in a row, oscillates between horizontal and vertical
    with period 2. Verify exact match against the known pattern."""
    grid = np.zeros((7, 7), dtype=int)
    grid[3, 2:5] = 1  # horizontal blinker
    print("Blinker t=0 (expect horizontal):")
    print(grid_to_str(grid))

    grid1 = step(grid).astype(int)
    print("\nBlinker t=1 (expect vertical):")
    print(grid_to_str(grid1))

    grid2 = step(grid1).astype(int)
    print("\nBlinker t=2 (expect horizontal again, matches t=0):")
    print(grid_to_str(grid2))

    assert np.array_equal(grid, grid2), "FAIL: blinker did not return to original state after period 2"
    print("\nPASS: blinker has correct period-2 oscillation.\n")


def test_glider():
    """Glider: canonical 5-cell pattern that translates by (1,1) every 4 steps.
    Verify it moves diagonally without changing shape after 4 steps."""
    grid = np.zeros((20, 20), dtype=int)
    # standard glider orientation
    glider_cells = [(1,2),(2,3),(3,1),(3,2),(3,3)]
    for r, c in glider_cells:
        grid[r, c] = 1

    print("Glider t=0:")
    print(grid_to_str(grid[0:6, 0:6]))

    g = grid.copy()
    for _ in range(4):
        g = step(g).astype(int)

    print("\nGlider t=4 (expect same shape, shifted by (1,1)):")
    print(grid_to_str(g[1:7, 1:7]))

    # check: shifting original glider region by (1,1) should match g region
    shifted_expected = np.zeros((20, 20), dtype=int)
    for r, c in glider_cells:
        shifted_expected[r+1, c+1] = 1

    assert np.array_equal(g, shifted_expected), "FAIL: glider did not translate correctly after 4 steps"
    print("\nPASS: glider translates correctly by (1,1) every 4 steps.\n")


if __name__ == "__main__":
    test_blinker()
    test_glider()
    print("All substrate sanity checks passed. Safe to build E/A/memory on top.")
