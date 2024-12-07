from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QDesktopServices
from Strings import about_text
from Strings import url_youtube
from Strings import get_image_path, url_github

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

        layout_dialog = QHBoxLayout()
        layout_dialog.setContentsMargins(32, 32, 32, 32)
        self.setLayout(layout_dialog)

        # add left layout in the dialog layout
        layout_left = QVBoxLayout()
        layout_left.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_dialog.addLayout(layout_left)

        layout_dialog.addSpacing(64)

        # add about image in the dialog layout
        image_about = QLabel()
        image_about.setPixmap(QPixmap(get_image_path('render.png')))
        image_about.setContentsMargins(16, 16, 16, 16)
        layout_dialog.addWidget(image_about)

        # add About text in the left layout
        label_about = QLabel(about_text)
        layout_left.addWidget(label_about)

        # add Youtube label in the left layout
        layout_youtube = QHBoxLayout()
        layout_youtube.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_left.addLayout(layout_youtube)

        # add Github label in the left layout
        layout_github = QHBoxLayout()
        layout_github.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout_left.addLayout(layout_github)

        # set Youtube icon
        label_youtube_icon = QLabel(self)
        layout_youtube.addWidget(label_youtube_icon)

        pixmap_youtube = QPixmap(get_image_path('youtube.png')).scaled(24, 24)
        label_youtube_icon.setPixmap(pixmap_youtube)
        label_youtube_icon.setFixedSize(24, 24)

        button_youtube_url = QPushButton(url_youtube)
        button_youtube_url.setStyleSheet("QPushButton {"
                              "    border: none;"
                             "    color: #0000EE;"  # Blue color
                             "    text-decoration: underline;"
                             "    padding: 0px;"
                             "    background-color: transparent;"
                             "}")
        button_youtube_url.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url_youtube)))
        layout_youtube.addWidget(button_youtube_url)

         # set Githun icon
        
        label_github_icon = QLabel(self)
        pixmap_github = QPixmap(get_image_path('github.png')).scaled(24, 24)
        label_github_icon.setPixmap(pixmap_github)
        label_github_icon.setFixedSize(24, 24)
        layout_github.addWidget(label_github_icon)

        button_github_url = QPushButton(url_github)
        button_github_url.setStyleSheet("QPushButton {"
                              "    border: none;"
                             "    color: #0000EE;"  # Blue color
                             "    text-decoration: underline;"
                             "    padding: 0px;"
                             "    background-color: transparent;"
                             "}")
        button_github_url.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url_github)))
        layout_github.addWidget(button_github_url)
