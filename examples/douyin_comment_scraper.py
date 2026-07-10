#!/usr/bin/env python3
"""Douyin/TikTok Comment Scraper -- collect comments via cloud devices.
Each device has a unique IP for safe multi-account scraping.
Adjust package names and UI coordinates for your Douyin/TikTok version.
"""
import argparse, sys, time, json
sys.path.insert(0, "src")
from cloudphone import CloudPhoneClient

PKG_DY = "com.ss.android.ugc.aweme"    # Douyin
PKG_TT = "com.zhiliaoapp.musically"    # TikTok International

def scrape_device(client, device_id, video_url, scrolls=10):
    """Open video and collect visible comments via UI automation."""
    comments = []
    # Open video URL in app
    r = client.shell(device_id, f'am start -a android.intent.action.VIEW -d "{video_url}" {PKG_TT}')
    if r.exit_code != 0:
        return {"device_id": device_id, "error": f"Failed to open app: {r.stderr}", "comments": []}
    time.sleep(3)

    # Scroll and collect visible text (simplified -- adjust coordinates for your version)
    for i in range(scrolls):
        # Dump UI hierarchy
        client.shell(device_id, "uiautomator dump /sdcard/ui.xml")
        time.sleep(0.5)
        # Pull and parse (production: parse XML for comment text nodes)
        try:
            client.pull(device_id, "/sdcard/ui.xml", f"/tmp/ui_{device_id}.xml")
        except: pass
        # Swipe up to load more
        client.shell(device_id, "input swipe 540 1800 540 900 500")
        time.sleep(1.5)

    return {"device_id": device_id, "comment_count": 0, "comments": comments}

def main():
    ap = argparse.ArgumentParser(description="Scrape Douyin/TikTok comments via CloudPhone")
    ap.add_argument("--video-url", required=True)
    ap.add_argument("--devices", nargs="+", required=True)
    ap.add_argument("--scrolls", type=int, default=10)
    ap.add_argument("--output", default="comments.json")
    a = ap.parse_args()

    client = CloudPhoneClient()
    all_results = []
    for did in a.devices:
        print(f"[{did}] Scraping...")
        result = scrape_device(client, did, a.video_url, scrolls=a.scrolls)
        all_results.append(result)
        print(f"[{did}] Done: {result.get('comment_count',0)} comments collected")

    with open(a.output, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    total = sum(r.get("comment_count",0) for r in all_results)
    print(f"\nTotal: {total} comments from {len(a.devices)} devices -> {a.output}")

if __name__ == "__main__": main()
