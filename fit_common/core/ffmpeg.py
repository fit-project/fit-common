"""Shared helpers for invoking and parsing ffmpeg output."""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Optional, Sequence

from fit_common.core import debug, get_platform

_LOG_CONTEXT = "fit_common.core.ffmpeg"

_PERMISSION_DENIED_PATTERNS = [
    "not authorized",
    "permission denied",
    "device is not authorized",
    "permission was not granted",
]


@dataclass
class FFmpegResult:
    returncode: int
    stderr: str
    timed_out: bool = False


DeviceKind = Literal["audio", "video", "unknown"]


@dataclass(frozen=True)
class DeviceInfo:
    index: Optional[int]
    name: str
    kind: DeviceKind


@dataclass(frozen=True)
class ListDevicesResult:
    returncode: int
    devices: list[DeviceInfo]
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0

    @property
    def error(self) -> Optional[str]:
        return self.stderr.strip() or None


def get_list_devices(
    ffmpeg_path: Path | str,
    *,
    timeout: Optional[float] = None,
) -> ListDevicesResult:
    """Return ffmpeg's detected audio and video devices or an error state."""

    args = _list_devices_args(get_platform())
    proc = execute_ffmpeg_command(ffmpeg_path, args, timeout=timeout)

    stderr = normalize_output(proc.stderr)
    stdout = normalize_output(proc.stdout)
    combined_output = "\n".join(filter(None, [stdout, stderr]))

    if proc.returncode != 0:
        if get_platform() == "macos" and _is_expected_list_error(stderr):
            devices = _parse_device_listing(combined_output)
            return ListDevicesResult(0, devices, stderr.strip())
        return ListDevicesResult(proc.returncode, [], stderr.strip())

    devices = _parse_device_listing(combined_output)
    return ListDevicesResult(proc.returncode, devices, stderr.strip())


def _list_devices_args(platform: str) -> list[str]:
    if platform == "macos":
        return ["-hide_banner", "-f", "avfoundation", "-list_devices", "true", "-i", ""]
    if platform == "win":
        return ["-hide_banner", "-f", "dshow", "-list_devices", "true", "-i", ""]
    if platform == "lin":
        return ["-hide_banner", "-f", "x11grab", "-list_devices", "true", "-i", ""]
    raise NotImplementedError(f"Unsupported platform: {platform}")


_DEVICE_SECTION_RE = re.compile(r"(audio|video)\s+devices", re.IGNORECASE)
_DEVICE_ENTRY_RE = re.compile(r".*\[(\d+)\]\s*(?P<name>.+)$")


def _parse_device_listing(output: str) -> list[DeviceInfo]:
    devices: list[DeviceInfo] = []
    current_kind: DeviceKind = "unknown"
    for line in output.splitlines():
        section_match = _DEVICE_SECTION_RE.search(line)
        if section_match:
            current_kind = section_match.group(1).lower()
            continue
        entry_match = _DEVICE_ENTRY_RE.match(line)
        if not entry_match:
            continue
        index = int(entry_match.group(1))
        name = entry_match.group("name").strip()
        devices.append(DeviceInfo(index=index, name=name, kind=current_kind))
    return devices


def _is_expected_list_error(stderr: str) -> bool:
    return "error opening input" in stderr.lower()


def _device_index_to_str(device: DeviceInfo) -> Optional[str]:
    return str(device.index) if device.index is not None else None


def find_screen_device_index(devices: Iterable[DeviceInfo]) -> Optional[str]:
    """Return the index of the screen capture device from parsed results."""

    for device in devices:
        if device.kind == "video" and "capture screen" in device.name.lower():
            return _device_index_to_str(device)
    return None


def find_audio_device_index(devices: Iterable[DeviceInfo]) -> Optional[str]:
    """Return the first audio device index if available."""

    for device in devices:
        if device.kind == "audio":
            return _device_index_to_str(device)
    return None


def execute_ffmpeg_command(
    ffmpeg_path: Path | str,
    args: Sequence[str],
    timeout: Optional[float] = None,
) -> subprocess.CompletedProcess:
    """Run ffmpeg with the supplied arguments and capture its output."""

    ffmpeg_exec = str(ffmpeg_path)
    command = [ffmpeg_exec, *args]
    quoted = " ".join(shlex.quote(part) for part in command)
    debug(f"ℹ️ Running ffmpeg: {quoted}", context=_LOG_CONTEXT)

    proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if proc.stderr:
        for line in proc.stderr.splitlines():
            debug(f"ℹ️ [ffmpeg] {line}", context=_LOG_CONTEXT)
    return proc


def normalize_output(value: Optional[str | bytes]) -> str:
    """Normalize ffmpeg stdout/stderr so callers can treat it as text."""

    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return value


def permission_was_denied(
    output: str, patterns: Iterable[str] = _PERMISSION_DENIED_PATTERNS
) -> bool:
    """Indicate whether ffmpeg signaled a permissions failure."""

    lowered = output.lower()
    return any(pattern in lowered for pattern in patterns)


def combine_timeout_output(exc: subprocess.TimeoutExpired) -> str:
    """Return all available text emitted before an ffmpeg timeout."""

    return "".join(
        filter(
            None,
            [
                normalize_output(exc.stdout),
                normalize_output(exc.stderr),
            ],
        )
    )
