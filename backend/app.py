from flask import Flask, jsonify, request
import hashlib
import numpy as np
from flask_cors import CORS
import json
import requests
from collections import Counter
from functools import lru_cache
app = Flask(__name__)
CORS(app)
HEADERS = {'User-Agent': 'LithosExplorer/1.0 (+https://github.com/your-repo/lithos-explorer)'}
# Load minerals.json
with open('minerals.json', 'r') as f:
    minerals_data = json.load(f)
# Build MINERAL_COLORS from JSON
MINERAL_COLORS = {
    'void': (255, 255, 255), # White (porosity)
    'cover': (165, 42, 42) # Brown for mining cover (fallback, not in JSON)
}
for name, data in minerals_data['minerals'].items():
    MINERAL_COLORS[name] = tuple(data['color'])
# Build DEPTH_LAYERS from JSON prob_layers
layers_map = {
    "0-10": (0, 10),
    "11-35": (11, 35),
    "36-inf": (36, float('inf'))
}
DEPTH_LAYERS = {}
for layer_key, layer_range in layers_map.items():
    probs = {}
    for name, data in minerals_data['minerals'].items():
        prob = data.get('prob_layers', {}).get(layer_key, 0.0)
        if prob > 0:
            probs[name] = prob
    # Add void probabilities (fixed, as they are not in JSON)
    probs['void'] = 0.1 if layer_range[0] < 36 else 0.05
    DEPTH_LAYERS[layer_range] = probs
# Tectonic plates cache
PLATES_GEOJSON = None
def load_tectonic_plates():
    global PLATES_GEOJSON
    if PLATES_GEOJSON is not None:
        return PLATES_GEOJSON
    try:
        with open('tectonic_plates.json', 'r') as f:
            PLATES_GEOJSON = json.load(f)
        print("Tectonic plates loaded from local file")
    except FileNotFoundError:
        print("Local tectonic_plates.json not found, falling back to URL")
        try:
            url = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/PB2002_plates.json"
            resp = requests.get(url, timeout=15)
            if resp.ok:
                PLATES_GEOJSON = resp.json()
                print("Tectonic plates loaded successfully from URL")
            else:
                PLATES_GEOJSON = None
        except Exception as e:
            print(f"Failed to load tectonic plates from URL: {e}")
            PLATES_GEOJSON = None
    return PLATES_GEOJSON
def point_in_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside
def get_plate_type(lat, lon):
    plates = load_tectonic_plates()
    if not plates:
        return None
    for feature in plates.get('features', []):
        geom = feature['geometry']
        plate_name = feature['properties'].get('PlateName', '').lower()
        coords = []
        if geom['type'] == 'Polygon':
            coords = [geom['coordinates'][0]]
        elif geom['type'] == 'MultiPolygon':
            coords = [poly[0] for poly in geom['coordinates']]
        for poly in coords:
            # poly is list of [lon, lat] → x=lon, y=lat → pass directly!
            if point_in_polygon(lon, lat, poly):
                return plate_name
    return None
