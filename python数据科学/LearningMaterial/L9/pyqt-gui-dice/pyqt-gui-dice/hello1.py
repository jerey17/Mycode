import sys

# Based on code from https://www.pythonguis.com/

# Import necessary libraries.
# Qt6 is current, but Qt5 is in Anaconda and mostly API-compatible.
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

# Qt provides QMainWindow to represent the main window of your application.
# Subclass it to create your own application.
class MainWindow(QMainWindow):
    # The constructor gets run when the class is instantiated.
    def __init__(self):
        super().__init__()
        # Set the window title.
        self.setWindowTitle("Hello")

        # Create a label widget.
        x = QLabel("World")
        self.setCentralWidget(x)

# Instantiate the main window.
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
