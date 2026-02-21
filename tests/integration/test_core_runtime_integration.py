import socket
from pathlib import Path

import pytest

from fit_common.core.paths import resolve_db_path, resolve_log_path, resolve_path
from fit_common.core.utils import find_free_port, get_context


@pytest.mark.integration
def test_paths_runtime_create_real_directories(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    resolved_asset = Path(resolve_path("assets/config.ini"))
    db_file = Path(resolve_db_path("main.db"))
    log_file = Path(resolve_log_path("app.log"))

    assert resolved_asset == (tmp_path / "assets" / "config.ini").resolve()
    assert db_file.parent.exists()
    assert log_file.parent.exists()
    assert db_file.name == "main.db"
    assert log_file.name == "app.log"


@pytest.mark.integration
def test_find_free_port_runtime_real_socket():
    try:
        port = find_free_port()
    except PermissionError:
        pytest.skip("Socket bind not permitted in this runtime environment.")

    assert isinstance(port, int)
    assert 1 <= port <= 65535

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", port))


@pytest.mark.integration
def test_get_context_runtime():
    class Probe:
        def call(self):
            return get_context(self)

    assert Probe().call() == "Probe.call"
