<<<<<<< HEAD

=======
>>>>>>> 8fcab17a001e8d8da21e572b3094a84a4c8dfe35
import sys
from PyQt5.QtWidgets import QApplication
from ui.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
