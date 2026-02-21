#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


import ctypes
import inspect
import locale
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from shutil import which
from typing import Literal

import ntplib

from fit_common.core.debug import debug

DEFAULT_LANG = "en"
Platform = Literal["lin", "macos", "win", "other"]


def __normalize_lang(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    cleaned = cleaned.split(".")[0].replace("-", "_")
    return cleaned.split("_")[0].lower() if cleaned else None


def get_system_lang() -> str:
    FIT_USER_SYSTEM_LANG = os.environ.get("FIT_USER_SYSTEM_LANG", "")
    normalized_user_lang = __normalize_lang(FIT_USER_SYSTEM_LANG)
    if normalized_user_lang:
        return normalized_user_lang
    try:
        if get_platform() == "macos":
            try:
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleLanguages"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        line = line.strip().strip('",')
                        if line and line not in ("(", ")"):
                            normalized = __normalize_lang(line)
                            if normalized:
                                return normalized
            except Exception:
                pass
            try:
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleLocale"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    normalized = __normalize_lang(result.stdout.strip())
                    if normalized:
                        return normalized
            except Exception:
                pass
        elif get_platform() == "win":
            try:
                windll = getattr(ctypes, "windll", None)
                if windll is not None:
                    lang_id = windll.kernel32.GetUserDefaultUILanguage()
                    win_locale = locale.windows_locale.get(lang_id)
                    normalized = __normalize_lang(win_locale)
                    if normalized:
                        return normalized
            except Exception:
                pass
        else:
            for key in ("LC_ALL", "LC_MESSAGES", "LANG"):
                normalized = __normalize_lang(os.environ.get(key))
                if normalized:
                    return normalized
        locale.setlocale(locale.LC_ALL, "")
        lang = locale.getlocale()[0]
        normalized = __normalize_lang(lang)
        return normalized or DEFAULT_LANG
    except Exception:
        return DEFAULT_LANG


def get_platform() -> Platform:
    platforms: dict[str, Platform] = {
        "linux": "lin",
        "linux1": "lin",
        "linux2": "lin",
        "darwin": "macos",
        "win32": "win",
    }

    if sys.platform not in platforms:
        return "other"

    return platforms[sys.platform]


def is_bundled() -> bool:
    return bool(getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))


def is_admin() -> bool:
    try:
        # macOS/Linux
        return os.geteuid() == 0
    except AttributeError:
        # Windows
        if get_platform() == "win":
            try:
                windll = getattr(ctypes, "windll", None)
                if windll is None:
                    return False
                return bool(windll.shell32.IsUserAnAdmin())
            except Exception as exc:
                debug(f"Windows admin check failed: {exc}", context="is_admin")
                return False
        debug("Admin check failed: unsupported platform", context="is_admin")
        return False


def is_npcap_installed() -> bool:
    # reference https://npcap.com/guide/npcap-devguide.html section (Install-time detection)
    return os.path.exists("C:\\Program Files\\Npcap\\NPFInstall.exe")


def get_ntp_date_and_time(server: str) -> datetime | None:
    try:
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return datetime.fromtimestamp(response.tx_time, timezone.utc)
    except Exception as exception:
        from fit_common.core.error_handler import log_exception

        log_exception(exception, context=f"NTP request failed with server: {server}")
        return None


def is_cmd(name: str) -> bool:
    return which(name) is not None


# search for the first free port to bind the proxy
def find_free_port() -> int:
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


def get_context(obj: object) -> str:
    """Return 'ClassName.method_name' for the calling method."""
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None:
        return obj.__class__.__name__
    class_name = obj.__class__.__name__
    method_name = frame.f_back.f_code.co_name
    return f"{class_name}.{method_name}"
