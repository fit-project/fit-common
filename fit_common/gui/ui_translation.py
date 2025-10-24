#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from typing import Callable, Mapping, Optional

from PySide6 import QtCore, QtWidgets

# ---- API principale ---------------------------------------------------------


def translate_ui(
    translations: Mapping[str, str],
    root: QtWidgets.QWidget,
    key_builder: Optional[Callable[[str], str]] = None,
    update_only_if_non_empty: bool = True,
) -> None:
    """
    Applica le traduzioni ai widget partendo da `root`, usando le chiavi
    derivate da objectName (di default .upper()).
    """
    _traverse_widgets(
        translations=translations,
        widget=root,
        key_builder=key_builder or (lambda name: name.upper()),
        update_only_if_non_empty=update_only_if_non_empty,
    )


# ---- Implementazione --------------------------------------------------------


def _traverse_widgets(
    translations: Mapping[str, str],
    widget: QtWidgets.QWidget,
    key_builder: Callable[[str], str],
    update_only_if_non_empty: bool,
) -> None:
    _apply_translation(translations, widget, key_builder, update_only_if_non_empty)

    # Solo figli diretti: è quello che volevi (puoi rimuovere `options=` per tutti i discendenti)
    for child in widget.findChildren(
        QtWidgets.QWidget, options=QtCore.Qt.FindDirectChildrenOnly
    ):
        _traverse_widgets(translations, child, key_builder, update_only_if_non_empty)

    # Extra: traduci anche eventuali QAction agganciate al widget (menu, toolbar, ecc.)
    for action in getattr(widget, "actions", lambda: [])():
        _apply_action_translation(
            translations, action, key_builder, update_only_if_non_empty
        )


def _apply_translation(
    translations: Mapping[str, str],
    widget: QtWidgets.QWidget,
    key_builder: Callable[[str], str],
    update_only_if_non_empty: bool,
) -> None:
    name = widget.objectName()
    if not name:
        return

    key = key_builder(name)
    value = translations.get(key)
    if value is None:
        return

    # text -> setText (QLabel, QPushButton, QCheckBox, QGroupBox, ecc.)
    if hasattr(widget, "text") and hasattr(widget, "setText"):
        current = widget.text()
        if (not update_only_if_non_empty) or (current and current.strip()):
            widget.setText(value)

    # placeholderText -> setPlaceholderText (QLineEdit, QPlainTextEdit, ecc.)
    if hasattr(widget, "placeholderText") and hasattr(widget, "setPlaceholderText"):
        current = widget.placeholderText()
        if (not update_only_if_non_empty) or (current and current.strip()):
            widget.setPlaceholderText(value)

    # title -> setTitle (es. QGroupBox)
    if hasattr(widget, "title") and hasattr(widget, "setTitle"):
        current = widget.title()
        if (not update_only_if_non_empty) or (current and current.strip()):
            widget.setTitle(value)

    # toolTip -> setToolTip
    if hasattr(widget, "toolTip") and hasattr(widget, "setToolTip"):
        current = widget.toolTip()
        if (not update_only_if_non_empty) or (current and current.strip()):
            widget.setToolTip(value)

    # statusTip -> setStatusTip
    if hasattr(widget, "statusTip") and hasattr(widget, "setStatusTip"):
        current = widget.statusTip()
        if (not update_only_if_non_empty) or (current and current.strip()):
            widget.setStatusTip(value)

    # QTabWidget: tab text per ogni indice — chiave composta "<OBJECTNAME>__TAB_<INDEX>"
    if isinstance(widget, QtWidgets.QTabWidget):
        for i in range(widget.count()):
            tab_key = f"{key}__TAB_{i}"
            tab_value = translations.get(tab_key)
            if tab_value is None:
                continue
            current = widget.tabText(i)
            if (not update_only_if_non_empty) or (current and current.strip()):
                widget.setTabText(i, tab_value)


def _apply_action_translation(
    translations: Mapping[str, str],
    action: QtWidgets.QAction,
    key_builder: Callable[[str], str],
    update_only_if_non_empty: bool,
) -> None:
    name = action.objectName()
    if not name:
        return
    key = key_builder(name)
    value = translations.get(key)
    if value is None:
        return

    # QAction: text / toolTip / statusTip
    current = action.text()
    if hasattr(action, "setText") and (
        (not update_only_if_non_empty) or (current and str(current).strip())
    ):
        action.setText(value)

    if hasattr(action, "toolTip") and hasattr(action, "setToolTip"):
        current_tt = action.toolTip()
        if (not update_only_if_non_empty) or (current_tt and current_tt.strip()):
            action.setToolTip(value)

    if hasattr(action, "statusTip") and hasattr(action, "setStatusTip"):
        current_st = action.statusTip()
        if (not update_only_if_non_empty) or (current_st and current_st.strip()):
            action.setStatusTip(value)
