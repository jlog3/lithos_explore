from flask import Flask, jsonify, request
from lithos_cipher.core import generate_3d_chunk, generate_2d_slice, get_mineral_type, get_offsets_from_location

app = Flask(__name__)

@app.route('/api/mineral', methods=['GET'])
def api_get_mineral():
    seed = request.args.get('seed', 'default_seed')
    x = int(request.args.get('x', 0))
    y = int(request.args.get('y', 0))
    z = int(request.args.get('z', 0))
    mineral = get_mineral_type(seed, x, y, z)
    return jsonify({'mineral': mineral})

@app.route('/api/chunk3d', methods=['GET'])
def api_generate_3d_chunk():
    seed = request.args.get('seed', 'default_seed')
    size = int(request.args.get('size', 32))
    x_offset = int(request.args.get('x_offset', 0))
    y_offset = int(request.args.get('y_offset', 0))
    z_offset = int(request.args.get('z_offset', 0))
    chunk = generate_3d_chunk(seed, size, x_offset, y_offset, z_offset)
    return jsonify(chunk)

@app.route('/api/slice2d', methods=['GET'])
def api_generate_2d_slice():
    seed = request.args.get('seed', 'default_seed')
    size = int(request.args.get('size', 100))
    z = int(request.args.get('z', 0))
    x_offset = int(request.args.get('x_offset', 0))
    y_offset = int(request.args.get('y_offset', 0))
    slice_data = generate_2d_slice(seed, size, z, x_offset, y_offset)
    return jsonify(slice_data)

# New: For region-specific mapping
@app.route('/api/offsets', methods=['GET'])
def api_get_offsets():
    location = request.args.get('location')
    if not location:
        return jsonify({'error': 'Missing location'}), 400
    x_offset, y_offset, z_offset = get_offsets_from_location(location)
    return jsonify({'x_offset': x_offset, 'y_offset': y_offset, 'z_offset': z_offset})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
