import numpy as np
from scipy import ndimage
import statistics

N = 50
MAX_STEPS = 5000
NOISE_RATE = 0.0008
NOISE_INTERVAL = 5

def conway_step(grid):
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    neighbors = ndimage.convolve(grid, kernel, mode='wrap')
    next_grid = np.zeros_like(grid)
    next_grid[(grid == 1) & ((neighbors == 2) | (neighbors == 3))] = 1
    next_grid[(grid == 0) & (neighbors == 3)] = 1
    return next_grid

def add_entropy(grid, noise_rate, rng):
    mask = rng.random(grid.shape) < noise_rate
    return np.logical_xor(grid, mask).astype(int)

def active_persistence_filter(grid):
    filtered_grid = grid.copy()
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    neighbor_count = ndimage.convolve(grid, kernel, mode='wrap')
    noise_mask = (grid == 1) & (neighbor_count < 2)
    filtered_grid[noise_mask] = 0
    return filtered_grid

def init_seed(size=N):
    grid = np.zeros((size, size), dtype=int)
    glider = np.array([[0,1,0],[0,0,1],[1,1,1]])
    grid[5:8, 5:8] = glider
    grid[15:18, 25:28] = glider
    grid[35:38, 10:13] = glider
    block = np.array([[1,1],[1,1]])
    grid[10:12, 40:42] = block
    grid[40:42, 40:42] = block
    return grid

def run_simulation(use_filter, seed_val):
    rng = np.random.default_rng(seed_val)
    grid = init_seed()
    for step in range(MAX_STEPS):
        grid = conway_step(grid)
        if step % NOISE_INTERVAL == 0:
            grid = add_entropy(grid, NOISE_RATE, rng)
        if use_filter:
            grid = active_persistence_filter(grid)
        total_cells = grid.sum()
        if total_cells == 0 or total_cells == N * N:
            return step
    return MAX_STEPS

if __name__ == "__main__":
    print("Executing Axiom 3 Entropic Decay Lifespan Test (20 Trials)...")
    control_lifespans = []
    filtered_lifespans = []
    for trial in range(20):
        t_control = run_simulation(use_filter=False, seed_val=1000 + trial)
        t_filtered = run_simulation(use_filter=True, seed_val=1000 + trial)
        control_lifespans.append(t_control)
        filtered_lifespans.append(t_filtered)
    print("\nRESULTS SUMMARY:")
    print(f"Control Lifespan (No Filter)  Mean: {statistics.mean(control_lifespans):.1f} steps (std: {statistics.pstdev(control_lifespans):.1f})")
    print(f"Filtered Lifespan (Active P)  Mean: {statistics.mean(filtered_lifespans):.1f} steps (std: {statistics.pstdev(filtered_lifespans):.1f})")
    diffs = [f - c for c, f in zip(control_lifespans, filtered_lifespans)]
    mean_diff = statistics.mean(diffs)
    std_diff = statistics.pstdev(diffs)
    t_stat = mean_diff / (std_diff / (len(diffs)**0.5)) if std_diff > 0 else float('inf')
    print(f"\nLifespan Extension Delta (Delta-T): {mean_diff:+.1f} steps")
    print(f"Paired t-statistic: {t_stat:.3f}")
