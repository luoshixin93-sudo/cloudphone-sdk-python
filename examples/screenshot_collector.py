#!/usr/bin/env python3
"""Screenshot Collector -- capture from multiple devices."""
import argparse, os, sys
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, "src")
from cloudphone import CloudPhoneClient

def capture(client, did, out_dir):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, f"{did}_{ts}.png")
    try:
        r = client.screenshot(did); r.save(path)
        return dict(id=did, ok=True, path=path, size=len(r.image_bytes))
    except Exception as e: return dict(id=did, ok=False, err=str(e))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--devices",nargs="+"); ap.add_argument("--output",default="screenshots"); ap.add_argument("--parallel",type=int,default=5)
    a = ap.parse_args()
    os.makedirs(a.output, exist_ok=True)
    c = CloudPhoneClient()
    devs = a.devices or [d.id for d in c.list_devices(status="online")]
    print(f"Capturing from {len(devs)} devices -> {a.output}/")
    with ThreadPoolExecutor(max_workers=a.parallel) as ex:
        fs = {ex.submit(capture,c,d,a.output):d for d in devs}
        for f in as_completed(fs):
            r = f.result()
            print(f"  ['OK ' if r['ok'] else 'FAIL'] {r['id']}: {r.get('path',r.get('err',''))}")
    print(f"Done.")

if __name__ == "__main__": main()
