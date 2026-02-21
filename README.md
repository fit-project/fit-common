# fit-common

Core library shared across all **FIT Project** modules.  
This repository provides common utilities, error handling, version management, and reusable components that power the FIT modular ecosystem.

---

## Purpose
- Provide a **centralized core** for shared logic used by all FIT modules.
- Offer **utility functions** and **base classes** to standardize module behavior.
- Simplify maintenance and ensure **consistency** across the FIT ecosystem.

---

## Requirements
- **Python** >=3.11,<3.14
- **Poetry** (recommended for development)
- **fit-assets** package available in the environment (runtime dependency used by `fit_common`)

---

## Installation

### As dependency
```bash
# install runtime assets package first
pip install git+https://github.com/fit-project/fit-assets.git@v1.0.0-rc1

# then install fit-common
poetry add git+https://github.com/fit-project/fit-common.git@main
# or
pip install git+https://github.com/fit-project/fit-common.git@main
```

### For local development
```bash
git clone https://github.com/fit-project/fit-common.git
cd fit-common
poetry install
pip install git+https://github.com/fit-project/fit-assets.git@v1.0.0-rc1
```

---

## Local checks (same as CI)

Run these commands before opening a PR, so failures are caught locally first.

### What each tool does
- `pytest`: runs automated tests (`unit`, `contract`, and `integration` suites).
- `ruff`: checks code style and common static issues (lint).
- `mypy`: performs static type checking on annotated Python code.
- `bandit`: scans source code for common security anti-patterns.
- `pip-audit`: checks installed dependencies for known CVEs.

### 1) Base setup
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install . pytest ruff mypy "bandit[toml]" pip-audit
```

### 2) Test suite
```bash
# unit tests
pytest -m "not contract and not integration" -q tests

# contract tests
pytest -m contract -q tests

# integration tests (requires fit-assets package)
pip install git+https://github.com/fit-project/fit-assets.git@v1.0.0-rc1
pytest -m integration -q tests
```

### 3) Quality and security checks
```bash
ruff check fit_common tests
mypy
bandit -c pyproject.toml -r fit_common -q -ll -ii
pip-audit --progress-spinner off
```

Note: `pip-audit` may print a skip message for `fit-common` because it is a local package and not published on PyPI.

---


## Usage examples

### Get local and remote versions
```python
from fit_common.core.utils.versions import (
    get_local_version,
    get_remote_tag_version,
    has_new_release_version
)

print("Local version:", get_local_version())
print("Latest remote:", get_remote_tag_version("fit-project/fit-common"))
```

### Handle controlled errors
```python
from fit_common.core.error_handler import handle_error

try:
    risky_operation()
except Exception as e:
    handle_error(e)
```

### Register crash handler
```python
from fit_common.core.crash_handler import register_crash_handler

register_crash_handler()
# The program will now log unhandled exceptions globally.
```

---

## Contributing
1. Fork this repository.  
2. Create a new branch (`git checkout -b feat/my-feature`).  
3. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).  
4. Submit a Pull Request describing your modification.

---
