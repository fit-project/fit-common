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


from PySide6 import QtWidgets

from enum import Enum, auto

from fit_common.lang import load_translations
from fit_common.gui.dialog import Dialog, DialogButtonTypes
from fit_common.core.utils import get_platform

class VerificationTypes(Enum):
    TIMESTAMP = auto()
    PEC = auto()


class Status(Enum):
    PENDING = "Pending"
    FAIL = "Fail"
    SUCCESS = "Success"
    UNKNOW = "Unknow"

class State(Enum):
    INITIALIZATED = "initializated"
    STARTED = "Started"
    COMPLETED = "Completed"
    STOPPED = "Stopped"




def show_finish_verification_dialog(path, verification_type):

    translations = load_translations()

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