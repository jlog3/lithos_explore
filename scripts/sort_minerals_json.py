import json
import os
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser(description="Sort minerals JSON and copy to backend.")
    parser.add_argument('--input', type=str, default='./frontend/public/minerals.json',
                        help="Path to the input JSON file (default: ./frontend/public/minerals.json)")
    args = parser.parse_args()

    input_file = args.input

    # Ensure the directory exists (optional, but good practice)
    os.makedirs(os.path.dirname(input_file), exist_ok=True)

    with open(input_file, 'r') as f:
        data = json.load(f)

    # Assuming the structure has a "minerals" key with an object of minerals
    minerals = data.get("minerals", {})

    # Sort the mineral names (keys) alphabetically
    sorted_keys = sorted(minerals.keys())

    # Rebuild the minerals dict with sorted keys, preserving inner key order
    sorted_minerals = {k: minerals[k] for k in sorted_keys}
    data["minerals"] = sorted_minerals

    # Overwrite the input file with sorted data
    with open(input_file, 'w') as f:
        json.dump(data, f, indent=4)

    # Copy to backend
    destination_path = './backend/minerals.json'
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    shutil.copy(input_file, destination_path)
    print(f"File copied successfully from '{input_file}' to '{destination_path}'.")

if __name__ == "__main__":
    main()
