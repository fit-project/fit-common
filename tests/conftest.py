from pathlib import Path
import sys


# Ensure test imports always resolve against this checkout, not an installed wheel.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
project_root_str = str(PROJECT_ROOT)
if sys.path[0] != project_root_str:
    try:
        sys.path.remove(project_root_str)
    except ValueError:
        pass
    sys.path.insert(0, project_root_str)
