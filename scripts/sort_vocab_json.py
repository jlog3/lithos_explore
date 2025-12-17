import json
from pathlib import Path

VOCAB_PATH = Path("frontend/public/vocab.json")

def sort_keys(obj):
    if isinstance(obj, dict):
        return {k: sort_keys(obj[k]) for k in sorted(obj, key=str.lower)}
    elif isinstance(obj, list):
        return [sort_keys(item) for item in obj]
    else:
        return obj

def main():
    if not VOCAB_PATH.exists():
        raise FileNotFoundError(f"{VOCAB_PATH} does not exist")
    
    with VOCAB_PATH.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # Rewind and read lines to inspect the problematic spot
            f.seek(0)
            lines = f.readlines()
            if e.lineno <= len(lines):
                problematic_line = lines[e.lineno - 1]
                print(f"\nProblematic line {e.lineno}: {problematic_line.rstrip()}")
                print(" " * (e.colno - 1) + "^") # Pointer to the column
            return # Exit early since loading failed
    
    sorted_data = sort_keys(data)
    
    # Print entry counts per category
    print("Entry counts per category:")
    for category in sorted(sorted_data.keys(), key=str.lower):
        entries = sorted_data[category]
        if isinstance(entries, (list, dict)):
            count = len(entries)
        else:
            count = 0
        print(f"{category}: {count}")
    
    with VOCAB_PATH.open("w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=4, ensure_ascii=False)
        f.write("\n") # keep newline at EOF

if __name__ == "__main__":
    main()
