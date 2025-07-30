#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging
from datetime import datetime
from enum import Enum
from logging.handlers import RotatingFileHandler

from fit_common.core.paths import resolve_log_path


class DebugLevel(Enum):
    NONE = 0
    LOG = 1
    VERBOSE = 2


# Current debug level (can be overwritten externally)
DEBUG_LEVEL = DebugLevel.LOG

LOG_PATH = resolve_log_path("fit_debug.log")


logger = logging.getLogger("fit_debug")
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=500_000,
    backupCount=5,
)
formatter = logging.Formatter("[DEBUG] %(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)


def debug(*args, context=None):
    """
    Logs debug information based on the current debug level.
    """
    if DEBUG_LEVEL == DebugLevel.NONE:
        return

    timestamp = datetime.now().isoformat(timespec="seconds")
    msg = " ".join(str(a) for a in args)
    prefix = f"[DEBUG] {timestamp}"
    line = f"{prefix} - {context + ': ' if context else ''}{msg}"

    if DEBUG_LEVEL in (DebugLevel.LOG, DebugLevel.VERBOSE):
        logger.debug(line)

    if DEBUG_LEVEL == DebugLevel.VERBOSE:
        print(line)
