#!/usr/bin/python
import sys
if len(sys.argv) < 2:
    print("Usage: python parse.py <trace file name>")
    sys.exit(0)
fn = sys.argv[1]


diffs = []
entry = False
with open(fn) as f:
    lines = f.readlines()
for line in lines:
    parts = line.split("sys_poll")
    if len(parts) < 2:
        continue
    ts = float(parts[0].split(" ")[-2].replace(":", ""))
    poll = parts[1]
    if "timeout_msecs" in poll and "ffffffff" not in poll:
        entry = True
        entry_ts = ts
    if "->" in poll and entry is True:
        diff = round(ts - entry_ts, 6)
        entry = False
        diffs.append(f"{entry_ts},{diff}\n")
        
with open("poll_durations.csv", "w") as f:
    f.writelines(diffs)
  




