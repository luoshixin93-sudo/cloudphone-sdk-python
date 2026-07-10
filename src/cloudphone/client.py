"""CloudPhone REST API Client for Python."""
from __future__ import annotations
import os, time, json, logging
from typing import Optional, List, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from cloudphone.models import Device, ScreenshotResult, ShellResult, FileTransferResult

logger = logging.getLogger(__name__)


class CloudPhoneError(Exception):
    def __init__(self, msg, code=None, status_code=None):
        super().__init__(msg); self.message = msg; self.code = code; self.status_code = status_code


class AuthenticationError(CloudPhoneError): pass
class RateLimitError(CloudPhoneError):
    def __init__(self, msg, retry_after=None, **kw):
        super().__init__(msg, **kw); self.retry_after = retry_after


class CloudPhoneClient:
    DEFAULT_BASE_URL = "https://api.qtphone.com/v1"

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or os.environ.get("CLOUDPHONE_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key not found. Set CLOUDPHONE_API_KEY env or pass api_key.")
        self.base_url = (base_url or os.environ.get("CLOUDPHONE_BASE_URL") or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout; self.max_retries = max_retries
        self._session = self._create_session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CloudPhone-SDK-Python/0.1.0",
        })

    def _create_session(self):
        s = requests.Session()
        r = Retry(self.max_retries, backoff_factor=0.5, status_forcelist=(429,500,502,503,504))
        s.mount("https://", HTTPAdapter(max_retries=r)); s.mount("http://", HTTPAdapter(max_retries=r))
        return s

    def _request(self, method, path, **kw) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip("/")}"
        kw.setdefault("timeout", self.timeout)
        try: resp = self._session.request(method, url, **kw)
        except requests.exceptions.RequestException as e: raise CloudPhoneError(f"Request failed: {e}") from e
        if resp.status_code == 401: raise AuthenticationError("Invalid API key.", status_code=401)
        if resp.status_code == 403: raise AuthenticationError("Access forbidden.", status_code=403)
        if resp.status_code == 429:
            ra = resp.headers.get("Retry-After"); raise RateLimitError("Rate limit exceeded.", retry_after=int(ra) if ra else None, status_code=429)
        if resp.status_code >= 400:
            try: msg = resp.json().get("message", resp.text)
            except: msg = resp.text
            raise CloudPhoneError(msg, status_code=resp.status_code)
        return resp

    # -- Device Management --
    def list_devices(self, status: Optional[str] = None, region: Optional[str] = None) -> List[Device]:
        params = {}
        if status: params["status"] = status
        if region: params["region"] = region
        r = self._request("GET", "/devices", params=params)
        data = r.json(); items = data if isinstance(data, list) else data.get("devices", data.get("data", []))
        return [Device.from_dict(d) for d in items]

    def get_device(self, device_id: str) -> Device:
        return Device.from_dict(self._request("GET", f"/devices/{device_id}").json())

    def start_device(self, device_id: str) -> Device:
        return Device.from_dict(self._request("POST", f"/devices/{device_id}/start").json())

    def stop_device(self, device_id: str) -> Device:
        return Device.from_dict(self._request("POST", f"/devices/{device_id}/stop").json())

    def reboot_device(self, device_id: str) -> Device:
        return Device.from_dict(self._request("POST", f"/devices/{device_id}/reboot").json())

    def delete_device(self, device_id: str) -> None:
        self._request("DELETE", f"/devices/{device_id}")

    # -- Screenshot --
    def screenshot(self, device_id: str) -> ScreenshotResult:
        resp = self._request("GET", f"/devices/{device_id}/screenshot")
        return ScreenshotResult(device_id=device_id, image_bytes=resp.content)

    # -- Shell --
    def shell(self, device_id: str, command: str, timeout: Optional[int] = None) -> ShellResult:
        import time as _t; payload = {"command": command}
        if timeout: payload["timeout"] = timeout
        start = _t.perf_counter(); resp = self._request("POST", f"/devices/{device_id}/shell", json=payload)
        data = resp.json()
        return ShellResult(device_id=device_id, command=command,
                           stdout=data.get("stdout",""), stderr=data.get("stderr",""),
                           exit_code=data.get("exit_code",0),
                           duration_ms=(_t.perf_counter()-start)*1000)

    # -- File Transfer --
    def push(self, device_id: str, local_path: str, remote_path: str) -> FileTransferResult:
        with open(local_path, "rb") as f:
            files = {"file": (os.path.basename(local_path), f)}
            data = {"path": remote_path}
            resp = self._request("POST", f"/devices/{device_id}/push", data=data, files=files)
        result = resp.json()
        return FileTransferResult(device_id=device_id, local_path=local_path, remote_path=remote_path,
                                 size_bytes=os.path.getsize(local_path),
                                 success=result.get("success", True), error=result.get("error"))

    def pull(self, device_id: str, remote_path: str, local_path: str) -> FileTransferResult:
        resp = self._request("GET", f"/devices/{device_id}/pull", params={"path": remote_path})
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        with open(local_path, "wb") as f: f.write(resp.content)
        return FileTransferResult(device_id=device_id, local_path=local_path, remote_path=remote_path,
                                 size_bytes=len(resp.content), success=True)

    # -- APK --
    def install_apk(self, device_id: str, apk_path: str) -> ShellResult:
        with open(apk_path, "rb") as f:
            files = {"apk": (os.path.basename(apk_path), f, "application/vnd.android.package-archive")}
            resp = self._request("POST", f"/devices/{device_id}/apk/install", files=files)
        data = resp.json()
        return ShellResult(device_id=device_id, command=f"install {apk_path}",
                           stdout=data.get("output",""), stderr=data.get("error",""),
                           exit_code=0 if data.get("success") else 1, duration_ms=0)

    def uninstall(self, device_id: str, package: str) -> ShellResult:
        return self.shell(device_id, f"uninstall {package}")

    # -- Script --
    def run_script(self, device_id: str, script: str, language: str = "python") -> ShellResult:
        resp = self._request("POST", f"/devices/{device_id}/script", json={"script": script, "language": language})
        data = resp.json()
        return ShellResult(device_id=device_id, command=f"run {language} script",
                           stdout=data.get("output",""), stderr=data.get("error",""),
                           exit_code=data.get("exit_code",0), duration_ms=data.get("duration_ms",0))

    def get_account_info(self) -> Dict[str, Any]:
        return self._request("GET", "/account/info").json()

    def __repr__(self): return f"<CloudPhoneClient base_url={self.base_url}>"
