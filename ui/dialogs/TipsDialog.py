from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap

class TipsDialog(QDialog):
    """_summary_

    Att:
        QDialog (_type_): _description_
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Tips")
        self.setStyleSheet("background-color: white;")

        # Create a QVBoxLayout to hold the content
        layout = QHBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)

        # Create a QLabel to display the application information
        text = """
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

        label = QLabel(text)
        layout.addWidget(label)

        layout.addSpacing(64)

        image = QLabel()
        image.setPixmap(QPixmap('icons/tips.png'))
        image.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(image)

        # Set the layout for the dialog
        self.setLayout(layout)