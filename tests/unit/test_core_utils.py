from datetime import datetime, timezone

from fit_common.core import utils


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


def test_get_ntp_date_and_time_failure_logs(monkeypatch):
    errors = []

    class _Client:
        def request(self, server, version):
            raise RuntimeError("ntp down")

    monkeypatch.setattr(utils.ntplib, "NTPClient", lambda: _Client())
    monkeypatch.setattr(
        "fit_common.core.error_handler.log_exception",
        lambda exc, context=None: errors.append((str(exc), context)),
    )
    assert utils.get_ntp_date_and_time("pool.ntp.org") is None
    assert errors


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
