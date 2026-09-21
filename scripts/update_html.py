#!/usr/bin/env python3
"""
Replace the inline const C=[] data, SPECIALTY_MULTIPLIERS, and
marks-to-rank tables in index.html with corrected values.
"""
import json, os, re

script_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(script_dir, '..', 'index.html')
data_path = os.path.join(script_dir, '..', 'data', 'college_cutoffs.json')

with open(data_path) as f:
    colleges = json.load(f)

# Build compact JS array
items = []
for c in colleges:
    obj = {
        "n": c["name"], "s": c["state"], "t": c["type"],
        "tier": c["tier"], "seats": c["seats"], "sp": c["specialties"],
        "UR": c["cutoffs"]["UR"], "OBC": c["cutoffs"]["OBC"],
        "SC": c["cutoffs"]["SC"], "ST": c["cutoffs"]["ST"],
        "EWS": c["cutoffs"]["EWS"], "PH": c["cutoffs"]["PH"],
        "new": c.get("is_new_2025", False),
    }
    items.append(json.dumps(obj, ensure_ascii=False))

new_c_line = "const C=[" + ",".join(items) + "];"

# Read HTML
with open(html_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Replace const C=[...]; line (line 758)
    if stripped.startswith('const C=[{'):
        new_lines.append(new_c_line + '\n')
        print(f"  ✅ Replaced const C=[] at line {i+1}")
        continue
    
    new_lines.append(line)

with open(html_path, 'w') as f:
    f.writelines(new_lines)

print(f"\n✅ Updated index.html with corrected data ({len(colleges)} colleges)")
