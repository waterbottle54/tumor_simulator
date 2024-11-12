from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from Strings import about_text

class AboutDialog(QDialog):
    """
    어플리케이션 정보를 보여주는 간단한 대화상자 
    A simple dialog that displays App information such as...
    
    - 어플리케이션 이름과 버젼(Application name and version)
    - 어플리케이션의 개발 목적(The purpose of the aplication)
    - 주의사항과 면책공고(The cautions and disclaimer)
    - 저작권과 개발자 연락처(The copyright and contact information of the developer)
    """

    # Copyright (c) 2023 Sung Won Jo
    # For more details: https://github.com/waterbottle54/tumor_simulator

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
        label = QLabel(about_text)
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
