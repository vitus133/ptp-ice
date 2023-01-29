#!/usr/bin/python
import sys
if len(sys.argv) < 2:
    print("Usage: python parse.py <trace file name>")
    sys.exit(0)
fn = sys.argv[1]


diffs = []
entry = False
items = []
with open(fn) as f:
    lines = f.readlines()
# Build a list of dictionaries with ts and poll
for line in lines:
    parts = line.split("sys_poll")
    if len(parts) < 2:
        continue
    ts = float(parts[0].split(" ")[-2].replace(":", ""))
    call = parts[1]
    items.append({"ts": ts, "call": call})
# Sort the list by ts
items = sorted(items, key=lambda d: d['ts'])
i = 0
for item in items:
    print(item)
    i += 1
    if i > 10:
        break
'''

    if "timeout_msecs" in poll and "ffffffff" not in poll:
        entry = True
        entry_ts = ts
    if "->" in poll and entry is True:
        diff = round(ts - entry_ts, 6)
        entry = False
        diffs.append(f"{entry_ts},{diff}\n")
        
with open("poll_durations.csv", "w") as f:
    f.writelines(diffs)
'''  




