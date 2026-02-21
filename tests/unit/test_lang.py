import json

from fit_common import lang


def test_load_translations_specific_language(monkeypatch, tmp_path):
    monkeypatch.setattr(lang, "LANG_DIR", tmp_path)
    (tmp_path / "it.json").write_text(json.dumps({"HELLO": "ciao"}), encoding="utf-8")
    data = lang.load_translations("it")
    assert data["HELLO"] == "ciao"


def test_load_translations_falls_back_to_default(monkeypatch, tmp_path):
    monkeypatch.setattr(lang, "LANG_DIR", tmp_path)
    monkeypatch.setattr(lang, "DEFAULT_LANG", "en")
    (tmp_path / "en.json").write_text(json.dumps({"HELLO": "hello"}), encoding="utf-8")
    data = lang.load_translations("zz")
    assert data["HELLO"] == "hello"
