#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# Copyright (c) 2023 FIT-Project
# SPDX-License-Identifier: GPL-3.0-only
# -----
######

from enum import Enum


class AcquisitionType(str, Enum):
    WEB = "web"
    ENTIRE_WEBSITE = "entire_website"
    EMAIL = "email"
    INSTAGRAM = "instagram"
    VIDEO = "video"
