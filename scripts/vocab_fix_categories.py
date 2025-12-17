import json
import os
from collections import defaultdict

# Hardcoded paths
master_path = 'frontend/public/vocab.json'
updates_path = 'scripts/json_used_for_recategorizing_vocab/vocab_partial_updates.json'

# Load master JSON
try:
    with open(master_path, 'r') as f:
        master = json.load(f)
except FileNotFoundError:
    print(f"Master file '{master_path}' not found.")
    exit(1)
except json.JSONDecodeError:
    print(f"Invalid JSON in '{master_path}'.")
    exit(1)

# Load updates JSON
try:
    with open(updates_path, 'r') as f:
        updates = json.load(f)
except FileNotFoundError:
    print(f"Updates file '{updates_path}' not found.")
    exit(1)
except json.JSONDecodeError:
    print(f"Invalid JSON in '{updates_path}'.")
    exit(1)

# Check if all categories in updates exist in master
missing_categories = [cat for cat in updates if cat not in master]
if missing_categories:
    print("Warning: The following categories do not exist in the master JSON: " + ", ".join(missing_categories))
    print("No updates will be made to the master vocab.json.")
    exit(0)

# Proceed with recategorizing: move terms to new categories
term_to_placements = defaultdict(dict)
for new_cat, terms in updates.items():
    seen_lower = set()
    if isinstance(terms, list):
        for term in terms:
            lower = term.lower()
            if lower in seen_lower:
                print(f"Duplicate term '{term}' (case-insensitive) found in category '{new_cat}'.")
                continue
            seen_lower.add(lower)
            term_to_placements[term][new_cat] = None
    elif isinstance(terms, dict):
        for term, desc in terms.items():
            lower = term.lower()
            if lower in seen_lower:
                print(f"Duplicate term '{term}' (case-insensitive) found in category '{new_cat}'.")
                continue
            seen_lower.add(lower)
            term_to_placements[term][new_cat] = desc
    else:
        print(f"Invalid format in updates for category '{new_cat}'.")
        continue

# Now, process each term
all_terms = list(term_to_placements.keys())
for term in all_terms:
    # Collect old categories and descriptions
    old_cats = []
    old_descs = []
    for old_cat in list(master.keys()):
        if not isinstance(master[old_cat], dict):
            continue
        conflicting_key = next((k for k in master[old_cat] if k.lower() == term.lower()), None)
        if conflicting_key:
            old_descs.append(master[old_cat][conflicting_key])
            old_cats.append(old_cat)
    # Remove from old categories (using exact matching keys)
    for old_cat in old_cats:
        conflicting_key = next((k for k in master[old_cat] if k.lower() == term.lower()), None)
        if conflicting_key:
            del master[old_cat][conflicting_key]
        if not master[old_cat]:
            del master[old_cat]
    # Handle descriptions for new placements
    placements = term_to_placements[term]
    none_count = sum(1 for desc in placements.values() if desc is None)
    if none_count > 0:
        if len(old_descs) == 1:
            single_desc = old_descs[0]
            for cat in placements:
                if placements[cat] is None:
                    placements[cat] = single_desc
        elif len(old_descs) == none_count:
            # Assign old descs to none placements in sorted category order
            none_cats = sorted([cat for cat, desc in placements.items() if desc is None])
            for i, cat in enumerate(none_cats):
                placements[cat] = old_descs[i]
        else:
            print(f"Warning for term '{term}': {len(old_descs)} old descriptions, but {none_count} placements without desc. Using empty for None.")
            for cat in placements:
                if placements[cat] is None:
                    placements[cat] = ""
    # Add to new categories
    for new_cat, desc in placements.items():
        if new_cat not in master:
            master[new_cat] = {}
        conflicting_key = next((k for k in master[new_cat] if k.lower() == term.lower()), None)
        if conflicting_key:
            print(f"Alert: Case-insensitive duplicate in '{new_cat}':")
            print(f"1. Existing: {conflicting_key} - {master[new_cat][conflicting_key]}")
            print(f"2. New: {term} - {desc}")
            while True:
                choice = input("Enter 1 or 2 to select which to keep: ")
                if choice == '1':
                    # Skip adding
                    break
                elif choice == '2':
                    del master[new_cat][conflicting_key]
                    master[new_cat][term] = desc
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        else:
            master[new_cat][term] = desc

# Write updated master back to file
try:
    # Backup original
    backup_path = master_path + '.bak'
    if os.path.exists(master_path):
        os.rename(master_path, backup_path)
    with open(master_path, 'w') as f:
        json.dump(master, f, indent=4)
    print(f"Master file updated successfully. Backup created at '{backup_path}'.")
except Exception as e:
    print(f"Error writing to '{master_path}': {e}")
