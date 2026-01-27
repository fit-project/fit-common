#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import sys


def resolve_path(path: str) -> str:
    """
    Resolves a relative path to a file bundled with the app (e.g. assets, .ui).
    In PyInstaller mode, uses sys._MEIPASS. In development, uses current working directory.
    """
    if getattr(sys, "frozen", False):
        # Running from a bundled executable
        return os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Running in development mode
        return os.path.abspath(os.path.join(os.getcwd(), path))


def resolve_app_path(subfolder: str = "FIT") -> str:
    """
    Returns the base writable application path depending on the platform.
    - Windows: %LOCALAPPDATA%\\FIT
    - macOS: ~/Library/Application Support/FIT
    - Linux: ~/.local/share/FIT
    - Development: current working directory/FIT
    """
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            base_path = os.path.join(os.path.expanduser("~"), "AppData", "Local")
        elif sys.platform == "darwin":
            base_path = os.path.expanduser("~/Library/Application Support")
        else:
            base_path = os.path.expanduser("~/.local/share")
    else:
        base_path = os.getcwd()

    full_path = os.path.join(base_path, subfolder)
    os.makedirs(full_path, exist_ok=True)
    return full_path


def resolve_db_path(filename: str | None = None) -> str:
    db_dir = os.path.join(resolve_app_path(), "data")
    os.makedirs(db_dir, exist_ok=True)
    if not filename:
        return db_dir
    return os.path.join(db_dir, filename)


def resolve_log_path(filename: str | None = None) -> str:
    log_dir = os.path.join(resolve_app_path(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    if not filename:
        return log_dir
    return os.path.join(log_dir, filename)
