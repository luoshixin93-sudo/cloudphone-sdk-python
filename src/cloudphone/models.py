"""Data models for CloudPhone SDK."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class DeviceStatus(Enum):
    ONLINE = "online"; OFFLINE = "offline"; STARTING = "starting"
    STOPPING = "stopping"; ERROR = "error"; UNKNOWN = "unknown"


class Device:
    def __init__(self, id: str, name: str, status: str = "unknown", public_ip: Optional[str] = None,
                 region: Optional[str] = None, os_version: Optional[str] = None,
                 model: Optional[str] = None, created_at: Optional[str] = None,
                 tags: Optional[Dict[str, str]] = None, **kw):
        self.id = id; self.name = name; self.status = DeviceStatus(status.lower()) if status else DeviceStatus.UNKNOWN
        self.public_ip = public_ip; self.region = region; self.os_version = os_version
        self.model = model; self.created_at = created_at; self.tags = tags or {}; self._raw = kw

    @classmethod
    def from_dict(cls, d: Dict[str, Any]): return cls(**{k:v for k,v in d.items() if not k.startswith("_")})

    def to_dict(self): return dict(id=self.id, name=self.name, status=self.status.value,
                                   public_ip=self.public_ip, region=self.region,
                                   os_version=self.os_version, model=self.model)

    def __repr__(self): return f"<Device {self.id}: {self.name} [{self.status.value}]>"


@dataclass
class ScreenshotResult:
    device_id: str; image_bytes: bytes; width: Optional[int] = None
    height: Optional[int] = None; format: str = "png"
    def save(self, path: str):
        with open(path, "wb") as f: f.write(self.image_bytes)


@dataclass
class ShellResult:
    device_id: str; command: str; stdout: str; stderr: str; exit_code: int; duration_ms: float
    @property
    def success(self): return self.exit_code == 0


@dataclass
class FileTransferResult:
    device_id: str; local_path: str; remote_path: str; size_bytes: int; success: bool
    error: Optional[str] = None
