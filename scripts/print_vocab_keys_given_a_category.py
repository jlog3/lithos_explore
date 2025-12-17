import json

# Hardcoded file path
file_path = 'frontend/public/vocab.json'

# Hardcoded category
category = 'Technology and Applications' 

# Load data from JSON file
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"File '{file_path}' not found.")
    exit(1)
except json.JSONDecodeError:
    print(f"Invalid JSON in '{file_path}'.")
    exit(1)

# Check if the category exists in the data
if category in data:
    # Print all terms (keys) in alphabetical order without values
    for term in sorted(data[category]):
        print(term)
else:
    print(f"Category '{category}' not found.")
