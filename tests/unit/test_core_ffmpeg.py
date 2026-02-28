import importlib.util
import subprocess
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "fit_common" / "core" / "ffmpeg.py"
SPEC = importlib.util.spec_from_file_location("fit_common.core.ffmpeg_under_test", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
ffmpeg = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ffmpeg
SPEC.loader.exec_module(ffmpeg)


def test_get_list_devices_macos_parses_expected_error_output(monkeypatch):
    stderr = """
[AVFoundation indev @ 0x1] AVFoundation video devices:
[AVFoundation indev @ 0x1] [0] Capture screen 0
[AVFoundation indev @ 0x1] AVFoundation audio devices:
[AVFoundation indev @ 0x1] [1] Built-in Microphone
[in#0 @ 0x1] Error opening input: Input/output error
""".strip()

    monkeypatch.setattr(ffmpeg, "get_platform", lambda: "macos")
    monkeypatch.setattr(
        ffmpeg,
        "execute_ffmpeg_command",
        lambda ffmpeg_path, args, timeout=None: subprocess.CompletedProcess(
            args=[str(ffmpeg_path), *args],
            returncode=1,
            stdout="",
            stderr=stderr,
        ),
    )

    result = ffmpeg.get_list_devices(Path("/usr/bin/ffmpeg"))

    assert result.success is True
    assert result.returncode == 0
    assert [device.name for device in result.devices] == [
        "Capture screen 0",
        "Built-in Microphone",
    ]
    assert ffmpeg.find_screen_device_index(result.devices) == "0"
    assert ffmpeg.find_audio_device_index(result.devices) == "1"


def test_get_list_devices_returns_error_for_unexpected_failure(monkeypatch):
    monkeypatch.setattr(ffmpeg, "get_platform", lambda: "macos")
    monkeypatch.setattr(
        ffmpeg,
        "execute_ffmpeg_command",
        lambda ffmpeg_path, args, timeout=None: subprocess.CompletedProcess(
            args=[str(ffmpeg_path), *args],
            returncode=1,
            stdout="",
            stderr="ffmpeg fatal error",
        ),
    )

    result = ffmpeg.get_list_devices("/usr/bin/ffmpeg")

    assert result.success is False
    assert result.returncode == 1
    assert result.devices == []
    assert result.error == "ffmpeg fatal error"


def test_execute_ffmpeg_command_passes_timeout_and_logs(monkeypatch):
    debug_calls = []

    def _fake_run(command, capture_output, text, timeout):
        assert command == ["/usr/bin/ffmpeg", "-version"]
        assert capture_output is True
        assert text is True
        assert timeout == 4
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="line one\nline two",
        )

    monkeypatch.setattr(ffmpeg.subprocess, "run", _fake_run)
    monkeypatch.setattr(ffmpeg, "debug", lambda message, context=None: debug_calls.append((message, context)))

    result = ffmpeg.execute_ffmpeg_command("/usr/bin/ffmpeg", ["-version"], timeout=4)

    assert result.returncode == 0
    assert debug_calls == [
        ("ℹ️ Running ffmpeg: /usr/bin/ffmpeg -version", "fit_common.core.ffmpeg"),
        ("ℹ️ [ffmpeg] line one", "fit_common.core.ffmpeg"),
        ("ℹ️ [ffmpeg] line two", "fit_common.core.ffmpeg"),
    ]


def test_normalize_output_permission_and_timeout_helpers():
    timeout_error = subprocess.TimeoutExpired(
        cmd=["ffmpeg"],
        timeout=3,
        output=b"stdout text",
        stderr="stderr text",
    )

    assert ffmpeg.normalize_output(None) == ""
    assert ffmpeg.normalize_output(b"hello") == "hello"
    assert ffmpeg.permission_was_denied("Device is not authorized") is True
    assert ffmpeg.permission_was_denied("ordinary failure") is False
    assert ffmpeg.combine_timeout_output(timeout_error) == "stdout textstderr text"


def test_find_device_index_helpers_return_none_when_missing():
    devices = [ffmpeg.DeviceInfo(index=4, name="USB Camera", kind="video")]

    assert ffmpeg.find_screen_device_index(devices) is None
    assert ffmpeg.find_audio_device_index(devices) is None
