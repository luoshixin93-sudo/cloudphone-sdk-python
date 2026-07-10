#!/usr/bin/env python3
"""Batch APK Installer -- deploy APKs to multiple devices."""
import argparse, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, "src")
from cloudphone import CloudPhoneClient, CloudPhoneError

def install_one(client, did, apk):
    try:
        r = client.install_apk(did, apk)
        ok = r.success if hasattr(r,"success") else r.exit_code==0
        return dict(id=did, ok=ok, out=getattr(r,"stdout",str(r)))
    except CloudPhoneError as e: return dict(id=did, ok=False, err=str(e))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("apk"); ap.add_argument("--devices",nargs="+"); ap.add_argument("--parallel",type=int,default=5)
    a = ap.parse_args()
    p = Path(a.apk)
    if not p.exists(): print(f"[ERROR] {p} not found"); sys.exit(1)
    c = CloudPhoneClient()
    devs = a.devices or [d.id for d in c.list_devices(status="online")]
    print(f"Installing {p.name} on {len(devs)} devices...")
    results = []
    with ThreadPoolExecutor(max_workers=a.parallel) as ex:
        fs = {ex.submit(install_one,c,d,str(p)):d for d in devs}
        for f in as_completed(fs):
            r = f.result(); results.append(r)
            print(f"  ['OK ' if r['ok'] else 'FAIL'] {r['id']}: {r.get('err',r.get('out',''))[:60]}")
    ok = sum(1 for r in results if r["ok"])
    print(f"\nDone: {ok}/{len(results)} succeeded")
    if len(results)-ok: sys.exit(1)

if __name__ == "__main__": main()
