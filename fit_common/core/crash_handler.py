#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import logging
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Callable, Optional

from fit_common.core.paths import resolve_log_path

LOG_PATH = resolve_log_path("fit_crash.log")


logger = logging.getLogger("fit_crash")
logger.setLevel(logging.ERROR)

handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=200_000,
    backupCount=10,
)
formatter = logging.Formatter("[CRASH] %(asctime)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Optional GUI callback to show the crash to the user (e.g. QMessageBox)
_gui_crash_callback: Optional[Callable[[str], None]] = None


def set_gui_crash_handler(callback: Callable[[str], None]):
    """
    Registers a GUI function to be called in case of a crash.
    Example: set_gui_crash_handler(show_crash_dialog)
    """
    global _gui_crash_callback
    _gui_crash_callback = callback


def handle_crash(exc_type, exc_value, exc_traceback):
    """
    Global handler for unhandled exceptions.
    Logs the crash and optionally shows a GUI dialog.
    """
    timestamp = datetime.now().isoformat(timespec="seconds")
    header = f"[CRASH] {timestamp}"
    exc_info = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_entry = f"{header}\n{exc_info}"

    # Log to file
    logger.error(log_entry)

    # Optional GUI feedback
    if _gui_crash_callback:
        try:
            _gui_crash_callback(log_entry)
        except Exception as gui_error:
            # Fallback in case GUI handling fails
            logger.error("Failed to show GUI crash dialog: %s", gui_error)


# Register the handler globally
sys.excepthook = handle_crash
