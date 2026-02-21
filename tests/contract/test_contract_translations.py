import json
import re
from pathlib import Path

import pytest


PATTERN = re.compile(r'translations\["([^"]+)"\]')


def _required_translation_keys() -> set[str]:
    base = Path("fit_common")
    keys: set[str] = set()
    for py_file in base.rglob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        if "load_translations(" not in text:
            continue
        for m in PATTERN.finditer(text):
            key = m.group(1)
            if key:
                keys.add(key)
    return keys


@pytest.mark.contract
def test_translation_keys_required_by_code_exist_in_en_and_it():
    required = _required_translation_keys()
    en = json.loads(Path("fit_common/lang/en.json").read_text(encoding="utf-8"))
    it = json.loads(Path("fit_common/lang/it.json").read_text(encoding="utf-8"))

    missing_en = sorted(required - set(en))
    missing_it = sorted(required - set(it))

    assert not missing_en, f"Missing translation keys in en.json: {missing_en}"
    assert not missing_it, f"Missing translation keys in it.json: {missing_it}"
