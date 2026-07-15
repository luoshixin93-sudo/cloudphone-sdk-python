# Android Cloud Device SDK for Python

[![PyPI](https://img.shields.io/pypi/v/android_cloud_device-sdk.svg)](https://pypi.org/project/android_cloud_device-sdk/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Manage **Android Cloud Device** (Android cloud devices with dedicated public IPs) programmatically.

[your-cloud-android-api.com](https://www.your-cloud-android-api.com) | [Documentation](#quick-start) | [Issues](https://github.com/luoshixin93-sudo/android_cloud_device-sdk-python/issues)

---

## Why Android Cloud Device?

Every Android Cloud Device instance comes with a **dedicated public IP address**, real Android OS, and full ADB access.

| | Android Cloud Device | Emulator | Physical Farm |
|---|:---:|:---:|:---:|
| Dedicated IP | YES | NO | YES |
| Full Android | YES | Limited | YES |
| Worldwide | YES | NO | Limited |
| ADB/REST API | YES | YES | Complex |
| Scale 100+ | YES | Limited | NO |

## Features

- REST API Client -- clean Python wrapper
- Device Management -- list/start/stop/reboot
- Screenshot Capture -- real-time screen capture
- Shell Commands -- execute any ADB command
- File Push/Pull -- upload APKs, pull logs
- Script Injection -- run Python/Lua on device
- CLI Tool -- zero-code terminal operations
- Examples -- TikTok/Douyin automation scripts

## Quick Start

```bash
pip install android_cloud_device-sdk
```

```python
from android_cloud_device import Android Cloud DeviceClient
client = Android Cloud DeviceClient(api_key="your_key")
devices = client.list_devices()
for d in devices:
    print(d.id, d.status, d.public_ip)
```

## CLI

```bash
export CLOUDPHONE_API_KEY=your_key
android_cloud_device-cli devices list
android_cloud_device-cli device screenshot GZ-01 --output screen.png
android_cloud_device-cli device shell GZ-01 --cmd "dumpsys battery"
android_cloud_device-cli device push GZ-01 --local app.apk --remote /sdcard/app.apk
```

## Examples

| Script | Description |
|--------|-------------|
| device_status_monitor.py | Real-time device health monitor |
| screenshot_collector.py | Batch screenshot capture |
| apk_installer.py | Deploy APKs to multiple devices |
| douyin_comment_scraper.py | Collect Douyin/TikTok comments |

## Use Cases

- Social Media Automation -- unique IPs per account
- App Testing -- CI/CD integration at scale
- Android Botting -- game bots, engagement automation
- Proxy Rotation -- each device as a residential proxy
- App Distribution -- push APKs for QA testing

## License

MIT -- see LICENSE.

## Contact

[your-cloud-android-api.com](https://www.your-cloud-android-api.com) | WhatsApp @along915 | ailong9281@gmail.com | Telegram @Alongyun
