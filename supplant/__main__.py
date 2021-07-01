from PyQt5.QtWidgets import QApplication
import sys

#from . import gui
import gui

app = QApplication(sys.argv)
GUI = gui.MainWindow()
GUI.show()
sys.exit(app.exec_())