@lru_cache(maxsize=100000)
def get_mineral_type_no_bias(seed: str, x: int, y: int, z: int, prob_offsets_tuple: tuple = (), allowed_minerals_tuple: tuple = ()):
    """Determine mineral at (x,y,z) using seeded SHA-256 hash, without vein bias"""
    prob_offsets = dict(prob_offsets_tuple)
    allowed_minerals = list(allowed_minerals_tuple)
    input_str = f"{seed}:{x}:{y}:{z}"
    hash_digest = hashlib.sha256(input_str.encode()).digest()
    hash_int = int.from_bytes(hash_digest[-8:], 'big')
    normalized = hash_int / (2 ** 64)
    # Find depth layer
    layer_probs = None
    layer_key = None # Added for layer-specific boosts
    for lk, (min_z, max_z) in layers_map.items(): # Use layers_map for key lookup
        if min_z <= z < max_z:
            layer_key = lk
            layer_probs = DEPTH_LAYERS[(min_z, max_z)].copy()
            break
    if not layer_probs:
        return 'void'
    # Apply location-based offsets
    for mineral, offset in prob_offsets.items():
        if mineral in layer_probs:
            layer_probs[mineral] = max(0, layer_probs[mineral] + offset)
    # Optional cluster boosts using 'related_minerals' (toggle here for dev)
    if False: # Set to True to enable; default False for realism priority
        associated_boost = 0.03 # Lowered for balance
        mineral_keys = list(minerals_data['minerals'].keys())
        for mineral, offset in list(prob_offsets.items()):
            if offset > 0 and mineral in minerals_data['minerals']:
                related = minerals_data['minerals'][mineral].get('related_minerals', [])
                if not isinstance(related, list): # Safeguard if malformed
                    continue
                boost_scale = 2.0 if layer_key == "36-inf" else 1.0 # Stronger in deep layers
                for rel in related:
                    rel_lower = rel.lower()
                    for min_key in list(layer_probs.keys()): # Only boost if in layer_probs
                        if min_key.lower() == rel_lower or rel_lower in min_key.lower():
                            layer_probs[min_key] = max(0, layer_probs[min_key] + associated_boost * boost_scale)
    # Filter if restricted
    if allowed_minerals:
        layer_probs = {k: v for k, v in layer_probs.items() if k in allowed_minerals}
    total = sum(layer_probs.values())
    if total <= 0:
        return 'void'
    # Renormalize after boosts (minor tweak for balance)
    for mineral in layer_probs:
        layer_probs[mineral] /= total
    total = sum(layer_probs.values()) # Should be ~1 now
    # Build cumulative distribution
    cum = 0.0
    cumulative = []
    for mineral in sorted(layer_probs.keys()):
        prob = layer_probs[mineral] / total
        cum += prob
        cumulative.append((cum, mineral))
    # Select mineral
    for threshold, mineral in cumulative:
        if normalized < threshold:
            return mineral
    return cumulative[-1][1] # Fallback
def generate_3d_chunk(seed, size, x_offset=0, y_offset=0, z_offset=0, prob_offsets=None, allowed_minerals=None, use_vein_bias=True):
    if prob_offsets is None:
        prob_offsets = {}
    if allowed_minerals is None:
        allowed_minerals = []
    # Prepare hashable args for cache
    prob_offsets_tuple = tuple(sorted(prob_offsets.items()))
    allowed_minerals_tuple = tuple(sorted(allowed_minerals))
    # Initial chunk without bias
    chunk = [
        [
            [
                get_mineral_type_no_bias(seed, x + x_offset, y + y_offset, z + z_offset, prob_offsets_tuple, allowed_minerals_tuple)
                for z in range(size)
            ]
            for y in range(size)
        ]
        for x in range(size)
    ]
    if not use_vein_bias:
        return chunk
    # Helper to get layer key from gz
    def get_layer_key(gz):
        if 0 <= gz < 10:
            return "0-10"
        elif 10 <= gz < 35:
            return "11-35"
        else:
            return "36-inf"
    # Helper to get neighbors within bounds
    def get_neighbors(ix, iy, iz):
        candidates = [
            (ix+1, iy, iz), (ix-1, iy, iz),
            (ix, iy+1, iz), (ix, iy-1, iz),
            (ix, iy, iz+1), (ix, iy, iz-1)
        ]
        return [(nx, ny, nz) for nx, ny, nz in candidates if 0 <= nx < size and 0 <= ny < size and 0 <= nz < size]
    # Iterative biasing
    max_iterations = 5 # Number of iterations for convergence
    for _ in range(max_iterations):
        new_chunk = [[[None for _ in range(size)] for _ in range(size)] for _ in range(size)]
        for lx in range(size):
            for ly in range(size):
                for lz in range(size):
                    # Get base probs
                    gz = lz + z_offset # Global z
                    layer_probs = None
                    for (min_z, max_z), probs in DEPTH_LAYERS.items():
                        if min_z <= gz < max_z:
                            layer_probs = probs.copy()
                            break
                    if not layer_probs:
                        new_chunk[lx][ly][lz] = 'void'
                        continue
                    # Apply offsets
                    for mineral, offset in prob_offsets.items():
                        if mineral in layer_probs:
                            layer_probs[mineral] = max(0, layer_probs[mineral] + offset)
                    # Filter allowed
                    if allowed_minerals:
                        layer_probs = {k: v for k, v in layer_probs.items() if k in allowed_minerals}
                    # Apply vein bias based on current chunk neighbors
                    neighbors = get_neighbors(lx, ly, lz)
                    layer_key = get_layer_key(gz)
                    for nx, ny, nz in neighbors:
                        n_mineral = chunk[nx][ny][nz]
                        if n_mineral in minerals_data['minerals']:
                            mineral_data = minerals_data['minerals'][n_mineral]
                            if 'vein_boost_layers' in mineral_data:
                                boost = mineral_data['vein_boost_layers'].get(layer_key)
                                if boost is not None and boost > 0 and n_mineral in layer_probs:
                                    layer_probs[n_mineral] += boost
                    # Normalize and select (same as in get_mineral_type_no_bias)
                    total = sum(layer_probs.values())
                    if total <= 0:
                        new_chunk[lx][ly][lz] = 'void'
                        continue
                    # Get normalized from hash (same as before)
                    gx = lx + x_offset
                    gy = ly + y_offset
                    input_str = f"{seed}:{gx}:{gy}:{gz}"
                    hash_digest = hashlib.sha256(input_str.encode()).digest()
                    hash_int = int.from_bytes(hash_digest[-8:], 'big')
                    normalized = hash_int / (2 ** 64)
                    # Cumulative
                    cum = 0.0
                    cumulative = []
                    for mineral in sorted(layer_probs.keys()):
                        prob = layer_probs[mineral] / total
                        cum += prob
                        cumulative.append((cum, mineral))
                    # Select
                    selected = cumulative[-1][1] # Fallback
                    for threshold, mineral in cumulative:
                        if normalized < threshold:
                            selected = mineral
                            break
                    new_chunk[lx][ly][lz] = selected
        chunk = new_chunk
    return chunk
