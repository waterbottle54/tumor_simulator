from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from Strings import tip_text
from Strings import dir_icons
from Strings import get_image_path

class TipsDialog(QDialog):
    """
    어플리케이션 사용법을 알려주는 간단한 대화상자
    A simple dialog that displays App instruction
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Tips")
        self.setStyleSheet("background-color: white;")

        # Create a QVBoxLayout to hold the content
        layout_top = QHBoxLayout()
        layout_top.setContentsMargins(32, 32, 32, 32)

        # Create a QLabel to display the application information
        label_tip = QLabel(tip_text)
        layout_top.addWidget(label_tip)

        layout_top.addSpacing(64)

        image_tip = QLabel()
        image_tip.setPixmap(QPixmap(get_image_path('tips.png')))
        image_tip.setContentsMargins(16, 16, 16, 16)
        layout_top.addWidget(image_tip)

        # Set the layout for the dialog
        self.setLayout(layout_top)