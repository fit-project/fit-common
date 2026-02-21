from pathlib import Path

import pytest

import fit_common.core.paths as paths
import fit_common.core.versions as versions
import fit_common.gui.utils as gui_utils


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class _Dialog:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


@pytest.mark.contract
@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
def test_resolve_app_path_contract_for_frozen_build(platform, monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "frozen", True, raising=False)
    monkeypatch.setattr(paths.sys, "platform", platform)
    monkeypatch.setattr(
        paths.os.path,
        "expanduser",
        lambda p: str(tmp_path / p.replace("~", "home")),
    )
    result = Path(paths.resolve_app_path("FIT_CONTRACT"))
    assert result.exists()
    assert result.name == "FIT_CONTRACT"


@pytest.mark.contract
def test_get_remote_tag_version_contract_uses_github_tags_endpoint(monkeypatch):
    captured = {}

    def _fake_get(url, timeout):
        captured["url"] = url
        captured["timeout"] = timeout
        return _Resp([{"name": "v2.3.4"}])

    monkeypatch.setattr(versions.requests, "get", _fake_get)
    tag = versions.get_remote_tag_version("fit-common")

    assert tag == "v2.3.4"
    assert captured["url"].endswith("/repos/fit-project/fit-common/tags")
    assert captured["timeout"] == 5


@pytest.mark.contract
def test_has_new_release_version_contract_compares_versions_when_frozen(monkeypatch):
    monkeypatch.setattr(versions.sys, "frozen", True, raising=False)
    monkeypatch.setattr(versions, "get_local_version", lambda: "1.0.0", raising=False)
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda url, timeout: _Resp({"tag_name": "v1.1.0"}),
    )
    assert versions.has_new_release_version("fit-common") is True


@pytest.mark.contract
def test_gui_verification_report_open_contract_windows(monkeypatch, tmp_path):
    calls = []
    dialog = _Dialog()
    monkeypatch.setattr(gui_utils, "get_platform", lambda: "win")
    monkeypatch.setattr(gui_utils.os, "startfile", lambda path: calls.append(path), raising=False)
    gui_utils.__open_verification_report(dialog, str(tmp_path), gui_utils.VerificationTypes.PEC)
    assert dialog.closed is True
    assert calls
    assert calls[0].endswith("report_integrity_pec_verification.pdf")


@pytest.mark.contract
def test_gui_acquisition_open_contract_non_windows(monkeypatch, tmp_path):
    calls = []
    dialog = _Dialog()
    monkeypatch.setattr(gui_utils, "get_platform", lambda: "lin")
    monkeypatch.setattr(gui_utils.subprocess, "call", lambda cmd: calls.append(cmd))
    gui_utils.__open_acquisition_directory(dialog, str(tmp_path))
    assert dialog.closed is True
    assert calls == [["xdg-open", str(tmp_path)]]
