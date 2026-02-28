import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "fit_common" / "core" / "utils.py"
SPEC = importlib.util.spec_from_file_location("fit_common.core.utils_under_test", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
utils = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = utils
SPEC.loader.exec_module(utils)


def test_normalize_lang_private_helper():
    assert utils.__normalize_lang(" it_IT.UTF-8 ") == "it"
    assert utils.__normalize_lang("en-US") == "en"
    assert utils.__normalize_lang("") is None


def test_get_system_lang_uses_env_override(monkeypatch):
    monkeypatch.setenv("FIT_USER_SYSTEM_LANG", "fr_FR.UTF-8")
    assert utils.get_system_lang() == "fr"


def test_get_platform_mapping(monkeypatch):
    monkeypatch.setattr(utils.sys, "platform", "darwin")
    assert utils.get_platform() == "macos"
    monkeypatch.setattr(utils.sys, "platform", "win32")
    assert utils.get_platform() == "win"
    monkeypatch.setattr(utils.sys, "platform", "something-else")
    assert utils.get_platform() == "other"


def test_is_admin_posix(monkeypatch):
    monkeypatch.setattr(utils.os, "geteuid", lambda: 0)
    assert utils.is_admin() is True
    monkeypatch.setattr(utils.os, "geteuid", lambda: 1000)
    assert utils.is_admin() is False


def test_is_admin_windows_branch(monkeypatch):
    monkeypatch.delattr(utils.os, "geteuid", raising=False)
    monkeypatch.setattr(utils, "get_platform", lambda: "win")

    class _Shell32:
        @staticmethod
        def IsUserAnAdmin():
            return 1

    class _Windll:
        shell32 = _Shell32()

    monkeypatch.setattr(utils.ctypes, "windll", _Windll(), raising=False)
    assert utils.is_admin() is True


def test_is_npcap_installed(monkeypatch):
    monkeypatch.setattr(utils.os.path, "exists", lambda path: True)
    assert utils.is_npcap_installed() is True


def test_get_ntp_date_and_time_success(monkeypatch):
    class _Resp:
        tx_time = 1_700_000_000

    class _Client:
        def request(self, server, version):
            return _Resp()

    monkeypatch.setattr(utils.ntplib, "NTPClient", lambda: _Client())
    value = utils.get_ntp_date_and_time("pool.ntp.org")
    assert isinstance(value, datetime)
    assert value.tzinfo == timezone.utc


def test_get_ntp_time_info_uses_fallback_server(monkeypatch):
    calls = []

    class _Resp:
        tx_time = 1_700_000_000

    class _Client:
        def request(self, server, version):
            calls.append((server, version))
            if server == "bad.example":
                raise RuntimeError("ntp down")
            return _Resp()

    monkeypatch.setattr(utils.ntplib, "NTPClient", lambda: _Client())

    value = utils.get_ntp_time_info("bad.example")

    assert value["source"] == "ntp"
    assert value["server"] == "time.google.com"
    assert value["datetime"].tzinfo == timezone.utc
    assert calls == [("bad.example", 3), ("time.google.com", 3)]


def test_get_ntp_time_info_all_servers_fail_logs_and_returns_os_time(monkeypatch):
    errors = []

    class _Client:
        def request(self, server, version):
            raise RuntimeError("ntp down")

    monkeypatch.setattr(utils.ntplib, "NTPClient", lambda: _Client())
    monkeypatch.setattr(
        "fit_common.core.error_handler.log_exception",
        lambda exc, context=None: errors.append((str(exc), context)),
    )

    value = utils.get_ntp_time_info("pool.ntp.org")

    assert value["source"] == "os"
    assert value["server"] is None
    assert isinstance(value["datetime"], datetime)
    assert value["datetime"].tzinfo == timezone.utc
    assert errors == [
        (
            "ntp down",
            (
                "NTP request failed for all servers: "
                "pool.ntp.org, time.google.com, time.cloudflare.com"
            ),
        )
    ]


def test_get_ntp_date_and_time_returns_none_when_os_fallback_is_used(monkeypatch):
    class _Client:
        def request(self, server, version):
            raise RuntimeError("ntp down")

    monkeypatch.setattr(utils.ntplib, "NTPClient", lambda: _Client())
    monkeypatch.setattr(
        "fit_common.core.error_handler.log_exception",
        lambda exc, context=None: None,
    )

    assert utils.get_ntp_date_and_time("pool.ntp.org") is None


def test_is_cmd(monkeypatch):
    monkeypatch.setattr(utils, "which", lambda name: "/usr/bin/" + name)
    assert utils.is_cmd("ffmpeg") is True


def test_find_free_port_returns_positive_int(monkeypatch):
    class _Sock:
        def bind(self, addr):
            self.addr = addr

        def getsockname(self):
            return ("127.0.0.1", 42424)

        def close(self):
            return None

    monkeypatch.setattr(utils.socket, "socket", lambda: _Sock())
    port = utils.find_free_port()
    assert isinstance(port, int)
    assert port == 42424


def test_get_context_returns_class_and_method():
    class _Obj:
        def probe(self):
            return utils.get_context(self)

    assert _Obj().probe() == "_Obj.probe"
