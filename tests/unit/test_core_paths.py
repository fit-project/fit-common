from pathlib import Path

from fit_common.core import paths


def test_resolve_path_dev_uses_cwd(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "frozen", False, raising=False)
    monkeypatch.chdir(tmp_path)
    resolved = paths.resolve_path("assets/config.ini")
    assert resolved == str((tmp_path / "assets" / "config.ini").resolve())


def test_resolve_path_frozen_uses_meipass(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "_MEIPASS", str(tmp_path), raising=False)
    resolved = paths.resolve_path("x/y.txt")
    assert resolved == str((tmp_path / "x" / "y.txt").resolve())


def test_resolve_app_path_dev_creates_subfolder(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "frozen", False, raising=False)
    monkeypatch.chdir(tmp_path)
    app_path = Path(paths.resolve_app_path("FIT_TEST"))
    assert app_path.exists()
    assert app_path.name == "FIT_TEST"


def test_resolve_db_and_log_paths_create_directories(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "frozen", False, raising=False)
    monkeypatch.chdir(tmp_path)

    db_file = Path(paths.resolve_db_path("main.db"))
    log_file = Path(paths.resolve_log_path("app.log"))

    assert db_file.parent.exists()
    assert log_file.parent.exists()
    assert db_file.name == "main.db"
    assert log_file.name == "app.log"
