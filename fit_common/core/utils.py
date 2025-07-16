#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from shutil import which
from distutils.version import StrictVersion
import os
import sys
import ntplib
import re

import requests
from datetime import datetime, timezone
from configparser import ConfigParser

import socket


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


def is_admin():
    is_admin = False
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        if get_platform() == "win":
            import windows_tools.users as users

            is_admin = users.is_user_local_admin(os.getlogin())

    return is_admin

def is_npcap_installed():
    # reference https://npcap.com/guide/npcap-devguide.html section (Install-time detection)
    return os.path.exists("C:\\Program Files\\Npcap\\NPFInstall.exe")


def resolve_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode.
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path


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
                and StrictVersion(remote_tag_name[0]) > StrictVersion(local_tag_name[0])
            ):
                return True
            return False
        except Exception as e:
            raise Exception(e)


def get_ntp_date_and_time(server):
    try:
        ntpDate = None
        client = ntplib.NTPClient()
        response = client.request(server, version=3)
    except Exception as exception:
        return exception

    return datetime.fromtimestamp(response.tx_time, timezone.utc)



def is_cmd(name):
    return which(name) is not None


def get_version():
    return "v0.0.0"


def resolve_db_path(path):
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            local_path = os.path.join(os.path.expanduser("~"), "AppData", "Local")
        elif sys.platform == "darwin":
            local_path = os.path.expanduser("~/Library/Application Support")
        else:
            local_path = os.path.expanduser("~/.local/share")

        resolve_db_path = os.path.join(local_path, path)
    else:
        resolve_db_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolve_db_path


# search for the first free port to bind the proxy
def find_free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    return sock.getsockname()[1]
