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


DEBUG_LEVEL = DebugLevel.NONE


def set_debug_level(level: DebugLevel):
    global DEBUG_LEVEL
    DEBUG_LEVEL = level


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
    if DEBUG_LEVEL == DebugLevel.NONE:
        return

    msg = " ".join(str(a) for a in args)
    line = f"{context + ': ' if context else ''}{msg}"

    if DEBUG_LEVEL in (DebugLevel.LOG, DebugLevel.VERBOSE):
        logger.debug(line)

    if DEBUG_LEVEL == DebugLevel.VERBOSE:
        print(f"[DEBUG] {datetime.now().isoformat(timespec='seconds')} - {line}")
