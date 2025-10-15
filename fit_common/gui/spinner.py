import os
import sys
import threading
import time

from PySide6.QtCore import QEvent, QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# ---------------- Spinner autosufficiente (file GIF) ----------------
class Spinner(QObject):
    _ui_start = Signal()
    _ui_stop = Signal()

    def __init__(
        self, parent: QWidget, gif_path: str = "spinner.gif", opacity: int = 160
    ):
        super().__init__(parent)
        self._parent = parent
        self._gif_path = gif_path

        # Overlay full-screen sul parent
        self._overlay = QWidget(parent)
        self._overlay.setAttribute(Qt.WA_StyledBackground, True)
        self._overlay.setStyleSheet(f"background-color: rgba(255,255,255,{opacity});")
        self._overlay.hide()

        # Label centrale
        self._label = QLabel(self._overlay)
        self._label.setAlignment(Qt.AlignCenter)

        # Prova a caricare la GIF
        self._movie = None
        if os.path.exists(self._gif_path):
            self._movie = QMovie(self._gif_path)
            self._label.setMovie(self._movie)
        else:
            # Fallback: testo se la gif non c'è
            self._label.setText("Caricamento…")

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

    # --- UI (solo main thread)
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


# --------------- Worker su QThread (lavoro lungo / rete) ---------------
class NetworkWorker(QObject):
    finished = Signal(bool, str)  # success, message

    def __init__(self, url: str = "wss://example.org/socket"):
        super().__init__()
        self._url = url
        self._cancel = threading.Event()

    @Slot()
    def run(self):
        try:
            for _ in range(16):  # 16 * 0.5s = 8s
                if self._cancel.is_set():
                    self.finished.emit(False, "Annullato dall'utente")
                    return
                time.sleep(0.5)  # qui metteresti I/O non bloccante/timeout
            self.finished.emit(True, "Connessione completata")
        except Exception as e:
            self.finished.emit(False, f"Errore: {e}")

    def cancel(self):
        self._cancel.set()


# -------------------------- Demo con Start/Stop --------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spinner + QThread (Start/Stop)")

        self.btn_start = QPushButton("Start (connessione)")
        self.btn_stop = QPushButton("Stop")
        self.status = QLabel("Pronto")

        layout = QVBoxLayout()
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.status)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

        # Spinner riusabile (passa qui il percorso se diverso)
        self.spinner = Spinner(self, gif_path="spinner.gif")

        # Connessioni pulsanti
        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_stop.clicked.connect(self.on_stop_clicked)

        self._thread: QThread | None = None
        self._worker: NetworkWorker | None = None

        self.btn_stop.setEnabled(False)
        self.resize(520, 300)

    def on_start_clicked(self):
        if self._thread is not None:  # già in corso
            return

        # Avvia spinner (UI nel main thread, non blocca)
        self.spinner.start()
        self.status.setText("Connessione in corso…")
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)

        # Prepara il worker nel suo QThread
        self._thread = QThread()
        self._worker = NetworkWorker(url="wss://example.org/socket")
        self._worker.moveToThread(self._thread)

        # Wiring segnali
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self.on_worker_finished)

        # Pulizia quando il thread finisce
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(self._worker.deleteLater)

        self._thread.start()

    def on_stop_clicked(self):
        if self._worker:
            self._worker.cancel()
        self.spinner.stop()  # UI immediata
        self.status.setText("Annullamento richiesto…")
        self.btn_stop.setEnabled(False)

    @Slot(bool, str)
    def on_worker_finished(self, ok: bool, msg: str):
        self.spinner.stop()
        self.status.setText(msg if msg else ("OK" if ok else "Fallito"))

        self._worker = None
        self._thread = None

        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
