# fix_json_in_place.py
# This script fixes the formatting and indentation of a JSON file in place.
# It uses the json5 library to handle more lenient JSON parsing (e.g., comments, trailing commas, single quotes).
# If the input JSON has syntax errors that json5 can't handle, it will still fail.
# It will report the changes made using a unified diff.
# Install json5 if not already: pip install json5
# Usage: python fix_json_in_place.py input.json

import json5
import json
import sys
import tempfile
import shutil
import difflib

if len(sys.argv) != 2:
    print("Usage: python fix_json_in_place.py input.json")
    sys.exit(1)

input_file = sys.argv[1]

try:
    with open(input_file, 'r') as f:
        original_text = f.read()
    
    data = json5.loads(original_text)
    
    fixed_text = json.dumps(data, indent=4, sort_keys=False) + '\n'
    
    if original_text == fixed_text:
        print(f"No changes needed for {input_file}")
    else:
        diff = difflib.unified_diff(
            original_text.splitlines(keepends=True),
            fixed_text.splitlines(keepends=True),
            fromfile='original',
            tofile='fixed'
        )
        print("Changes made:")
        print(''.join(diff))
        
        # Use a temporary file to write the output safely
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(fixed_text)
        
        # Replace the original file with the temp file
        shutil.move(temp_file.name, input_file)
        
        print(f"Successfully fixed and formatted JSON in place: {input_file}")
except Exception as e:
    print(f"Error processing JSON: {str(e)}")
    sys.exit(1)
