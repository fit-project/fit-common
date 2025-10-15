import os
from importlib.resources import files

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
)

from fit_common.lang import load_translations


class Spinner(QObject):
    _ui_start = Signal()
    _ui_stop = Signal()

    def __init__(self, parent: QWidget, opacity: int = 160):
        super().__init__(parent)
        self._parent = parent
        self._gif_path = files("fit_assets.images") / "spinner.gif"

        self.__translations = load_translations()

        self._overlay = QWidget(parent)
        self._overlay.setAttribute(Qt.WA_StyledBackground, True)
        self._overlay.setStyleSheet(f"background-color: rgba(255,255,255,{opacity});")
        self._overlay.hide()

        self._label = QLabel(self._overlay)
        self._label.setAlignment(Qt.AlignCenter)

        self._movie = None
        if os.path.exists(self._gif_path):
            self._movie = QMovie(str(self._gif_path))
            self._label.setMovie(self._movie)
        else:
            self._label.setText(self.__translations["LOADING"])

        # Segnali per garantire esecuzione in main thread
        self._ui_start.connect(self.__ui_start)
        self._ui_stop.connect(self.__ui_stop)

        # Mantieni l’overlay sincronizzato con il parent
        self._sync_geometry()
        parent.installEventFilter(self)

    # API pubblica
    def start(self):
        self._ui_start.emit()

    def stop(self):
        self._ui_stop.emit()

    def __ui_start(self):
        self._sync_geometry()
        self._overlay.show()
        if self._movie:
            self._movie.start()

    def __ui_stop(self):
        if self._movie:
            self._movie.stop()
        self._overlay.hide()

    def _sync_geometry(self):
        self._overlay.setGeometry(self._parent.rect())
        self._label.setGeometry(self._overlay.rect())

    def eventFilter(self, watched, event):
        if watched is self._parent and event.type() in (QEvent.Resize, QEvent.Show):
            self._sync_geometry()
        return super().eventFilter(watched, event)
