#!/usr/bin/env python3
"""Device Status Monitor -- watch device state changes in real-time."""
import argparse, sys, time, json
from datetime import datetime
sys.path.insert(0, "src")
from cloudphone import CloudPhoneClient

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=10)
    ap.add_argument("--watch", nargs="+")
    a = ap.parse_args()
    c = CloudPhoneClient()
    print("AndroidCloudDevice Device Monitor (Ctrl+C to stop)\n")
    states = {}
    try:
        while True:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Polling...")
            try: devs = c.list_devices()
            except Exception as e: print(f"[ERROR] {e}"); time.sleep(a.interval); continue
            if a.watch: devs = [d for d in devs if d.id in a.watch]
            for d in devs:
                cur = d.status.value; last = states.get(d.id); m = "NEW" if last is None else ("CHG" if last!=cur else "")
                states[d.id] = cur
                icon = dict(online="OK ", offline="OFF", error="ERR", starting="RUN", stopping="STP").get(d.status.value, "???")
                print(f"  [{icon}] {m:<3s} {d.id:<8s} {d.name:<20s} {d.status.value:<10s} {d.public_ip or 'N/A'}")
            online = sum(1 for d in devs if d.status.value=="online")
            print(f"  --- Total:{len(devs)} Online:{online} ---\n")
            time.sleep(a.interval)
    except KeyboardInterrupt:
        with open("device_states.json","w") as f: json.dump(states,f)
        print("\nMonitor stopped. States saved.")

if __name__ == "__main__": main()
