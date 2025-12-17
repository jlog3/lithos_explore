import json

input_file = './frontend/public/minerals.json'

# Define the desired order of keys here. Rearrange the list as needed.
# Any keys not listed will be appended at the end.
desired_order = [
    "id",
    "name",
    "formula",
    "hardness",
    "color_variants",
    "crystal_system",
    "description",

    "location",
    "geological_significance",
    "sacred_frequency",
    "texture",
    "normalMap",
    "roughnessMap",
    "emissiveMap",
    "roughness",
    "metalness",
    "color",
    "prob_layers",
    "vein_boost_layers",
]

with open(input_file, 'r') as f:
    data = json.load(f)

for mineral_name, mineral in data['minerals'].items():
    new_mineral = {}
    for key in desired_order:
        if key in mineral:
            new_mineral[key] = mineral[key]
    # Add any extra keys not in desired_order at the end
    for key in mineral:
        if key not in desired_order:
            new_mineral[key] = mineral[key]
    data['minerals'][mineral_name] = new_mineral

with open(input_file, 'w') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

