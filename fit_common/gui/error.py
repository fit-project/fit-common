#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PySide6 import QtWidgets

from fit_common.gui.dialog import Dialog


class Error(Dialog):
    def __init__(
        self,
        severity: QtWidgets.QMessageBox.Icon | None,
        title: str,
        message: str,
        details: str,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(title, message, details, severity, parent)
        self.right_button.clicked.connect(self.close)
