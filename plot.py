#!/usr/bin/python
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print("Usage: python parse.py <trace file name>")
    sys.exit(0)
fn = sys.argv[1]

hist_bins = 100
poll_durations = [] # List of time differences between poll entry and exit
fw_durations = [] # List of time differences between firmware start and end
samples = [] # list of increasing sample numbers for X axis
items = [] # list of dictionaries handy for sorting by timestamp
entry = False # If true, we are within the transaction
skip_exit =  0 # skip sys_poll exit if entry was irrelevant

trace_dict = {"poll_entry": 0, "poll_exit": 1, "ice_tx_tstamp_request": 2, 
"ice_tx_tstamp_fw_req": 3, "ice_tx_tstamp_fw_done": 4, "ice_tx_tstamp_complete": 5}

with open(fn) as f:
    lines = f.readlines()
# Build a list of dictionaries with ts, call and args
for line in lines:
    if "sys_poll" in line:
        fcn = "sys_poll"
    elif "ice_tx_tstamp_request" in line:
        fcn = "ice_tx_tstamp_request"
    elif "ice_tx_tstamp_fw_req" in line:
        fcn = "ice_tx_tstamp_fw_req"
    elif "ice_tx_tstamp_fw_done" in line:
        fcn = "ice_tx_tstamp_fw_done"
    elif "ice_tx_tstamp_complete" in line:
        fcn = "ice_tx_tstamp_complete"
    else: continue
    parts = line.split(fcn)
    
    if len(parts) < 2:
        print(f"Malformed line {line}")
        sys.exit(1)
    ts = float(parts[0].split(" ")[-2].replace(":", ""))
    args = parts[1]
    items.append({"ts": ts, "call": fcn, "args": args})
# Sort the list by ts
items = sorted(items, key=lambda d: d['ts'])
# Process and plot
tracker = [False]
for item in items:
    if "ts" not in item or "call" not in item:
        print(f"Malformed line {item}")
        sys.exit(2)
    ts = item.get("ts")
    call = item.get("call")
    args = item.get("args")
    if call == "ice_tx_tstamp_request":
        entry = True
        ice_tx_req_ts = ts
        tracker = [False] * len(trace_dict)
        tracker[trace_dict[call]] = True
    elif call == "sys_poll" and entry is True:
        if "ffffffff" in args:
            skip_exit += 1
        elif "timeout_msecs" in args :
            poll_call_ts = ts
            configured_timeout_ms = int(args.split("meout_msecs: ")[-1].replace(")\n", ""), base=16)
            tracker[trace_dict["poll_entry"]] = True
        elif "->" in args:
            if skip_exit > 0:
                skip_exit -= 1
                continue
            exit_ts = ts
            tracker[trace_dict["poll_exit"]] = True
            

    elif call == "ice_tx_tstamp_fw_req" and entry is True:
        fw_req_ts = ts
        tracker[trace_dict[call]] = True
    elif call == "ice_tx_tstamp_fw_done" and entry is True:
        fw_done_ts = ts
        tracker[trace_dict[call]] = True
    elif call == "ice_tx_tstamp_complete" and entry is True:
        ice_tstamp_complete_ts = ts
        tracker[trace_dict[call]] = True

    if all(tracker):
        entry = False
        tracker = [False]
        diff = round(exit_ts - poll_call_ts, 6)
        if diff * 1000 > configured_timeout_ms:
            print(f"timeout detected at {exit_ts}, diff = {diff * 1000} ms")
        fw_diff = round(fw_done_ts - fw_req_ts, 6)
        if diff > 0:
            poll_durations.append(diff)
            samples.append(samples[-1]+1 if len(samples) > 0 else 0)
            if fw_diff > 0:
                fw_durations.append(fw_diff)
            else:
                print(item)
                sys.exit(3)
        else:
            print(item)
            sys.exit(4)


fig, ax = plt.subplots()  
ax.set_xlabel("Sample")
ax.set_ylabel("Poll duration, sec")
ax.set_title("Poll duration, sec")

ax.plot(poll_durations)

ax.text(samples[-1]*0.1, max(poll_durations)*0.9, "\n".join((f"max: {max(poll_durations)}",
f"min: {1000000 * min(poll_durations)} us", f"average: {round(1000000 * sum(poll_durations)/len(poll_durations),2)} us")),
size=14, weight='bold', ha='left', va='top')
fig2, ax2 = plt.subplots()

ax2.hist(poll_durations, bins=hist_bins, color="Gray")

ax2.set_yscale('log')
ax2.set_title("Poll system call Histogram (logY) and CDF")

count, bins_count = np.histogram(poll_durations, bins=hist_bins)
pdf = count / sum(count)
cdf = np.cumsum(pdf)
ax3 = ax2.twinx()
ax3.plot(np.arange(0, max(poll_durations), max(poll_durations)/hist_bins)[0:hist_bins], cdf, label='CDF')

fig_fw, ax_fw = plt.subplots()
ax_fw.plot(fw_durations, color="gray")
ax_fw.set_xlabel("Sample")
ax_fw.set_ylabel("duration, sec")
ax_fw.set_title("Firmware request to firmware done, sec")
ax_fw.text(samples[-1]*0.1, max(fw_durations)*0.9, "\n".join((f"max: {max(fw_durations)}",
f"min: {1000000 * min(fw_durations)} us", f"average: {round(1000000 * sum(fw_durations)/len(fw_durations),2)} us")),
size=14, weight='bold', ha='left', va='top')

fig_fw_hist, ax_fw_hist = plt.subplots()
ax_fw_hist.hist(fw_durations, bins=hist_bins, color="cyan")
ax_fw_hist.set_yscale('log')
ax_fw_hist.set_title("Firmware execution time histogram (logY) and CDF")
count_fw, bins_count_fw = np.histogram(fw_durations, bins=hist_bins)
pdf_fw = count_fw / sum(count_fw)
cdf_fw = np.cumsum(pdf_fw)
ax_fw_cdf = ax_fw_hist.twinx()
ax_fw_cdf.plot(np.arange(0, max(fw_durations), max(fw_durations)/hist_bins)[0:hist_bins], cdf_fw, label='CDF', color="darkorange")

plt.show()

  




