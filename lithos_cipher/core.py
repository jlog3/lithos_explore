# lithos_cipher/core.py
import hashlib
import numpy as np
def get_mineral_type(seed, x, y, z):
    """
    Determine the mineral type at a point (x, y, z) using a cryptographic hash.
   
    Hashes the seed + coordinates, normalizes to [0,1), and assigns mineral types
    based on cumulative probability thresholds for heterogeneity.
   
    Thresholds (cumulative):
    - 0.0-0.4: void (empty space, for porosity)
    - 0.4-0.7: quartz (common)
    - 0.7-0.85: feldspar
    - 0.85-0.95: mica
    - 0.95-1.0: gold (rare veins)
   
    Args:
        seed (str): The seed for consistency.
        x, y, z (int): Coordinates to check.
   
    Returns:
        str: Mineral type.
    """
    input_str = f"{seed}:{x}:{y}:{z}"
    hash_obj = hashlib.sha256(input_str.encode())
    hash_int = int.from_bytes(hash_obj.digest()[-8:], 'big')
    normalized = hash_int / (2**64)
   
    if normalized < 0.4:
        return 'void'
    elif normalized < 0.7:
        return 'quartz'
    elif normalized < 0.85:
        return 'feldspar'
    elif normalized < 0.95:
        return 'mica'
    else:
        return 'gold'
# Mineral to color mapping (RGB) for visualizations
MINERAL_COLORS = {
    'void': (255, 255, 255), # White
    'quartz': (128, 128, 128), # Gray
    'feldspar': (255, 192, 203), # Pink
    'mica': (0, 0, 0), # Black
    'gold': (255, 215, 0) # Yellow
}
def generate_slice(seed, size, z_offset=0, x_offset=0, y_offset=0, zoom=1):
    """
    Generate a 2D numpy array of colors for the slice at z.
    """
    effective_size = size // zoom
    if effective_size <= 0:
        return np.zeros((size, size, 3), dtype=np.uint8)  # Fallback to black
    small_grid = np.zeros((effective_size, effective_size, 3), dtype=np.uint8)
    for x in range(effective_size):
        for y in range(effective_size):
            mineral = get_mineral_type(seed, x_offset + x, y_offset + y, z_offset)
            small_grid[y, x] = MINERAL_COLORS[mineral] # Note: For pygame or similar
    grid = np.repeat(small_grid, zoom, axis=0)
    grid = np.repeat(grid, zoom, axis=1)
    # If not exact size, pad with black
    if grid.shape[0] < size:
        padded = np.zeros((size, size, 3), dtype=np.uint8)
        padded[:grid.shape[0], :grid.shape[1]] = grid
        grid = padded
    return grid
