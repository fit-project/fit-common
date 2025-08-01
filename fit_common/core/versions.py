#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import importlib
import re
import sys
from pathlib import Path

import requests
import tomllib
from packaging.version import InvalidVersion, Version


def get_local_version():
    try:

        project_root = Path(__file__).resolve().parents[3]
        pyproject_path = project_root / "pyproject.toml"
        if pyproject_path.exists():
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
            if "project" in data and "version" in data["project"]:
                return data["project"]["version"]
    except Exception:
        pass

    try:
        main_module = sys.modules["__main__"]
        main_path = Path(main_module.__file__).resolve()
        version_path = main_path.parent / "_version.py"

        if version_path.exists():
            spec = importlib.util.spec_from_file_location("_version", version_path)
            version_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(version_mod)
            return getattr(version_mod, "__version__", "unknown version")
    except Exception:
        pass

    return None


def get_remote_tag_version(repo: str):
    url = f"https://api.github.com/repos/fit-project/{repo}/tags"
    response = requests.get(url, timeout=5)
    tags = response.json()
    if tags:
        return tags[0]["name"]
    return None


def has_new_release_version(repo: str):
    if getattr(sys, "frozen", False):
        try:
            response = requests.get(
                f"https://api.github.com/repos/fit-project/{repo}/releases/latest",
                timeout=10,
            )
            response.raise_for_status()

            remote_tag_name = response.json().get("tag_name", "")
            remote_version_str = extract_version(remote_tag_name)
            local_version_str = get_local_version()

            try:
                remote_version = Version(remote_version_str)
                local_version = Version(local_version_str)
                return remote_version > local_version
            except InvalidVersion:
                return False

        except requests.RequestException:
            return False
    else:
        return False


def extract_version(tag_name):
    match = re.search(r"\d+\.\d+\.\d+", tag_name)
    return match.group(0) if match else ""
