"""Unit tests for CloudPhone SDK. Run: pytest tests/ -v"""
import pytest
from unittest.mock import patch, Mock
from cloudphone import CloudPhoneClient, AuthenticationError
from cloudphone.models import Device, DeviceStatus, ScreenshotResult, ShellResult


class TestClient:
    @patch("cloudphone.client.requests.Session")
    def test_init(self, _): assert CloudPhoneClient(api_key="x").api_key == "x"

    @patch.dict("os.environ", {"CLOUDPHONE_API_KEY": "env_key"})
    @patch("cloudphone.client.requests.Session")
    def test_env_key(self, _): assert CloudPhoneClient().api_key == "env_key"

    def test_no_key(self):
        with patch("cloudphone.client.os.environ.get", return_value=None):
            with pytest.raises(AuthenticationError): CloudPhoneClient(api_key=None)

class TestDevice:
    def test_from_dict(self):
        d = Device.from_dict({"id":"GZ-01","name":"Test","status":"online","public_ip":"1.2.3.4"})
        assert d.id=="GZ-01" and d.status==DeviceStatus.ONLINE and d.public_ip=="1.2.3.4"
    def test_unknown(self):
        assert Device(id="X",name="Y",status="banana").status == DeviceStatus.UNKNOWN
    def test_repr(self): r=repr(Device(id="A",name="B",status="offline")); assert "A" in r and "offline" in r

class TestShellResult:
    def test_ok(self): assert ShellResult("X","cmd","out","",0,50).success is True
    def test_fail(self): assert ShellResult("X","cmd","","e",1,10).success is False

class TestScreenshot:
    def test_save(self, tmp_path):
        r = ScreenshotResult(device_id="X", image_bytes=b"PNGdata")
        r.save(str(p:=tmp_path/"t.png"))
        assert p.read_bytes() == b"PNGdata"

if __name__ == "__main__": pytest.main([__file__,"-v"])