def generate_2d_slice(seed, size, z, x_offset=0, y_offset=0, prob_offsets=None, allowed_minerals=None):
    if prob_offsets is None:
        prob_offsets = {}
    if allowed_minerals is None:
        allowed_minerals = []
    prob_offsets_tuple = tuple(sorted(prob_offsets.items()))
    allowed_minerals_tuple = tuple(sorted(allowed_minerals))
    return [
        [
            get_mineral_type_no_bias(seed, x + x_offset, y + y_offset, z, prob_offsets_tuple, allowed_minerals_tuple)
            for y in range(size)
        ]
        for x in range(size)
    ]
def generate_slice(seed, size, z_offset=0, x_offset=0, y_offset=0, zoom=1, prob_offsets=None):
    """
    Generate a 2D numpy array of colors for the slice at z.
    """
    if prob_offsets is None:
        prob_offsets = {}
    prob_offsets_tuple = tuple(sorted(prob_offsets.items()))
    effective_size = size // zoom
    if effective_size <= 0:
        return np.zeros((size, size, 3), dtype=np.uint8) # Fallback to black
    small_grid = np.zeros((effective_size, effective_size, 3), dtype=np.uint8)
    for x in range(effective_size):
        for y in range(effective_size):
            mineral = get_mineral_type_no_bias(seed, x_offset + x, y_offset + y, z_offset, prob_offsets_tuple)
            small_grid[y, x] = MINERAL_COLORS[mineral] # Note: For pygame or similar
    grid = np.repeat(small_grid, zoom, axis=0)
    grid = np.repeat(grid, zoom, axis=1)
    # If not exact size, pad with black
    if grid.shape[0] < size:
        padded = np.zeros((size, size, 3), dtype=np.uint8)
        padded[:grid.shape[0], :grid.shape[1]] = grid
        grid = padded
    return grid
