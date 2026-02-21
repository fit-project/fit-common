#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from enum import Enum

from PySide6 import QtCore, QtWidgets

from fit_common.gui.ui_multipurpose import Ui_multipurpose_dialog
from fit_common.lang import load_translations


class DialogButtonTypes(Enum):
    MESSAGE = 1
    QUESTION = 2
    NONE = 3


class Dialog(QtWidgets.QDialog, Ui_multipurpose_dialog):
    def __init__(
        self,
        title: str,
        message: str,
        details: str | None = None,
        severity: QtWidgets.QMessageBox.Icon | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super(Dialog, self).__init__(parent)

        # Inizializza l'interfaccia da ui_multipurpose.py
        self.setupUi(self)

        # HIDE STANDARD TITLE BAR
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__translations = load_translations()

        self.__set_icon_severity(severity)
        self.__set_title(title)
        self.__set_message(message)
        self.__set_details(details)
        self.__set_buttons_message()
        self.progress_bar.hide()

        self.content_box.adjustSize()
        self.adjustSize()
        self.setMinimumWidth(self.content_box.width())
        self.content_top_bg.setMinimumWidth(self.content_box.width())

    def set_buttons_type(self, buttons_type: DialogButtonTypes) -> None:
        if buttons_type == DialogButtonTypes.MESSAGE:
            self.__set_buttons_message()
        elif buttons_type == DialogButtonTypes.QUESTION:
            self.__set_buttons_question()
        elif buttons_type == DialogButtonTypes.NONE:
            self.__hide_buttons()

    def show_progress_bar(self) -> None:
        self.progress_bar.show()

    def __set_title(self, title: str) -> None:
        self.title_right_info.setText(title)

    def __set_icon_severity(
        self, severity: QtWidgets.QMessageBox.Icon | None
    ) -> None:
        if severity is not None:
            standard_pixmap: QtWidgets.QStyle.StandardPixmap | None = None
            if severity == QtWidgets.QMessageBox.Icon.Warning:
                standard_pixmap = QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning
            elif severity == QtWidgets.QMessageBox.Icon.Information:
                standard_pixmap = (
                    QtWidgets.QStyle.StandardPixmap.SP_MessageBoxInformation
                )
            elif severity == QtWidgets.QMessageBox.Icon.Question:
                standard_pixmap = (
                    QtWidgets.QStyle.StandardPixmap.SP_MessageBoxQuestion
                )
            elif severity == QtWidgets.QMessageBox.Icon.Critical:
                standard_pixmap = (
                    QtWidgets.QStyle.StandardPixmap.SP_MessageBoxCritical
                )

            if standard_pixmap is not None:
                icon = self.style().standardIcon(standard_pixmap)
                self.icon_severity.setPixmap(icon.pixmap(QtCore.QSize(42, 42)))
            else:
                self.icon_severity.hide()

        else:
            self.icon_severity.hide()

    def __set_message(self, message: str) -> None:
        self.message.setText(message)

    def __set_details(self, details: str | None) -> None:
        self.details.setText(details or "")

    def __set_buttons_message(self) -> None:
        self.close_button.hide()
        self.left_button.hide()
        self.right_button.setText(self.__translations["OK"])

    def __set_buttons_question(self) -> None:
        self.close_button.hide()
        self.left_button.setText(self.__translations["YES"])
        self.right_button.setText(self.__translations["NO"])
        self.left_button.show()

    def __hide_buttons(self) -> None:
        self.close_button.hide()
        self.left_button.hide()
        self.right_button.hide()
