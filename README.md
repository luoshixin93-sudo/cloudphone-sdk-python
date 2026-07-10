# CloudPhone SDK for Python

[![PyPI](https://img.shields.io/pypi/v/cloudphone-sdk.svg)](https://pypi.org/project/cloudphone-sdk/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Manage **CloudPhone** (Android cloud devices with dedicated public IPs) programmatically.

[qtphone.com](https://www.qtphone.com) | [Documentation](#quick-start) | [Issues](https://github.com/luoshixin93-sudo/cloudphone-sdk-python/issues)

---

## Why CloudPhone?

Every CloudPhone instance comes with a **dedicated public IP address**, real Android OS, and full ADB access.

| | CloudPhone | Emulator | Physical Farm |
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
pip install cloudphone-sdk
```

```python
from cloudphone import CloudPhoneClient
client = CloudPhoneClient(api_key="your_key")
devices = client.list_devices()
for d in devices:
    print(d.id, d.status, d.public_ip)
```

## CLI

```bash
export CLOUDPHONE_API_KEY=your_key
cloudphone-cli devices list
cloudphone-cli device screenshot GZ-01 --output screen.png
cloudphone-cli device shell GZ-01 --cmd "dumpsys battery"
cloudphone-cli device push GZ-01 --local app.apk --remote /sdcard/app.apk
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

[qtphone.com](https://www.qtphone.com) | WhatsApp @along915 | ailong9281@gmail.com | Telegram @Alongyun
