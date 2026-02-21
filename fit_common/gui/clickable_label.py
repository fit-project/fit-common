#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QEnterEvent, QMouseEvent
from PySide6.QtWidgets import QLabel, QWidget


class ClickableLabel(QLabel):
    def __init__(self, url: str, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.url = url
        self.setText(text)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            webbrowser.open(self.url)
        super().mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.setStyleSheet("text-decoration: underline;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event: QEnterEvent) -> None:
        self.setStyleSheet("text-decoration: none;")
        super().leaveEvent(event)
