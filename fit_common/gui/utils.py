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

from PySide6 import QtWidgets

from fit_common.core.utils import get_platform
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


def show_dialog(
    severity: str = "information",
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
        dialog.exec()
    except Exception:
        return


def show_finish_verification_dialog(path, verification_type):

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


def __open_verification_report(dialog, path, verification_type):

    dialog.close()

    filename = "report_integrity_pec_verification.pdf"

    if verification_type == VerificationTypes.TIMESTAMP:
        filename = "report_timestamp_verification.pdf"

    pdf_file = os.path.join(path, filename)

    platform = get_platform()
    if platform == "win":
        os.startfile(pdf_file)
    elif platform == "macos":
        subprocess.call(["open", pdf_file])
    else:
        subprocess.call(["xdg-open", pdf_file])


def get_verification_label_text(
    verification_name, verification_status, verification_message
):
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
):
    item = QtWidgets.QListWidgetItem(status_list)
    label = QtWidgets.QLabel(label_text)
    label.setWordWrap(True)
    item.setSizeHint(label.sizeHint())
    status_list.addItem(item)
    status_list.setItemWidget(item, label)


def show_finish_acquisition_dialog(acquisition_directory):

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


def __open_acquisition_directory(dialog, acquisition_directory):
    platform = get_platform()
    if platform == "win":
        os.startfile(acquisition_directory)
    elif platform == "macos":
        subprocess.call(["open", acquisition_directory])
    else:
        subprocess.call(["xdg-open", acquisition_directory])

    dialog.close()
