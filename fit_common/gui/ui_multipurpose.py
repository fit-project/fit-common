# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'multipurpose.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_multipurpose_dialog(object):
    def setupUi(self, multipurpose_dialog):
        if not multipurpose_dialog.objectName():
            multipurpose_dialog.setObjectName(u"multipurpose_dialog")
        multipurpose_dialog.resize(400, 300)
        multipurpose_dialog.setMinimumSize(QSize(400, 0))
        multipurpose_dialog.setMaximumSize(QSize(16777215, 16777215))
        multipurpose_dialog.setStyleSheet(u"QWidget{\n"
"	color: rgb(221, 221, 221);\n"
"}\n"
"\n"
"/* Content App */\n"
"#content_top_bg{	\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"\n"
"/* Top Buttons */\n"
"#right_buttons .QPushButton { background-color: rgba(255, 255, 255, 0); border: none;  border-radius: 5px; }\n"
"#right_buttons .QPushButton:hover { background-color: rgb(44, 49, 57); border-style: solid; border-radius: 4px; }\n"
"#right_buttons .QPushButton:pressed { background-color: rgb(23, 26, 30); border-style: solid; border-radius: 4px; }\n"
"")
        self.content_box = QFrame(multipurpose_dialog)
        self.content_box.setObjectName(u"content_box")
        self.content_box.setGeometry(QRect(0, 50, 400, 251))
        self.content_box.setMinimumSize(QSize(400, 0))
        self.content_box.setStyleSheet(u"background-color: rgb(40, 44, 52);")
        self.content_box_layout = QVBoxLayout(self.content_box)
        self.content_box_layout.setObjectName(u"content_box_layout")
        self.content_box_layout.setContentsMargins(12, 12, 12, 12)
        self.content_box_horizontal_layout = QHBoxLayout()
        self.content_box_horizontal_layout.setObjectName(u"content_box_horizontal_layout")
        self.content_box_horizontal_layout.setContentsMargins(-1, -1, -1, 0)
        self.icon_severity = QLabel(self.content_box)
        self.icon_severity.setObjectName(u"icon_severity")
        self.icon_severity.setMaximumSize(QSize(42, 42))
        self.icon_severity.setFrameShape(QFrame.NoFrame)

        self.content_box_horizontal_layout.addWidget(self.icon_severity)

        self.text_box = QVBoxLayout()
        self.text_box.setObjectName(u"text_box")
        self.text_box.setContentsMargins(10, -1, -1, 0)
        self.message = QLabel(self.content_box)
        self.message.setObjectName(u"message")
        self.message.setStyleSheet(u"font-size: 13px;")
        self.message.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.message.setWordWrap(True)

        self.text_box.addWidget(self.message)

        self.details = QLabel(self.content_box)
        self.details.setObjectName(u"details")
        self.details.setStyleSheet(u"font-size: 11px;")
        self.details.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.details.setWordWrap(True)

        self.text_box.addWidget(self.details)


        self.content_box_horizontal_layout.addLayout(self.text_box)


        self.content_box_layout.addLayout(self.content_box_horizontal_layout)

        self.vertical_spacer = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.content_box_layout.addItem(self.vertical_spacer)

        self.progress_bar_layout = QVBoxLayout()
        self.progress_bar_layout.setObjectName(u"progress_bar_layout")
        self.progress_bar_layout.setContentsMargins(-1, -1, -1, 0)
        self.progress_bar = QProgressBar(self.content_box)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setMinimumSize(QSize(200, 0))
        self.progress_bar.setMaximumSize(QSize(16777215, 20))
        self.progress_bar.setStyleSheet(u"QProgressBar\n"
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
"}")
        self.progress_bar.setValue(24)

        self.progress_bar_layout.addWidget(self.progress_bar)


        self.content_box_layout.addLayout(self.progress_bar_layout)

        self.navigation_buttons = QFrame(self.content_box)
        self.navigation_buttons.setObjectName(u"navigation_buttons")
        self.navigation_buttons.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout_6 = QHBoxLayout(self.navigation_buttons)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.left_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.left_spacer)

        self.left_button = QPushButton(self.navigation_buttons)
        self.left_button.setObjectName(u"left_button")
        self.left_button.setEnabled(True)
        self.left_button.setMinimumSize(QSize(80, 30))
        self.left_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.left_button.setLayoutDirection(Qt.LeftToRight)

        self.horizontalLayout_6.addWidget(self.left_button)

        self.between_spacer = QSpacerItem(5, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.between_spacer)

        self.right_button = QPushButton(self.navigation_buttons)
        self.right_button.setObjectName(u"right_button")
        self.right_button.setEnabled(True)
        self.right_button.setMinimumSize(QSize(80, 30))
        self.right_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.right_button.setLayoutDirection(Qt.LeftToRight)
        self.right_button.setStyleSheet(u":disabled {background-color: rgb(52, 59, 72); color: rgba(255, 255, 255, 10%) }")

        self.horizontalLayout_6.addWidget(self.right_button)


        self.content_box_layout.addWidget(self.navigation_buttons)

        self.content_top_bg = QFrame(multipurpose_dialog)
        self.content_top_bg.setObjectName(u"content_top_bg")
        self.content_top_bg.setGeometry(QRect(0, 0, 400, 50))
        self.content_top_bg.setMinimumSize(QSize(400, 50))
        self.content_top_bg.setMaximumSize(QSize(16777215, 50))
        self.content_top_bg.setFrameShape(QFrame.NoFrame)
        self.content_top_bg.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.content_top_bg)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.left_box = QFrame(self.content_top_bg)
        self.left_box.setObjectName(u"left_box")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left_box.sizePolicy().hasHeightForWidth())
        self.left_box.setSizePolicy(sizePolicy)
        self.left_box.setFrameShape(QFrame.NoFrame)
        self.left_box.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.left_box)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.logo_container = QFrame(self.left_box)
        self.logo_container.setObjectName(u"logo_container")
        self.logo_container.setMinimumSize(QSize(60, 0))
        self.logo_container.setMaximumSize(QSize(60, 16777215))
        self.horizontalLayout_8 = QHBoxLayout(self.logo_container)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.top_logo = QLabel(self.logo_container)
        self.top_logo.setObjectName(u"top_logo")
        self.top_logo.setMinimumSize(QSize(42, 42))
        self.top_logo.setMaximumSize(QSize(42, 42))
        self.top_logo.setPixmap(QPixmap(u"../images/logo-42x42.png"))

        self.horizontalLayout_8.addWidget(self.top_logo)


        self.horizontalLayout_3.addWidget(self.logo_container)

        self.title_right_info = QLabel(self.left_box)
        self.title_right_info.setObjectName(u"title_right_info")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.title_right_info.sizePolicy().hasHeightForWidth())
        self.title_right_info.setSizePolicy(sizePolicy1)
        self.title_right_info.setMaximumSize(QSize(16777215, 45))
        self.title_right_info.setStyleSheet(u"font: 12pt;")
        self.title_right_info.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.title_right_info)


        self.horizontalLayout.addWidget(self.left_box)

        self.right_buttons = QFrame(self.content_top_bg)
        self.right_buttons.setObjectName(u"right_buttons")
        self.right_buttons.setMinimumSize(QSize(0, 28))
        self.right_buttons.setFrameShape(QFrame.NoFrame)
        self.right_buttons.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.right_buttons)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.close_button = QPushButton(self.right_buttons)
        self.close_button.setObjectName(u"close_button")
        self.close_button.setMinimumSize(QSize(28, 28))
        self.close_button.setMaximumSize(QSize(28, 28))
        self.close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_button.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.close_button)


        self.horizontalLayout.addWidget(self.right_buttons, 0, Qt.AlignRight)


        self.retranslateUi(multipurpose_dialog)

        QMetaObject.connectSlotsByName(multipurpose_dialog)
    # setupUi

    def retranslateUi(self, multipurpose_dialog):
        multipurpose_dialog.setWindowTitle(QCoreApplication.translate("multipurpose_dialog", u"Dialog", None))
        self.icon_severity.setText("")
        self.message.setText(QCoreApplication.translate("multipurpose_dialog", u"Lorem ipsum dolor sit amet", None))
        self.details.setText(QCoreApplication.translate("multipurpose_dialog", u"Lorem ipsum dolor sit amet", None))
        self.left_button.setText(QCoreApplication.translate("multipurpose_dialog", u"Left", None))
        self.right_button.setText(QCoreApplication.translate("multipurpose_dialog", u"Right", None))
        self.top_logo.setText("")
        self.title_right_info.setText(QCoreApplication.translate("multipurpose_dialog", u"TITLE", None))
#if QT_CONFIG(tooltip)
        self.close_button.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.close_button.setText(QCoreApplication.translate("multipurpose_dialog", u"Skip", None))
    # retranslateUi