def get_offsets_from_location(location: str):
    hash_obj = hashlib.sha256(location.encode())
    hash_bytes = hash_obj.digest()
    x_offset = int.from_bytes(hash_bytes[0:4], 'big') % (1 << 30)
    y_offset = int.from_bytes(hash_bytes[4:8], 'big') % (1 << 30)
    z_offset = int.from_bytes(hash_bytes[8:12], 'big') % (1 << 30)
    crust_type = "continental"
    prob_offsets = {}
    elevation = 0  # Safe default
    lat, lon = None, None
    minerals_counter = Counter()
    plate = None

    # Build debug_info incrementally to avoid reference errors
    debug_info = {'location': location}

    use_mindat = False  # Toggle: Set to True to use Mindat API instead of MRDS for testing

    MINDAT_API_KEY = ""  # Set your Mindat API key here if using Mindat

    try:
        # Geocoding
        if ',' in location.strip():
            parts = [p.strip() for p in location.split(',')]
            lat, lon = float(parts[0]), float(parts[1])
        else:
            url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.ok and resp.json():
                debug_info['geocoding_response'] = resp.json()
                data = resp.json()[0]
                lat, lon = float(data['lat']), float(data['lon'])
        debug_info['lat'] = lat
        debug_info['lon'] = lon
        if lat is None or lon is None:
            raise ValueError("Geocoding failed")

        # Elevation (fixed URL: use comma for single location)
        elev_resp = requests.get(
            f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}",
            timeout=10
        )
        if elev_resp.ok and elev_resp.json().get('results'):
            debug_info['elevation_response'] = elev_resp.json()
            elevation = elev_resp.json()['results'][0]['elevation']
        debug_info['elevation'] = elevation  # Update after assignment
        if elevation > 3000:
            prob_offsets['void'] = prob_offsets.get('void', 0) + 0.1
            prob_offsets['mica'] = prob_offsets.get('mica', 0) + 0.08
            prob_offsets['granite'] = prob_offsets.get('granite', 0) + 0.1
        elif elevation > 1000:
            prob_offsets['void'] = prob_offsets.get('void', 0) + 0.05
            prob_offsets['granite'] = prob_offsets.get('granite', 0) + 0.05
        elif elevation < -200:
            crust_type = "oceanic"
            prob_offsets['basalt'] = 0.35
            prob_offsets['pyroxene'] = 0.25

        # Tectonic Plate
        plate = get_plate_type(lat, lon)
        debug_info['plate_type'] = plate  # After assignment
        debug_info['tectonic_plates_response'] = 'Loaded successfully' if PLATES_GEOJSON else 'Failed to load'
        if plate and ('subduction' in plate or 'convergent' in plate or 'andes' in plate or 'pacific' in plate or 'nazca' in plate):
            crust_type = "volcanic_subduction"
            prob_offsets['basalt'] = prob_offsets.get('basalt', 0) + 0.2
            prob_offsets['pyroxene'] = prob_offsets.get('pyroxene', 0) + 0.15
            prob_offsets['gold'] = prob_offsets.get('gold', 0) + 0.05
            prob_offsets['copper'] = prob_offsets.get('copper', 0) + 0.08

        # Mineral Deposits
        if use_mindat:
            if not MINDAT_API_KEY:
                print("Mindat API key not set. Skipping Mindat query.")
            else:
                mindat_headers = {"Authorization": f"Token {MINDAT_API_KEY}"}
                # Query localities in a box (±1 degree)
                localities_url = f"https://api.mindat.org/localities/?lat__gte={lat-1}&lat__lte={lat+1}&lon__gte={lon-1}&lon__lte={lon+1}&limit=20"
                resp = requests.get(localities_url, headers=mindat_headers, timeout=10)
                if resp.ok:
                    debug_info['mindat_localities_response'] = resp.json()
                    localities = resp.json().get('results', [])
                    for loc in localities:
                        loc_id = loc['id']
                        # Query minerals for this locality
                        minerals_url = f"https://api.mindat.org/minerals/?locality={loc_id}"
                        miner_resp = requests.get(minerals_url, headers=mindat_headers, timeout=10)
                        if miner_resp.ok:
                            minerals = miner_resp.json().get('results', [])
                            for minr in minerals:
                                name = minr.get('name', '').lower()
                                if name:
                                    minerals_counter[name] += 1  # Count occurrences
                else:
                    print(f"Mindat localities query failed: {resp.status_code}")
        else:
            # Use MRDS (original)
            mrds_url = f"https://mrdata.usgs.gov/mrds/search-bbox.php?min_lat={lat-1}&max_lat={lat+1}&min_lon={lon-1}&max_lon={lon+1}&format=json"
            try:
                resp = requests.get(mrds_url, timeout=8)
                if resp.ok:
                    debug_info['mrds_response'] = resp.json()
                    data = resp.json()
                    for f in data.get('features', []):
                        dep_size = f['properties'].get('dep_size', 'M')
                        size_factor = {'L': 3, 'M': 2, 'S': 1}.get(dep_size.upper(), 1)
                        comm = f['properties'].get('commodity', '')
                        comms = [m.strip().lower() for m in comm.split(',') if m.strip()]
                        for c in comms:
                            minerals_counter[c] += size_factor
            except:
                pass

        debug_info['minerals_counter'] = dict(minerals_counter)  # After processing

        # Apply mineral boosts dynamically using minerals.json
        if minerals_counter:
            common = minerals_counter.most_common(8)
            total_mentions = sum(minerals_counter.values())
            mineral_keys = list(minerals_data['minerals'].keys())
            for name, count in common:
                boost = 0.18 * (count / total_mentions)
                matched = False
                for target in mineral_keys:
                    if name in target or target in name: # Simple string containment match
                        prob_offsets[target] = prob_offsets.get(target, 0) + boost
                        matched = True
                # Optional: Fallback mappings for unmatched (minimal listing)
                if not matched:
                    fallback_mapping = {
                        'platinum': 'gold',
                        'nickel': 'copper',
                        'uranium': 'iron_ore',
                        'coal': 'mica' # Example for coal
                    }
                    if name in fallback_mapping:
                        target = fallback_mapping[name]
                        if target in mineral_keys:
                            prob_offsets[target] = prob_offsets.get(target, 0) + boost
    except Exception as e:
        print(f"[Geology Engine] Fallback mode for {location}: {e}")

    # Final crust type decision (runs even if some APIs failed)
    # If we have a strong basalt signal, we're probably on oceanic or volcanic crust
    if prob_offsets.get('basalt', 0) > 0.25:
        crust_type = "oceanic" if elevation < 0 else "volcanic"
    elif crust_type == "volcanic_subduction":
        # Keep the more specific subduction type if we detected it
        pass
    return x_offset, y_offset, z_offset, crust_type, prob_offsets, debug_info
