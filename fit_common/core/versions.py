#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

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
        main_file = getattr(main_module, "__file__", None)
        if not isinstance(main_file, str):
            return None
        main_path = Path(main_file).resolve()
        version_path = main_path.parent / "_version.py"

        if version_path.exists():
            spec = importlib.util.spec_from_file_location("_version", version_path)
            if spec is None or spec.loader is None:
                return None
            version_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(version_mod)
            return getattr(version_mod, "__version__", "unknown version")
    except Exception:
        pass
    return None


def get_version(start_path: Path | None = None) -> str | None:
    try:
        if start_path is None:
            main_file = getattr(sys.modules["__main__"], "__file__", None)
            if not isinstance(main_file, str):
                return None
            start_path = Path(main_file).resolve()

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


def has_new_release_version(
    repo: str,
    asset_name: str | None = None,
    *,
    asset_filters: dict[str, str] | None = None,
) -> bool:
    return (
        get_new_release_version(
            repo,
            asset_name=asset_name,
            asset_filters=asset_filters,
        )
        is not None
    )


def get_new_release_version(
    repo: str,
    asset_name: str | None = None,
    *,
    asset_filters: dict[str, str] | None = None,
) -> str | None:
    #if getattr(sys, "frozen", False):
    if True:
        try:
            payload = get_latest_release_payload(repo)
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
                if remote_version <= local_version:
                    return None
            except InvalidVersion:
                return None

            if asset_name is not None:
                rendered_asset_name = asset_name.format(version=remote_version_str)
                if not release_has_asset(payload, rendered_asset_name):
                    return None
            elif asset_filters is not None:
                rendered_asset_filters = {
                    key: value.format(version=remote_version_str)
                    for key, value in asset_filters.items()
                }
                if not release_has_asset_matching(payload, rendered_asset_filters):
                    return None

            return remote_version_str
        except requests.RequestException:
            return None
    else:
        return None


def get_latest_release_payload(repo: str) -> dict[str, Any]:
    try:
        response = requests.get(
            f"https://api.github.com/repos/fit-project/{repo}/releases/latest",
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def release_has_asset(payload: dict[str, Any], asset_name: str) -> bool:
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        return False
    return any(
        isinstance(asset, dict) and asset.get("name") == asset_name
        for asset in assets
    )


def release_has_asset_matching(
    payload: dict[str, Any],
    filters: dict[str, str],
) -> bool:
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        return False

    contains = [value.lower() for value in filters.get("contains", "").split() if value]
    suffix = filters.get("suffix", "").lower()

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        asset_name = asset.get("name")
        if not isinstance(asset_name, str):
            continue
        normalized_name = asset_name.lower()
        if contains and not all(token in normalized_name for token in contains):
            continue
        if suffix and not normalized_name.endswith(suffix):
            continue
        return True
    return False


def extract_version(tag_name: str) -> str:
    match = re.search(r"\d+\.\d+\.\d+", tag_name)
    return match.group(0) if match else ""
