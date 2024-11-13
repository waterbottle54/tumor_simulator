"""
Strings.py

이 모듈에서는 문자열 리소스를 보관합니다.
"""

# Copyright (c) 2023 Sung Won Jo
# For more details: https://github.com/waterbottle54/tumor_simulator

import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#=================================== Directories ==========================================

dir_icons = 'resources/icons'

#==================================== About Text ==========================================
about_text = """
Brain Tumor Simulator 1.0


Purpose: Tumor volume measurement, comparison, and analysis

Disclaimer: This software is not intended to replace professional medical diagnosis.

Copyright 2023. Sung Won Jo. All rights reserved.


Contact: waterbottle54@naver.com
"""

#==================================== Tip Text ==========================================
# Used in TipsDialog.py
tip_text = """
Zoom Image: \t Ctrl + Mouse Wheel

Move Focus: \t Right Drag

Mark Tumor: \t Left Drag

Change Layer: \t Mouse Wheel

Skip Layers: \t Page Up / Page Down

Skip All Layers: \t Home / End

Zoom 3D Tumor: \t Mouse Wheel

Rotate 3D Tumor: \t Mouse Drag


* Import folder that directly contains DICOM files.

* Importing may take up to two minutes.

* Project documents are *.bts files.

* Tumor object files are *.tmr files.
        """