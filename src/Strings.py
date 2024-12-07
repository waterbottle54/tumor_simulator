"""
Strings.py

이 모듈에서는 문자열 리소스를 보관합니다.
"""

# Copyright (c) 2023 Sung Won Jo
# For more details: https://github.com/waterbottle54/tumor_simulator

import os
import sys
from Consts import debug_or_release

version_name = '1.02'

#====================================== URLs ==============================================

url_github = 'https://github.com/waterbottle54/tumor_simulator'
url_youtube = 'https://www.youtube.com/channel/UChfv3TOHGociOKYMXSzS6hw'

#===================================== Contact ============================================

email = 'waterbottle54@naver.com'

#=================================== Directories ==========================================

dir_icons = 'resources/icons'

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_image_path(filename: str):
    """Get absolute path of the image whose name is given by the arguement.
    The path may differ depending on whether its debug mode or release mode (See consts.py).

    Args:
        filename (str): The name of the image, not including its directory.

    Returns:
        str: The absolute path of an image
    """
    return dir_icons + f'/{filename}' if debug_or_release else resource_path(filename)

#==================================== About Text ==========================================
about_text = f"""
Brain Tumor Simulator {version_name}


Purpose: Tumor volume measurement, comparison, and analysis

Disclaimer: This software is not intended to replace professional medical diagnosis.

Copyright 2023. Sung Won Jo. All rights reserved.


Contact: {email}
"""

#==================================== Tip Text ==========================================
# Used in TipsDialog.py
tip_text = """
Move Camera: \t Left Button Drag

Zoom In/Out: \t Mouse Wheel

Mark Tumor: \t Right Button Drag

Change Layer: \t Ctrl + Mouse Wheel

Skip Layers: \t Page Up / Page Down

Skip All Layers: \t Home / End

Zoom 3D Tumor: \t Mouse Wheel

Rotate 3D Tumor: \t Mouse Drag


* Import folder that directly contains DICOM files.

* Importing may take up to two minutes.

* Project documents are *.bts files.

* Tumor object files are *.tmr files.
"""