#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from PySide6 import QtCore, QtGui, QtWidgets


class Ui_multipurpose_dialog(object):
    def setupUi(self, multipurpose_dialog):
        multipurpose_dialog.setObjectName("multipurpose_dialog")
        multipurpose_dialog.resize(400, 300)
        multipurpose_dialog.setMinimumSize(QtCore.QSize(400, 0))
        multipurpose_dialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        multipurpose_dialog.setStyleSheet(
            "QWidget{\n"
            "    color: rgb(221, 221, 221);\n"
            "}\n"
            "\n"
            "/* Content App */\n"
            "#content_top_bg{    \n"
            "    background-color: rgb(33, 37, 43);\n"
            "}\n"
            "\n"
            "/* Top Buttons */\n"
            "#right_buttons .QPushButton { background-color: rgba(255, 255, 255, 0); border: none;  border-radius: 5px; }\n"
            "#right_buttons .QPushButton:hover { background-color: rgb(44, 49, 57); border-style: solid; border-radius: 4px; }\n"
            "#right_buttons .QPushButton:pressed { background-color: rgb(23, 26, 30); border-style: solid; border-radius: 4px; }\n"
            ""
        )
        self.content_box = QtWidgets.QFrame(parent=multipurpose_dialog)
        self.content_box.setGeometry(QtCore.QRect(0, 50, 400, 251))
        self.content_box.setMinimumSize(QtCore.QSize(400, 0))
        self.content_box.setStyleSheet("background-color: rgb(40, 44, 52);")
        self.content_box.setObjectName("content_box")
        self.content_box_layout = QtWidgets.QVBoxLayout(self.content_box)
        self.content_box_layout.setContentsMargins(12, 12, 12, 12)
        self.content_box_layout.setObjectName("content_box_layout")
        self.content_box_horizontal_layout = QtWidgets.QHBoxLayout()
        self.content_box_horizontal_layout.setContentsMargins(-1, -1, -1, 0)
        self.content_box_horizontal_layout.setObjectName(
            "content_box_horizontal_layout"
        )
        self.icon_severity = QtWidgets.QLabel(parent=self.content_box)
        self.icon_severity.setMaximumSize(QtCore.QSize(42, 42))
        self.icon_severity.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.icon_severity.setText("")
        self.icon_severity.setObjectName("icon_severity")
        self.content_box_horizontal_layout.addWidget(self.icon_severity)
        self.text_box = QtWidgets.QVBoxLayout()
        self.text_box.setContentsMargins(10, -1, -1, 0)
        self.text_box.setObjectName("text_box")
        self.message = QtWidgets.QLabel(parent=self.content_box)
        self.message.setStyleSheet("font-size: 13px;")
        self.message.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading
            | QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.message.setWordWrap(True)
        self.message.setObjectName("message")
        self.text_box.addWidget(self.message)
        self.details = QtWidgets.QLabel(parent=self.content_box)
        self.details.setStyleSheet("font-size: 11px;")
        self.details.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading
            | QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.details.setWordWrap(True)
        self.details.setObjectName("details")
        self.text_box.addWidget(self.details)
        self.content_box_horizontal_layout.addLayout(self.text_box)
        self.content_box_layout.addLayout(self.content_box_horizontal_layout)
        spacerItem = QtWidgets.QSpacerItem(
            20,
            5,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.content_box_layout.addItem(spacerItem)
        self.progress_bar_layout = QtWidgets.QVBoxLayout()
        self.progress_bar_layout.setContentsMargins(-1, -1, -1, 0)
        self.progress_bar_layout.setObjectName("progress_bar_layout")
        self.progress_bar = QtWidgets.QProgressBar(parent=self.content_box)
        self.progress_bar.setMinimumSize(QtCore.QSize(200, 0))
        self.progress_bar.setMaximumSize(QtCore.QSize(16777215, 20))
        self.progress_bar.setStyleSheet(
            "QProgressBar\n"
            "{\n"
            "    color: #ffffff;\n"
            "    border-style: outset;\n"
            "border-width: 2px;\n"
            "    border-radius: 5px;\n"
            "    text-align: left;\n"
            "}\n"
            "QProgressBar::chunk\n"
            "{\n"
            "    background-color:#e06133;\n"
            "}"
        )
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar_layout.addWidget(self.progress_bar)
        self.content_box_layout.addLayout(self.progress_bar_layout)
        self.navigation_buttons = QtWidgets.QFrame(parent=self.content_box)
        self.navigation_buttons.setMaximumSize(QtCore.QSize(16777215, 40))
        self.navigation_buttons.setObjectName("navigation_buttons")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.navigation_buttons)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem1 = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_6.addItem(spacerItem1)
        self.left_button = QtWidgets.QPushButton(parent=self.navigation_buttons)
        self.left_button.setEnabled(True)
        self.left_button.setMinimumSize(QtCore.QSize(80, 30))
        self.left_button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.left_button.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.left_button.setObjectName("left_button")
        self.horizontalLayout_6.addWidget(self.left_button)
        spacerItem2 = QtWidgets.QSpacerItem(
            5,
            20,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_6.addItem(spacerItem2)
        self.right_button = QtWidgets.QPushButton(parent=self.navigation_buttons)
        self.right_button.setEnabled(True)
        self.right_button.setMinimumSize(QtCore.QSize(80, 30))
        self.right_button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.right_button.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.right_button.setStyleSheet(
            ":disabled {background-color: rgb(52, 59, 72); color: rgba(255, 255, 255, 10%) }"
        )
        self.right_button.setObjectName("right_button")
        self.horizontalLayout_6.addWidget(self.right_button)
        self.content_box_layout.addWidget(self.navigation_buttons)
        self.content_top_bg = QtWidgets.QFrame(parent=multipurpose_dialog)
        self.content_top_bg.setGeometry(QtCore.QRect(0, 0, 400, 50))
        self.content_top_bg.setMinimumSize(QtCore.QSize(400, 50))
        self.content_top_bg.setMaximumSize(QtCore.QSize(16777215, 50))
        self.content_top_bg.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.content_top_bg.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.content_top_bg.setObjectName("content_top_bg")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.content_top_bg)
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.left_box = QtWidgets.QFrame(parent=self.content_top_bg)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left_box.sizePolicy().hasHeightForWidth())
        self.left_box.setSizePolicy(sizePolicy)
        self.left_box.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.left_box.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.left_box.setObjectName("left_box")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.left_box)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.logo_container = QtWidgets.QFrame(parent=self.left_box)
        self.logo_container.setMinimumSize(QtCore.QSize(60, 0))
        self.logo_container.setMaximumSize(QtCore.QSize(60, 16777215))
        self.logo_container.setObjectName("logo_container")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.logo_container)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.top_logo = QtWidgets.QLabel(parent=self.logo_container)
        self.top_logo.setMinimumSize(QtCore.QSize(42, 42))
        self.top_logo.setMaximumSize(QtCore.QSize(42, 42))
        self.top_logo.setText("")
        self.top_logo.setPixmap(QtGui.QPixmap(":/images/images/logo-42x42.png"))
        self.top_logo.setObjectName("top_logo")
        self.horizontalLayout_8.addWidget(self.top_logo)
        self.horizontalLayout_3.addWidget(self.logo_container)
        self.title_right_info = QtWidgets.QLabel(parent=self.left_box)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.title_right_info.sizePolicy().hasHeightForWidth()
        )
        self.title_right_info.setSizePolicy(sizePolicy)
        self.title_right_info.setMaximumSize(QtCore.QSize(16777215, 45))
        self.title_right_info.setStyleSheet("font: 12pt;")
        self.title_right_info.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading
            | QtCore.Qt.AlignmentFlag.AlignLeft
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.title_right_info.setObjectName("title_right_info")
        self.horizontalLayout_3.addWidget(self.title_right_info)
        self.horizontalLayout.addWidget(self.left_box)
        self.right_buttons = QtWidgets.QFrame(parent=self.content_top_bg)
        self.right_buttons.setMinimumSize(QtCore.QSize(0, 28))
        self.right_buttons.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.right_buttons.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.right_buttons.setObjectName("right_buttons")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.right_buttons)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.close_button = QtWidgets.QPushButton(parent=self.right_buttons)
        self.close_button.setMinimumSize(QtCore.QSize(28, 28))
        self.close_button.setMaximumSize(QtCore.QSize(28, 28))
        self.close_button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.close_button.setToolTip("")
        self.close_button.setIconSize(QtCore.QSize(20, 20))
        self.close_button.setObjectName("close_button")
        self.horizontalLayout_2.addWidget(self.close_button)
        self.horizontalLayout.addWidget(
            self.right_buttons, 0, QtCore.Qt.AlignmentFlag.AlignRight
        )

        self.retranslateUi(multipurpose_dialog)
        QtCore.QMetaObject.connectSlotsByName(multipurpose_dialog)

    def retranslateUi(self, multipurpose_dialog):
        _translate = QtCore.QCoreApplication.translate
        multipurpose_dialog.setWindowTitle(_translate("multipurpose_dialog", "Dialog"))
        self.message.setText(
            _translate("multipurpose_dialog", "Lorem ipsum dolor sit amet")
        )
        self.details.setText(
            _translate("multipurpose_dialog", "Lorem ipsum dolor sit amet")
        )
        self.left_button.setText(_translate("multipurpose_dialog", "Left"))
        self.right_button.setText(_translate("multipurpose_dialog", "Right"))
        self.title_right_info.setText(_translate("multipurpose_dialog", "TITLE"))
        self.close_button.setText(_translate("multipurpose_dialog", "Skip"))
