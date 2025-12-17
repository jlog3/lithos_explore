import json

# Hardcoded path to the JSON file
master_path = 'frontend/public/vocab.json'

# Load the JSON data from the file
with open(master_path, 'r') as f:
    json_data = json.load(f)

# List to hold keys that don't have 'definition' and 'level'
missing_keys = []

# Iterate over each category
for category, items in json_data.items():
    if isinstance(items, dict):
        for key, value in items.items():
            if not (isinstance(value, dict) and 'definition' in value and 'level' in value):
                # missing_keys.append(f"{category}: {key}")
                missing_keys.append(f"{key}")

# Print the list
print("Keys without 'definition' and 'level':")
for key in missing_keys:
    print(key)
