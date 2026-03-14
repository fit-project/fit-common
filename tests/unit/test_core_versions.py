from fit_common.core import versions


class _Resp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def test_find_pyproject_walks_up(tmp_path):
    root = tmp_path / "repo"
    nested = root / "a" / "b"
    nested.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[tool.poetry]\nversion='1.2.3'\n", encoding="utf-8")
    found = versions.find_pyproject(nested)
    assert found == root / "pyproject.toml"


def test_get_version_reads_pyproject(tmp_path):
    proj = tmp_path / "pyproject.toml"
    proj.write_text("[tool.poetry]\nversion='9.9.9'\n", encoding="utf-8")
    value = versions.get_version(tmp_path)
    assert value == "9.9.9"


def test_get_remote_tag_version(monkeypatch):
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda url, timeout: _Resp([{"name": "v2.0.0"}]),
    )
    assert versions.get_remote_tag_version("fit-common") == "v2.0.0"


def test_get_latest_release_payload_returns_payload(monkeypatch):
    monkeypatch.setattr(
        versions.requests,
        "get",
        lambda url, timeout: _Resp({"tag_name": "v1.1.0"}),
    )
    assert versions.get_latest_release_payload("fit-common") == {"tag_name": "v1.1.0"}


def test_get_latest_release_payload_handles_request_exception(monkeypatch):
    def _boom(*args, **kwargs):
        raise versions.requests.RequestException("network")

    monkeypatch.setattr(versions.requests, "get", _boom)
    assert versions.get_latest_release_payload("fit-common") == {}
