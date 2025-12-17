import json
import os

# Hardcoded input and output files relative to the current working directory
input_file = './frontend/public/minerals.json'
output_file = './scripts/minerals_ex.json'

# Ensure the directories exist (optional, but good practice)
os.makedirs(os.path.dirname(input_file), exist_ok=True)
os.makedirs(os.path.dirname(output_file), exist_ok=True)
with open(input_file, 'r') as f:
    data = json.load(f)

# Assuming the structure has a "minerals" key with an object of minerals
minerals = data.get("minerals", {})

# Remove the specified keys from each mineral - Comment what you want to see
for mineral_data in minerals.values():
    mineral_data.pop("id", None)
    mineral_data.pop("name", None)
    mineral_data.pop("formula", None)
    mineral_data.pop("hardness", None)
    mineral_data.pop("color_variants", None)
    mineral_data.pop("crystal_system", None)
    mineral_data.pop("description", None)
    mineral_data.pop("location", None)
    mineral_data.pop("geological_significance", None)
    mineral_data.pop("sacred_frequency", None)
   
    mineral_data.pop("texture", None)
    mineral_data.pop("normalMap", None)
    mineral_data.pop("emissiveMap", None)
    mineral_data.pop("roughnessMap", None)
    mineral_data.pop("roughness", None)
    mineral_data.pop("metalness", None)
    mineral_data.pop("color", None)
    mineral_data.pop("prob_layers", None)
    mineral_data.pop("vein_boost_layers", None)
   
    mineral_data.pop("luster", None)
    mineral_data.pop("cleavage", None)
    mineral_data.pop("specific_gravity", None)
    mineral_data.pop("streak", None)
    mineral_data.pop("optical_properties", None)
    mineral_data.pop("chemical_composition", None)
    mineral_data.pop("associated_minerals", None)
    mineral_data.pop("formation_process", None)
    mineral_data.pop("rock_types", None)
    mineral_data.pop("industrial_uses", None)
    mineral_data.pop("modern_applications", None)
    mineral_data.pop("etymology", None)
    mineral_data.pop("historical_uses", None)
    mineral_data.pop("cultural_myths", None)
    mineral_data.pop("economic_value", None)
    mineral_data.pop("mining_methods", None)
    mineral_data.pop("environmental_impact", None)
    mineral_data.pop("health_aspects", None)
    mineral_data.pop("fun_facts", None)
    mineral_data.pop("related_minerals", None)
    mineral_data.pop("specimen_images", None)
    mineral_data.pop("rarity_index", None)
    # mineral_data.pop("educational_quiz_questions", None)
    mineral_data.pop("references", None)
    
    
    

    
# Remove the coverVariants key
data.pop("coverVariants", None)

# Sort the mineral names (keys) alphabetically
sorted_keys = sorted(minerals.keys())

# Rebuild the minerals dict with sorted keys, preserving inner key order
sorted_minerals = {k: minerals[k] for k in sorted_keys}
data["minerals"] = sorted_minerals

# Write to the output file
with open(output_file, 'w') as f:
    json.dump(data, f, indent=4)
