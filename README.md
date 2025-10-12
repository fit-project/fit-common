# fit-common

Core library shared across all **FIT Project** modules.  
This repository provides common utilities, error handling, version management, and reusable components that power the FIT modular ecosystem.

---

## Purpose
- Provide a **centralized core** for shared logic used by all FIT modules.
- Offer **utility functions** and **base classes** to standardize module behavior.
- Simplify maintenance and ensure **consistency** across the FIT ecosystem.

---

## Features
- 🔧 **Error and crash handling** (`fit_common/core/error_handler.py`, `crash_handler.py`)
- 🧩 **Debug utilities** and logging (`debug.py`)
- 📦 **Version management** (`fit_common/core/utils/versions.py`)
- 🧠 **Cross-module constants** and configuration helpers
- 🧪 **Tests and stubs** for module integration

---

## Requirements
- **Python** 3.11
- **Poetry** (recommended for development)

---

## Installation

### As dependency
```bash
poetry add git+https://github.com/fit-project/fit-common.git@main
# or
pip install git+https://github.com/fit-project/fit-common.git@main
```

### For local development
```bash
git clone https://github.com/fit-project/fit-common.git
cd fit-common
poetry install
```

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
