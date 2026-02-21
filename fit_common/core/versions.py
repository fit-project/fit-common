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


def find_pyproject(start_path: Path) -> Path | None:
    current = start_path.resolve()
    for parent in [current, *current.parents]:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            return pyproject
    return None


def get_version_from_bundle() -> str | None:
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


def get_version(start_path: Path | None = None) -> str | None:
    try:
        if start_path is None:
            start_path = Path(sys.modules["__main__"].__file__).resolve()

        pyproject_path = find_pyproject(start_path)
        if pyproject_path:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)
            return data.get("tool", {}).get("poetry", {}).get("version")
    except Exception:
        pass

    return get_version_from_bundle()


def get_local_version() -> str:
    return get_version() or "0.0.0"


def get_remote_tag_version(repo: str) -> str | None:
    url = f"https://api.github.com/repos/fit-project/{repo}/tags"
    response = requests.get(url, timeout=5)
    tags = response.json()
    if isinstance(tags, list) and tags:
        first_tag = tags[0]
        if isinstance(first_tag, dict):
            tag_name = first_tag.get("name")
            if isinstance(tag_name, str):
                return tag_name
    return None


def has_new_release_version(repo: str) -> bool:
    if getattr(sys, "frozen", False):
        try:
            response = requests.get(
                f"https://api.github.com/repos/fit-project/{repo}/releases/latest",
                timeout=10,
            )
            response.raise_for_status()

            payload = response.json()
            remote_tag_name = (
                payload.get("tag_name", "")
                if isinstance(payload, dict)
                else ""
            )
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


def extract_version(tag_name: str) -> str:
    match = re.search(r"\d+\.\d+\.\d+", tag_name)
    return match.group(0) if match else ""
