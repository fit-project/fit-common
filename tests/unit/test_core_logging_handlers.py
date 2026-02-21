from importlib import import_module

import pytest

crash_handler = import_module("fit_common.core.crash_handler")
debug_mod = import_module("fit_common.core.debug")
error_handler = import_module("fit_common.core.error_handler")


@pytest.fixture(autouse=True)
def _reset_crash_handler_state(monkeypatch):
    monkeypatch.setattr(crash_handler, "_gui_crash_callback", None)


def test_debug_none_level_does_not_log(monkeypatch):
    calls = []
    debug_mod.set_debug_level(debug_mod.DebugLevel.NONE)
    monkeypatch.setattr(debug_mod.logger, "debug", lambda msg: calls.append(msg))
    debug_mod.debug("hello", context="ctx")
    assert calls == []


def test_debug_log_level_logs(monkeypatch):
    calls = []
    debug_mod.set_debug_level(debug_mod.DebugLevel.LOG)
    monkeypatch.setattr(debug_mod.logger, "debug", lambda msg: calls.append(msg))
    debug_mod.debug("hello", 123, context="ctx")
    assert calls
    assert "ctx: hello 123" in calls[0]


def test_debug_verbose_prints(monkeypatch):
    prints = []
    debug_mod.set_debug_level(debug_mod.DebugLevel.VERBOSE)
    monkeypatch.setattr(debug_mod.logger, "debug", lambda msg: None)
    monkeypatch.setattr("builtins.print", lambda msg: prints.append(msg))
    debug_mod.debug("line", context="ctx")
    assert prints
    assert "ctx: line" in prints[0]


def test_log_exception_writes_error(monkeypatch):
    calls = []
    monkeypatch.setattr(error_handler.logger, "error", lambda msg: calls.append(msg))
    error_handler.log_exception(ValueError("boom"), context="load")
    assert calls
    assert "load: boom" in calls[0]


def test_handle_crash_dev_calls_system_hook(monkeypatch):
    received = []
    monkeypatch.setattr(crash_handler.sys, "frozen", False, raising=False)
    monkeypatch.setattr(crash_handler.sys, "__excepthook__", lambda et, ev, tb: received.append((et, ev)))
    crash_handler.handle_crash(ValueError, ValueError("x"), None)
    assert received


def test_handle_crash_frozen_logs_and_callback(monkeypatch):
    logs = []
    callback_logs = []
    monkeypatch.setattr(crash_handler.sys, "frozen", True, raising=False)
    monkeypatch.setattr(crash_handler.logger, "error", lambda msg, *args: logs.append(msg))
    crash_handler.set_gui_crash_handler(lambda text: callback_logs.append(text))
    crash_handler.handle_crash(RuntimeError, RuntimeError("fatal"), None)
    assert logs
    assert callback_logs


def test_handle_crash_frozen_callback_failure_is_logged(monkeypatch):
    debug_calls = []
    monkeypatch.setattr(crash_handler.sys, "frozen", True, raising=False)
    monkeypatch.setattr(
        crash_handler,
        "debug",
        lambda *args, **kwargs: debug_calls.append((args, kwargs)),
    )

    def _bad_callback(text):
        raise RuntimeError("ui-error")

    crash_handler.set_gui_crash_handler(_bad_callback)
    crash_handler.handle_crash(RuntimeError, RuntimeError("fatal"), None)
    assert debug_calls
    assert "Failed to show GUI crash dialog:" in debug_calls[0][0][0]