@app.route('/api/offsets', methods=['GET'])
def api_get_offsets():
    location = request.args.get('location', '').strip()
    if not location:
        return jsonify({'error': 'Missing location parameter'}), 400
    x_offset, y_offset, z_offset, crust_type, prob_offsets, debug_info = get_offsets_from_location(location)
    response = {
        'x_offset': x_offset,
        'y_offset': y_offset,
        'z_offset': z_offset,
        'crust_type': crust_type,
        'prob_offsets': prob_offsets
    }
    if request.args.get('debug', 'false').lower() == 'true':
        response['debug_info'] = debug_info
    return jsonify(response)
@app.route('/api/mineral', methods=['GET'])
def api_get_mineral():
    try:
        seed = request.args.get('seed', 'default_seed')
        x = int(request.args.get('x', 0))
        y = int(request.args.get('y', 0))
        z = int(request.args.get('z', 0))
        mineral = get_mineral_type_no_bias(seed, x, y, z)
        return jsonify({'mineral': mineral})
    except ValueError:
        return jsonify({'error': 'Invalid coordinates'}), 400
   
@app.route('/api/chunk3d', methods=['GET'])
def api_generate_3d_chunk():
    try:
        seed = request.args.get('seed', 'default_seed')
        size = min(int(request.args.get('size', 32)), 128)
        chunk_x = int(request.args.get('chunk_x', 0))
        chunk_y = int(request.args.get('chunk_y', 0))
        chunk_z = int(request.args.get('chunk_z', 0))
        x_offset = int(request.args.get('x_offset', 0)) + size * chunk_x
        y_offset = int(request.args.get('y_offset', 0)) + size * chunk_y
        z_offset = int(request.args.get('z_offset', 0)) + size * chunk_z
        prob_offsets = json.loads(request.args.get('prob_offsets', '{}'))
        allowed = json.loads(request.args.get('allowed_minerals', '[]')) or None
        use_vein_bias = request.args.get('use_vein_bias', 'True').lower() == 'true'
        chunk = generate_3d_chunk(seed, size, x_offset, y_offset, z_offset, prob_offsets, allowed, use_vein_bias)
        response = {'chunk': chunk}
        if request.args.get('debug', 'false').lower() == 'true':
            response['debug_info'] = {
                'seed': seed,
                'offsets': {'x': x_offset, 'y': y_offset, 'z': z_offset},
                'prob_offsets': prob_offsets,
                'allowed_minerals': allowed,
                'use_vein_bias': use_vein_bias
            }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
@app.route('/api/slice2d', methods=['GET'])
def api_generate_2d_slice():
    try:
        seed = request.args.get('seed', 'default_seed')
        size = int(request.args.get('size', 100))
        z = int(request.args.get('z', 0))
        x_offset = int(request.args.get('x_offset', 0))
        y_offset = int(request.args.get('y_offset', 0))
        prob_offsets = json.loads(request.args.get('prob_offsets', '{}'))
        allowed = json.loads(request.args.get('allowed_minerals', '[]')) or None
        slice_data = generate_2d_slice(seed, size, z, x_offset, y_offset, prob_offsets, allowed)
        return jsonify(slice_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
if __name__ == '__main__':
    app.run(debug=True, port=5000)
