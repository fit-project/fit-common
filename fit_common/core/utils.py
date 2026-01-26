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
import os
import re
import socket
import sys
from configparser import ConfigParser
from datetime import datetime, timezone
from shutil import which

import ntplib
import requests
from packaging.version import Version

from fit_common.core.debug import debug
from fit_common.core.paths import resolve_path


def get_platform():
    platforms = {
        "linux": "lin",
        "linux1": "lin",
        "linux2": "lin",
        "darwin": "macos",
        "win32": "win",
    }

    if sys.platform not in platforms:
        return "other"

    return platforms[sys.platform]


def is_bundled():
    return bool(getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))


def is_admin() -> bool:
    try:
        # macOS/Linux
        return os.geteuid() == 0
    except AttributeError:
        # Windows
        if get_platform() == "win":
            try:
                return bool(ctypes.windll.shell32.IsUserAnAdmin())
            except Exception as exc:
                debug(f"Windows admin check failed: {exc}", context="is_admin")
                return False
        debug("Admin check failed: unsupported platform", context="is_admin")
        return False


def is_npcap_installed():
    # reference https://npcap.com/guide/npcap-devguide.html section (Install-time detection)
    return os.path.exists("C:\\Program Files\\Npcap\\NPFInstall.exe")


def has_new_portable_version():
    parser = ConfigParser()
    parser.read(resolve_path("assets/config.ini"))
    url = parser.get("fit_properties", "fit_latest_version_url")

    with requests.get(url, stream=True, timeout=10, verify=False) as response:
        try:
            remote_tag_name = response.json()["tag_name"]
            local_tag_name = parser.get("fit_properties", "tag_name")

            remote_tag_name = re.findall(r"(?:(\d+\.(?:\d+\.)*\d+))", remote_tag_name)
            local_tag_name = re.findall(r"(?:(\d+\.(?:\d+\.)*\d+))", local_tag_name)

            if (
                len(remote_tag_name) == 1
                and len(local_tag_name) == 1
                and Version(remote_tag_name[0]) > Version(local_tag_name[0])
            ):
                return True
            return False
        except Exception as e:
            from fit_common.core.error_handler import log_exception

            log_exception(e, context="Error comparing remote and local version")
            return False


def get_ntp_date_and_time(server):
    try:
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
        return datetime.fromtimestamp(response.tx_time, timezone.utc)
    except Exception as exception:
        from fit_common.core.error_handler import log_exception

        log_exception(exception, context=f"NTP request failed with server: {server}")
        return None


def is_cmd(name):
    return which(name) is not None


# search for the first free port to bind the proxy
def find_free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    return sock.getsockname()[1]


def get_context(obj):
    """Return 'ClassName.method_name' for the calling method."""
    frame = inspect.currentframe().f_back
    class_name = obj.__class__.__name__
    method_name = frame.f_code.co_name
    return f"{class_name}.{method_name}"
