from PyQt5.QtWidgets import QApplication
import sys

import supplant.gui as gui

app = QApplication(sys.argv)
GUI = gui.MainWindow()
GUI.show()
sys.exit(app.exec_())
