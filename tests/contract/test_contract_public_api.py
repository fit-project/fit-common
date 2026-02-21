import pytest

import fit_common.core as core


@pytest.mark.contract
def test_core_public_api_symbols_are_available():
    required = {
        "resolve_path",
        "resolve_log_path",
        "resolve_db_path",
        "resolve_app_path",
        "AcquisitionType",
        "get_platform",
        "get_system_lang",
        "DEFAULT_LANG",
        "is_admin",
        "is_npcap_installed",
        "is_cmd",
        "is_bundled",
        "find_free_port",
        "get_ntp_date_and_time",
        "get_context",
        "debug",
        "DEBUG_LEVEL",
        "DebugLevel",
        "set_debug_level",
        "log_exception",
        "handle_crash",
        "set_gui_crash_handler",
        "get_version",
        "get_remote_tag_version",
        "has_new_release_version",
    }

    missing = [name for name in required if not hasattr(core, name)]
    assert not missing, f"Missing exported symbols: {missing}"


@pytest.mark.contract
def test_core_all_contains_stable_subset():
    stable_subset = {
        "resolve_path",
        "resolve_log_path",
        "resolve_db_path",
        "resolve_app_path",
        "AcquisitionType",
        "get_version",
        "get_remote_tag_version",
        "has_new_release_version",
    }
    assert stable_subset.issubset(set(core.__all__))
