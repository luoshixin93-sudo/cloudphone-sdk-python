#!/usr/bin/env python3
"""Android Cloud Device CLI -- manage Android cloud devices from terminal."""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cloudphone import CloudPhoneClient, CloudPhoneError, AuthenticationError


def client(): 
    try: return CloudPhoneClient()
    except AuthenticationError as e:
        print(f"[ERROR] {e.message}", file=sys.stderr)
        print("Set CLOUDPHONE_API_KEY env var", file=sys.stderr); sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Android Cloud Device CLI")
    sp = ap.add_subparsers(dest="cmd", required=True)

    # devices list
    lp = sp.add_parser("list", help="List all devices")
    lp.add_argument("--status", choices=["online","offline","starting","stopping","error"])
    lp.add_argument("--json", action="store_true")
    lp.set_defaults(func=lambda a: _list(a))

    # device <id> <action>
    dp = sp.add_parser("device", help="Device operations"); dp.add_argument("id")
    dsp = dp.add_subparsers()

    def add_sub(name, fn, args):
        p = dsp.add_parser(name); [getattr(p,"add_argument")(a,b) for a,b in args]; p.set_defaults(func=fn)

    add_sub("info", lambda a: _info(a), [])
    add_sub("screenshot", lambda a: _screenshot(a), [("-o","--output")])
    add_sub("shell", lambda a: _shell(a), [("-c","--cmd",{"required":True}),("-q","--quiet",{"action":"store_true"})])
    add_sub("push", lambda a: _push(a), [("-l","--local",{"required":True}),("-r","--remote",{"required":True})])
    add_sub("pull", lambda a: _pull(a), [("-r","--remote",{"required":True}),("-l","--local",{"required":True})])
    add_sub("start", lambda a: _start(a), [])
    add_sub("stop", lambda a: _stop(a), [])
    add_sub("reboot", lambda a: _reboot(a), [])

    # account
    ap2 = sp.add_parser("account", help="Account info")
    ap2.set_defaults(func=lambda a: _account(a))

    args = ap.parse_args()
    if hasattr(args, "func"): args.func(args)
    else: ap.print_help()


def _list(args):
    c = client(); devs = c.list_devices(status=args.status)
    if not devs: print("No devices."); return
    if args.json: print(json.dumps([d.to_dict() for d in devs], indent=2, ensure_ascii=False))
    else:
        print(f'{"ID":<10} {"NAME":<20} {"STATUS":<10} {"IP":<18}')
        print("-"*60)
        [print(f"{d.id:<10} {d.name:<20} {d.status.value:<10} {str(d.public_ip or "-"):<18}") for d in devs]

def _info(args):
    c = client(); d = c.get_device(args.id)
    print(json.dumps(d.to_dict(), indent=2, ensure_ascii=False))

def _screenshot(args):
    c = client(); r = c.screenshot(args.id)
    p = args.output or f"{args.id}_screenshot.png"; r.save(p)
    print(f"Saved: {p} ({len(r.image_bytes)} bytes)")

def _shell(args):
    c = client(); r = c.shell(args.id, args.cmd)
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr, file=sys.stderr)
    if not args.quiet: print(f"[Exit:{r.exit_code}] [{r.duration_ms:.1f}ms]")
    sys.exit(r.exit_code)

def _push(args):
    c = client(); r = c.push(args.id, args.local, args.remote)
    print(f"OK: {args.local} -> {args.remote}") if r.success else print(f"FAIL: {r.error}", file=sys.stderr)

def _pull(args):
    c = client(); r = c.pull(args.id, args.remote, args.local)
    print(f"OK: {args.remote} -> {args.local}")

def _start(args): print(f"Starting {args.id}..."); c = client(); d = c.start_device(args.id); print(f"Status: {d.status.value}")
def _stop(args): print(f"Stopping {args.id}..."); c = client(); d = c.stop_device(args.id); print(f"Status: {d.status.value}")
def _reboot(args): print(f"Rebooting {args.id}..."); c = client(); d = c.reboot_device(args.id); print(f"Status: {d.status.value}")
def _account(args): c = client(); print(json.dumps(c.get_account_info(), indent=2, ensure_ascii=False))

if __name__ == "__main__": main()
