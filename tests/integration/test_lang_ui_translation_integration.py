import pytest
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from fit_common.gui.ui_translation import translate_ui
from fit_common.lang import load_translations


def _ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.mark.integration
def test_translate_ui_with_real_lang_files_on_widgets_and_actions():
    _ensure_app()
    translations = load_translations("en")

    root = QWidget()
    layout = QVBoxLayout(root)

    button_ok = QPushButton("placeholder")
    button_ok.setObjectName("ok")
    layout.addWidget(button_ok)

    button_no = QPushButton("placeholder")
    button_no.setObjectName("no")
    layout.addWidget(button_no)

    action_yes = QAction("placeholder", root)
    action_yes.setObjectName("yes")
    root.addAction(action_yes)

    translate_ui(translations, root)

    assert button_ok.text() == translations["OK"]
    assert button_no.text() == translations["NO"]
    assert action_yes.text() == translations["YES"]
