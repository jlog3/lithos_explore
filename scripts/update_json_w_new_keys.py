import json
import argparse
import os
import subprocess

# merges only new keys into existing minerals, preserving the rest of your JSON structure (including "minerals" and other top-level keys like "coverVariants").

# python update_json_w_new_keys.py --new /path/to/your_new_json_file.json 
#   optional [--master /path/to/your_master_json_file.json]

RED = '\033[91m'
RESET = '\033[0m'

def deep_merge(target, source, path=""):
    """
    Recursively merge source into target, adding new keys/subkeys and updating changed values.
    Returns lists of added and changed paths for tracking.
    """
    added = []
    changed = []
    for key, value in source.items():
        full_path = f"{path}.{key}" if path else key
        if key not in target:
            target[key] = value
            added.append(full_path)
        elif isinstance(target.get(key), dict) and isinstance(value, dict):
            sub_added, sub_changed = deep_merge(target[key], value, full_path)
            added.extend(sub_added)
            changed.extend(sub_changed)
        else:
            if target[key] != value:
                changed.append(full_path)
                target[key] = value  # Apply the change
    return added, changed

def get_required_schema(data_list):
    """
    Determine the required schema based on common keys and structures in the data_list.
    """
    if not data_list:
        return {}
    
    all_keys = set()
    for d in data_list:
        all_keys.update(d.keys())
    
    required_keys = [k for k in all_keys if all(k in d for d in data_list)]
    
    schema = {}
    for k in required_keys:
        values = [d[k] for d in data_list]
        has_none = None in values
        non_none_values = [v for v in values if v is not None]
        
        if not non_none_values:
            schema[k] = {'allow_none': True, 'type': None, 'sub': None}
            continue
        
        types = set(type(v) for v in non_none_values)
        if len(types) > 1:
            schema[k] = None  # Just presence
            continue
        
        t = list(types)[0]
        allow_none = has_none
        
        sub = None
        if t == dict:
            sub = get_required_schema(non_none_values)
        elif t == list:
            sub = None  # No deep check for lists
        
        schema[k] = {'type': t, 'sub': sub, 'allow_none': allow_none}
    
    return schema

def validate_against_schema(new_data, schema):
    """
    Validate new_data against the required schema, returning list of missing or incorrect items.
    """
    missing = []
    for key, sch in schema.items():
        if key not in new_data:
            missing.append(key)
            continue
        
        value = new_data[key]
        if sch is None:
            # Just presence required
            continue
        
        if value is None:
            if sch['allow_none']:
                continue
            else:
                missing.append(f"{key} (cannot be None)")
                continue
        
        # Check type
        if not isinstance(value, sch['type']):
            missing.append(f"{key} (wrong type, expected {sch['type'].__name__})")
            continue
        
        # If sub-schema, recurse
        if sch['sub'] is not None:
            sub_missing = validate_against_schema(value, sch['sub'])
            for sm in sub_missing:
                missing.append(f"{key}.{sm}")
    
    return missing

def main():
    # Set up argument parser for flexibility
    parser = argparse.ArgumentParser(description="Update master JSON file with new data.")
    parser.add_argument('--master', type=str, default='./frontend/public/minerals.json',
                        help="Path to the master JSON file (default: ./frontend/public/minerals.json)")
    parser.add_argument('--new', type=str, required=True,
                        help="Path to the new JSON file containing updates")
    args = parser.parse_args()

    master_file = args.master
    new_file = args.new

    # Check if files exist
    if not os.path.exists(master_file):
        print(f"Error: Master file '{master_file}' not found.")
        return
    if not os.path.exists(new_file):
        print(f"Error: New data file '{new_file}' not found.")
        return

    # Load master JSON
    try:
        with open(master_file, 'r') as f:
            master = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in master file '{master_file}': {e}")
        return
    except Exception as e:
        print(f"Error loading master file: {e}")
        return

    # Ensure 'minerals' key exists
    master['minerals'] = master.get('minerals', {})

    # Load new JSON
    try:
        with open(new_file, 'r') as f:
            new_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in new file '{new_file}': {e}")
        return
    except Exception as e:
        print(f"Error loading new file: {e}")
        return

    # Get existing minerals for schema
    existing_minerals = list(master['minerals'].values())
    required_schema = get_required_schema(existing_minerals)

    # Validate new minerals
    errors = {}
    new_minerals = set()
    if 'minerals' in new_data:
        for mineral, new_props in new_data['minerals'].items():
            if mineral not in master['minerals']:
                new_minerals.add(mineral)
                missing = validate_against_schema(new_props, required_schema)
                if missing:
                    errors[mineral] = missing

    if errors:
        print("Errors in new minerals:")
        for m, miss in errors.items():
            print(f"- {m}: Missing or incorrect: {', '.join(miss)}")
        print("No changes will be made.")
        return

    # Now apply merges and additions
    changes = {}
    if 'minerals' in new_data:
        for mineral, new_props in new_data['minerals'].items():
            is_new = mineral in new_minerals
            if is_new:
                master['minerals'][mineral] = {}
            mineral_data = master['minerals'][mineral]
            added, changed = deep_merge(mineral_data, new_props)
            if added or changed:
                changes[mineral] = {'added': added, 'changed': changed, 'is_new': is_new}

    # Propagate new top-level keys to all minerals with null
    new_top_keys = set()
    for info in changes.values():
        for a in info['added']:
            top_key = a.split('.')[0]
            new_top_keys.add(top_key)

    propagate_added = {}
    for key in new_top_keys:
        for mineral, mineral_data in master['minerals'].items():
            if key not in mineral_data:
                mineral_data[key] = None
                if mineral not in propagate_added:
                    propagate_added[mineral] = []
                propagate_added[mineral].append(key)

    # Update changes with propagations
    for mineral, adds in propagate_added.items():
        if mineral in changes:
            changes[mineral]['added'].extend(adds)
        else:
            changes[mineral] = {'added': adds, 'changed': [], 'is_new': False}

    # Display changes
    if changes:
        print("Proposed updates:")
        for mineral, info in changes.items():
            prefix = f"- {mineral}"
            if info.get('is_new', False):
                prefix += " (new mineral)"
            add_str = f"Added: {', '.join(info['added'])}" if info['added'] else ""
            change_str = f"Changed: {', '.join(info['changed'])}" if info['changed'] else ""
            if change_str:
                change_str = f"{RED}{change_str}{RESET}"
            separator = '; ' if add_str and change_str else ''
            print(f"{prefix}: {add_str}{separator}{change_str}")
    else:
        print("No new keys or changes to add.")
        return

    # Confirm save
    while True:
        confirm = input("Do you want to save these changes? (y/n): ").strip().lower()
        if confirm == 'y':
            try:
                with open(master_file, 'w') as f:
                    json.dump(master, f, indent=4)
                # Validate the written JSON
                with open(master_file, 'r') as f:
                    json.load(f)
                print(f"Success: Master file '{master_file}' updated and validated.")
                import subprocess
                subprocess.run(['python', 'scripts/sort_minerals_json.py', '--input', master_file])
            except json.JSONDecodeError as e:
                print(f"Error validating written JSON: {e}")
            except Exception as e:
                print(f"Error saving or validating master file: {e}")
            break
        elif confirm == 'n':
            print("Updates discarded.")
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()
