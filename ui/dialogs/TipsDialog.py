from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from utils.Strings import tip_text

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
        layout = QHBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)

        # Create a QLabel to display the application information
        label = QLabel(tip_text)
        layout.addWidget(label)

        layout.addSpacing(64)

        image = QLabel()
        image.setPixmap(QPixmap('icons/tips.png'))
        image.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(image)

        # Set the layout for the dialog
        self.setLayout(layout)