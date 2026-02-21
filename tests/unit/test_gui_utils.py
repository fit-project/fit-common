from fit_common.gui import utils as gui_utils


class _FakeDialog:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_verification_label_text_success_and_failure():
    ok = gui_utils.get_verification_label_text(
        "timestamp", gui_utils.Status.SUCCESS, "all good"
    )
    ko = gui_utils.get_verification_label_text(
        "timestamp", gui_utils.Status.FAILURE, ""
    )
    assert "color:green" in ok
    assert "details: all good" in ok
    assert "color:red" in ko


def test_open_verification_report_windows(monkeypatch, tmp_path):
    calls = []
    dialog = _FakeDialog()
    monkeypatch.setattr(gui_utils, "get_platform", lambda: "win")
    monkeypatch.setattr(gui_utils.os, "startfile", lambda path: calls.append(path), raising=False)
    gui_utils.__open_verification_report(
        dialog, str(tmp_path), gui_utils.VerificationTypes.TIMESTAMP
    )
    assert dialog.closed is True
    assert calls
    assert calls[0].endswith("report_timestamp_verification.pdf")


def test_open_verification_report_macos(monkeypatch, tmp_path):
    calls = []
    dialog = _FakeDialog()
    monkeypatch.setattr(gui_utils, "get_platform", lambda: "macos")
    monkeypatch.setattr(gui_utils.subprocess, "call", lambda cmd: calls.append(cmd))
    gui_utils.__open_verification_report(
        dialog, str(tmp_path), gui_utils.VerificationTypes.PEC
    )
    assert calls
    assert calls[0][0] == "open"
    assert calls[0][1].endswith("report_integrity_pec_verification.pdf")


def test_open_acquisition_directory_linux(monkeypatch, tmp_path):
    calls = []
    dialog = _FakeDialog()
    monkeypatch.setattr(gui_utils, "get_platform", lambda: "lin")
    monkeypatch.setattr(gui_utils.subprocess, "call", lambda cmd: calls.append(cmd))
    gui_utils.__open_acquisition_directory(dialog, str(tmp_path))
    assert dialog.closed is True
    assert calls == [["xdg-open", str(tmp_path)]]


def test_show_dialog_swallow_exceptions(monkeypatch):
    class _FakeQApplication:
        @staticmethod
        def instance():
            return object()

    class _BadDialog:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(gui_utils.QtWidgets, "QApplication", _FakeQApplication)
    monkeypatch.setattr(gui_utils, "Dialog", _BadDialog)
    gui_utils.show_dialog("error", "x", "y", "z")
