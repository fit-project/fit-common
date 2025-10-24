#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######


from PySide6.QtMultimedia import QMediaDevices

from fit_common.core.utils import is_cmd


def is_installed_ffmpeg():
    return is_cmd("ffmpeg")


def get_vb_cable_virtual_audio_device():
    for dev in QMediaDevices().audioInputs():
        if any(
            x in dev.description()
            for x in ["Virtual Cable", "CABLE Output", "VB-Audio", "VB-Cable"]
        ):
            return dev
    return None


def is_vb_cable_first_ouput_audio_device():
    for idx, dev in enumerate(QMediaDevices().audioOutputs()):
        if any(
            x in dev.description()
            for x in ["Virtual Cable", "CABLE Output", "VB-Audio", "VB-Cable"]
        ):
            return idx == 0
    return False


def enable_audio_recording():
    return (
        is_installed_ffmpeg()
        and get_vb_cable_virtual_audio_device()
        and is_vb_cable_first_ouput_audio_device()
    )
