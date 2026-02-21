#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

from fit_common.core.paths import resolve_log_path

LOG_PATH = resolve_log_path("fit_error.log")

logger = logging.getLogger("fit_error")
logger.setLevel(logging.ERROR)

handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=500_000,
    backupCount=5,
)
formatter = logging.Formatter("[ERROR] %(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_exception(exception: Exception, context: str | None = None) -> None:
    """
    Logs a handled exception to a rotating file.
    """
    timestamp = datetime.now().isoformat(timespec="seconds")
    header = f"[ERROR] {timestamp}"
    message = f"{context + ': ' if context else ''}{str(exception)}"
    stack = "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )

    log_entry = f"{header} - {message}\n{stack}"

    logger.error(log_entry)
