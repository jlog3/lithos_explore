import json

# Hardcoded filename
filename = './frontend/public/minerals.json'

# Load the JSON file
with open(filename, 'r') as file:
    data = json.load(file)

# Extract the minerals dictionary
minerals_dict = data.get('minerals', {})

# Print all mineral names
for mineral in minerals_dict.values():
    print(mineral['name'])
