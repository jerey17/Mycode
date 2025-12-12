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
        # Run the superclass initialisation code.
        super().__init__()

        # Set the window title.
        self.setWindowTitle("Hello")

        # Create a label widget.
        x = QLabel("World")

        # Set the label widget as the central widget of the Window.
        # (Widgets can also be docked around the edges.)
        self.setCentralWidget(x)

        # Text alignment can be set directly on the label.
        x.setAlignment(Qt.AlignCenter)

        # To change the font, we have to get a font object...        
        f = x.font()
        # ...modify the font...
        f.setPointSize(72)
        # ...then set it back on the label.
        x.setFont(f)

# Instantiate the Qt event loop class.
# Passing on command-line arguments lets the application process them, if you want.
# (You can just use an empty list.)
app = QApplication(sys.argv)

# Instantiate the main window.
window = MainWindow()
# Tell Qt we actually want to display it.
window.show()

window.setMinimumSize(640,480)

# Finally, start the event loop itself.
app.exec()

# The application will terminate when all main windows are closed.

