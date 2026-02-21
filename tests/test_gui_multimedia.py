from fit_common.gui import multimedia


class _Dev:
    def __init__(self, text):
        self._text = text

    def description(self):
        return self._text


class _MediaDevices:
    def __init__(self, inputs=None, outputs=None):
        self._inputs = inputs or []
        self._outputs = outputs or []

    def audioInputs(self):
        return self._inputs

    def audioOutputs(self):
        return self._outputs


def test_is_installed_ffmpeg(monkeypatch):
    monkeypatch.setattr(multimedia, "is_cmd", lambda name: name == "ffmpeg")
    assert multimedia.is_installed_ffmpeg() is True


def test_get_vb_cable_virtual_audio_device_found(monkeypatch):
    monkeypatch.setattr(
        multimedia,
        "QMediaDevices",
        lambda: _MediaDevices(inputs=[_Dev("Mic"), _Dev("VB-Cable Output")]),
    )
    dev = multimedia.get_vb_cable_virtual_audio_device()
    assert dev is not None
    assert "VB-Cable" in dev.description()


def test_is_vb_cable_first_output_audio_device(monkeypatch):
    monkeypatch.setattr(
        multimedia,
        "QMediaDevices",
        lambda: _MediaDevices(outputs=[_Dev("Virtual Cable Main"), _Dev("Speaker")]),
    )
    assert multimedia.is_vb_cable_first_ouput_audio_device() is True


def test_enable_audio_recording_requires_all_conditions(monkeypatch):
    monkeypatch.setattr(multimedia, "is_installed_ffmpeg", lambda: True)
    monkeypatch.setattr(multimedia, "get_vb_cable_virtual_audio_device", lambda: object())
    monkeypatch.setattr(multimedia, "is_vb_cable_first_ouput_audio_device", lambda: True)
    assert multimedia.enable_audio_recording() is True

    monkeypatch.setattr(multimedia, "is_vb_cable_first_ouput_audio_device", lambda: False)
    assert multimedia.enable_audio_recording() is False
