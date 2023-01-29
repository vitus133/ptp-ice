#!/usr/bin/python
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
if len(sys.argv) < 2:
    print("Usage: python parse.py <trace file name>")
    sys.exit(0)
fn = sys.argv[1]


diffs = []
samples = []
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
        if diff > 0:
            diffs.append(diff)
            samples.append(samples[-1]+1 if len(samples) > 0 else 0)
fig, ax = plt.subplots()  
ax.plot(samples, diffs)

ax.set_xlabel("Sample")
ax.set_ylabel("Poll duration, sec")
ax.set_title("duration, sec")
ax.text(samples[-1]*0.1, max(diffs)*0.9, "\n".join((f"max: {max(diffs)}",
f"min: {1000000 * min(diffs)} us", f"average: {round(1000000 * sum(diffs)/len(diffs),2)} us")), size=12,
ha='left', va='top')
fig2, ax2 = plt.subplots()
ax2.hist(diffs, bins=100, color="Gray")

ax2.set_yscale('log')
ax2.set_title("Histogram (logY) and CDF")

count, bins_count = np.histogram(diffs, bins=100)

pdf = count / sum(count)
cdf = np.cumsum(pdf)
ax3 = ax2.twinx()
ax3.plot(np.arange(0, max(diffs), max(diffs)/100), cdf, label='CDF')

plt.show()

  




