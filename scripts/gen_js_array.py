#!/usr/bin/env python3
"""Generate the compact JS const C=[] from the corrected college_cutoffs.json"""
import json, os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '..', 'data', 'college_cutoffs.json')

with open(data_path) as f:
    colleges = json.load(f)

items = []
for c in colleges:
    obj = {
        "n": c["name"],
        "s": c["state"],
        "t": c["type"],
        "tier": c["tier"],
        "seats": c["seats"],
        "sp": c["specialties"],
        "UR": c["cutoffs"]["UR"],
        "OBC": c["cutoffs"]["OBC"],
        "SC": c["cutoffs"]["SC"],
        "ST": c["cutoffs"]["ST"],
        "EWS": c["cutoffs"]["EWS"],
        "PH": c["cutoffs"]["PH"],
        "new": c.get("is_new_2025", False),
    }
    items.append(json.dumps(obj, ensure_ascii=False))

js_array = "const C=[" + ",".join(items) + "];"

out_path = os.path.join(script_dir, '..', 'data', 'colleges_compact.js')
with open(out_path, 'w') as f:
    f.write(js_array)

print(f"✅ Generated {len(colleges)} entries → {out_path}")
print(f"   Size: {len(js_array):,} bytes")
