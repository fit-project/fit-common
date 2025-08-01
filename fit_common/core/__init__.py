#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

# Expose a clean public API for the fit_common.core package,
# avoiding circular imports and keeping modules decoupled.

# ---- Paths utilities ----
from .paths import (
    resolve_app_path,
    resolve_db_path,
    resolve_log_path,
    resolve_path,
)

# ---- System & platform utilities ----
from .utils import (
    find_free_port,
    get_context,
    get_ntp_date_and_time,
    get_platform,
    has_new_portable_version,
    is_admin,
    is_cmd,
    is_npcap_installed,
)

# ---- Logging & error handling ----
# NOTE: these are safe to import as long as debug.py does NOT import utils.py
try:
    from .crash_handler import handle_crash, set_gui_crash_handler
    from .debug import DEBUG_LEVEL, DebugLevel, debug, set_debug_level
    from .error_handler import log_exception
    from .versions import (
        get_local_version,
        get_remote_tag_version,
        has_new_release_version,
    )
except ImportError:
    # Optional if those files are not available yet during early development
    debug = None
    log_exception = None
    handle_crash = None

__all__ = [
    # paths
    "resolve_path",
    "resolve_log_path",
    "resolve_db_path",
    "resolve_app_path",
    # utils
    "get_platform",
    "is_admin",
    "is_npcap_installed",
    "is_cmd",
    "get_version",
    "find_free_port",
    "has_new_portable_version",
    "get_ntp_date_and_time",
    "get_context",
    # logging
    "debug",
    "DEBUG_LEVEL",
    "DebugLevel",
    "set_debug_level",
    "log_exception",
    "handle_crash",
    "set_gui_crash_handler",
    # version
    "get_local_version",
    "get_remote_tag_version",
    "has_new_release_version",
]
