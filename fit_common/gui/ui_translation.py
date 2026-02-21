#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from typing import Mapping

from PySide6 import QtCore, QtGui, QtWidgets


def translate_ui(translations: Mapping[str, str], root: QtWidgets.QWidget) -> None:
    """Apply translations to all child widgets starting from the given root."""
    _traverse_widgets(translations, root)


def _traverse_widgets(
    translations: Mapping[str, str], widget: QtWidgets.QWidget
) -> None:
    _apply_translation(translations, widget)

    for child in widget.findChildren(
        QtWidgets.QWidget,
        options=QtCore.Qt.FindChildOption.FindDirectChildrenOnly,
    ):
        _traverse_widgets(translations, child)

    # Include QAction items (e.g., menus, toolbars)
    for action in getattr(widget, "actions", lambda: [])():
        _apply_action_translation(translations, action)


def _apply_translation(
    translations: Mapping[str, str], widget: QtWidgets.QWidget
) -> None:
    name = widget.objectName()
    if not name:
        return

    key = name.upper()
    value = translations.get(key)
    if not value:
        return

    # text -> setText
    if hasattr(widget, "text") and hasattr(widget, "setText"):
        current = widget.text()
        if current and current.strip():
            widget.setText(value)

    # placeholderText -> setPlaceholderText
    if hasattr(widget, "placeholderText") and hasattr(widget, "setPlaceholderText"):
        current = widget.placeholderText()
        if current and current.strip():
            widget.setPlaceholderText(value)

    # title -> setTitle (e.g., QGroupBox)
    if hasattr(widget, "title") and hasattr(widget, "setTitle"):
        current = widget.title()
        if current and current.strip():
            widget.setTitle(value)

    # toolTip -> setToolTip
    if hasattr(widget, "toolTip") and hasattr(widget, "setToolTip"):
        current = widget.toolTip()
        if current and current.strip():
            widget.setToolTip(value)

    # statusTip -> setStatusTip
    if hasattr(widget, "statusTip") and hasattr(widget, "setStatusTip"):
        current = widget.statusTip()
        if current and current.strip():
            widget.setStatusTip(value)

    # QTabWidget tabs
    if isinstance(widget, QtWidgets.QTabWidget):
        for i in range(widget.count()):
            tab_key = f"{key}__TAB_{i}"
            tab_value = translations.get(tab_key)
            if not tab_value:
                continue
            current = widget.tabText(i)
            if current and current.strip():
                widget.setTabText(i, tab_value)


def _apply_action_translation(
    translations: Mapping[str, str], action: QtGui.QAction
) -> None:
    name = action.objectName()
    if not name:
        return

    key = name.upper()
    value = translations.get(key)
    if not value:
        return

    if hasattr(action, "setText"):
        current = action.text()
        if current and current.strip():
            action.setText(value)

    if hasattr(action, "setToolTip"):
        current_tt = action.toolTip()
        if current_tt and current_tt.strip():
            action.setToolTip(value)

    if hasattr(action, "setStatusTip"):
        current_st = action.statusTip()
        if current_st and current_st.strip():
            action.setStatusTip(value)
