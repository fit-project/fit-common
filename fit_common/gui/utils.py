#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import os
import subprocess
import sys
from enum import Enum, auto
from typing import Literal

from PySide6 import QtWidgets

from fit_common.gui.dialog import Dialog, DialogButtonTypes
from fit_common.lang import load_translations


class VerificationTypes(Enum):
    TIMESTAMP = auto()
    PEC = auto()


class Status(Enum):
    PENDING = "Pending"
    FAILURE = "Failure"
    SUCCESS = "Success"
    UNKNOWN = "Unknown"


class State(Enum):
    INITIALIZATED = "initializated"
    STARTED = "Started"
    COMPLETED = "Completed"
    STOPPED = "Stopped"


translations = load_translations()


def _open_with_default_app(path: str) -> None:
    startfile = getattr(os, "startfile", None)
    if callable(startfile):
        startfile(path)
    elif sys.platform == "darwin":
        subprocess.call(["open", path])
    else:
        subprocess.call(["xdg-open", path])


def show_dialog(
    severity: Literal[
        "error", "critical", "warning", "warn", "question", "info", "information"
    ] = "information",
    title: str = "",
    message: str = "",
    details: str = "",
) -> None:
    try:
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)

        severity_map = {
            "error": QtWidgets.QMessageBox.Icon.Critical,
            "critical": QtWidgets.QMessageBox.Icon.Critical,
            "warning": QtWidgets.QMessageBox.Icon.Warning,
            "warn": QtWidgets.QMessageBox.Icon.Warning,
            "question": QtWidgets.QMessageBox.Icon.Question,
            "info": QtWidgets.QMessageBox.Icon.Information,
            "information": QtWidgets.QMessageBox.Icon.Information,
        }
        icon = severity_map.get(
            severity.lower(), QtWidgets.QMessageBox.Icon.Information
        )

        dialog = Dialog(title, message, details, icon)
        dialog.right_button.clicked.connect(dialog.close)
        dialog.exec()
    except Exception:
        return


def show_finish_verification_dialog(
    path: str, verification_type: VerificationTypes
) -> None:

    title = translations["VERIFICATION_COMPLETED"]
    msg = translations["VERIFY_PEC_SUCCESS_MSG"]

    if verification_type == VerificationTypes.TIMESTAMP:
        msg = translations["VALID_TIMESTAMP_REPORT"]

    dialog = Dialog(
        title,
        msg,
    )
    dialog.message.setStyleSheet("font-size: 13px;")
    dialog.set_buttons_type(DialogButtonTypes.QUESTION)
    dialog.right_button.clicked.connect(dialog.close)
    dialog.left_button.clicked.connect(
        lambda: __open_verification_report(dialog, path, verification_type)
    )

    dialog.exec()


def __open_verification_report(
    dialog: Dialog, path: str, verification_type: VerificationTypes
) -> None:

    dialog.close()

    filename = "report_integrity_pec_verification.pdf"

    if verification_type == VerificationTypes.TIMESTAMP:
        filename = "report_timestamp_verification.pdf"

    pdf_file = os.path.join(path, filename)

    _open_with_default_app(pdf_file)


def get_verification_label_text(
    verification_name: str,
    verification_status: Status,
    verification_message: str,
) -> str:
    __status = (
        '<strong style="color:green">{}</strong>'.format(verification_status)
        if verification_status == Status.SUCCESS
        else '<strong style="color:red">{}</strong>'.format(verification_status)
    )
    __message = (
        "" if verification_message == "" else "details: {}".format(verification_message)
    )

    return "{}: {} {}".format(verification_name, __status, __message)


def add_label_in_verification_status_list(
    status_list: QtWidgets.QListWidget, label_text: str
) -> None:
    item = QtWidgets.QListWidgetItem(status_list)
    label = QtWidgets.QLabel(label_text)
    label.setWordWrap(True)
    item.setSizeHint(label.sizeHint())
    status_list.addItem(item)
    status_list.setItemWidget(item, label)


def show_finish_acquisition_dialog(acquisition_directory: str) -> None:

    dialog = Dialog(
        translations["ACQUISITION_FINISHED_TITLE"],
        translations["ACQUISITION_FINISHED_MSG"],
    )
    dialog.message.setStyleSheet("font-size: 13px;")
    dialog.set_buttons_type(DialogButtonTypes.QUESTION)
    dialog.right_button.clicked.connect(dialog.close)
    dialog.left_button.clicked.connect(
        lambda: __open_acquisition_directory(dialog, acquisition_directory)
    )

    dialog.exec()


def __open_acquisition_directory(dialog: Dialog, acquisition_directory: str) -> None:
    _open_with_default_app(acquisition_directory)

    dialog.close()
