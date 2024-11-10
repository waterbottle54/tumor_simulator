from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About")
        self.setStyleSheet("background-color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)

        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addLayout(left_layout)

        # About Text
        text = """
Brain Tumor Simulator 1.0


Purpose: Tumor volume measurement, comparison, and analysis

Disclaimer: This software is not intended to replace professional medical diagnosis.

Copyright 2023. Sung Won Jo. All rights reserved.


Contact: waterbottle54@naver.com
        """
        label = QLabel(text)
        left_layout.addWidget(label)

        # YouTube icon
        youtube_layout = QHBoxLayout()
        left_layout.addLayout(youtube_layout)

        youtube_icon = QLabel(self)
        youtube_pixmap = QPixmap("icons/youtube.png").scaled(24, 24)
        youtube_icon.setPixmap(youtube_pixmap)
        youtube_icon.setFixedSize(24, 24)
        youtube_layout.addWidget(youtube_icon)

        youtube_url = 'https://www.youtube.com/channel/UChfv3TOHGociOKYMXSzS6hw'
        youtube_button = QPushButton(youtube_url)
        youtube_button.setStyleSheet("QPushButton {"
                              "    border: none;"
                             "    color: #0000EE;"  # Blue color
                             "    text-decoration: underline;"
                             "    padding: 0px;"
                             "    background-color: transparent;"
                             "}")
        youtube_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(youtube_url)))
        youtube_layout.addWidget(youtube_button)

        layout.addSpacing(64)

        # app icon
        image = QLabel()
        image.setPixmap(QPixmap('icons/render.png'))
        image.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(image)

        # Set the layout for the dialog
        self.setLayout(layout)
