

# # need to take input like 
# # {"(Mg,Fe)₂SiO₄":"3","(Zn,Fe)S":"3","Ag":"1","Al2O3":"2","Aluminum, silicon, fluorine, and oxygen":"3", ...

# # and change the master vocab.json from the simple
# {
    # "Chemistry": {
        # "(Mg,Fe)₂SiO₄": "The chemical formula for olivine, a solid solution series of magnesium-iron silicates.",
        

# # to apply the difficulty level
# {
    # "Chemistry": {
        # "(Mg,Fe)₂SiO₄": {"definition": "The chemical formula for olivine, a solid solution series of magnesium-iron silicates.",
                        # "level": "3"
                        # }




import json

# Hardcoded paths and category
master_path = 'frontend/public/vocab.json'
updates_path = 'scripts/json_used_for_recategorizing_vocab/levels.json'
category_to_update = "Petrology"  #Mining and Extraction Hardcoded category to update

# Load the master JSON
with open(master_path, 'r', encoding='utf-8') as f:
    master = json.load(f)

# Load the updates JSON (levels)
with open(updates_path, 'r', encoding='utf-8') as f:
    updates = json.load(f)

# Update only the specified category
if category_to_update in master:
    section = master[category_to_update]
    for term, definition in list(section.items()):  # Use list to avoid runtime modification issues
        if isinstance(definition, str):  # Only update if it's currently a string
            if term in updates:
                level = updates[term]
                section[term] = {
                    "definition": definition,
                    "level": level
                }
            # If term not in updates, we leave it as string or could add default level, but per request, only apply where provided

# Save the updated master back to the same path
with open(master_path, 'w', encoding='utf-8') as f:
    json.dump(master, f, indent=4, ensure_ascii=False)

print(f"Master vocab.json updated successfully for category '{category_to_update}'.")
