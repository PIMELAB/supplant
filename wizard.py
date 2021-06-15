import sys
from PyQt5.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget, QLineEdit, QLabel, QComboBox, QMainWindow

import supplant


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.layout = QGridLayout(self.widget)
        self.setWindowTitle('Configuration Wizard')

        self.sim = supplant.Configuration('test_folder')
        self.filenames, self.content = self.sim.check()

        self.options = ['constant', 'variable', 'dependent']
        self.labels = self.content.copy()
        self.comboBoxes = self.content.copy()
        self.lineEdits = self.content.copy()
        number = 0
        for i in range(len(self.filenames)):
            self.labels[number] = QLabel(self.content[i])
            self.layout.addWidget(self.labels[number], i, 0)
            self.comboBoxes[number] = QComboBox()
            self.comboBoxes[number].addItems(self.options)
            # TODO: Create comboBox with labels as options when selecting 'dependent' option
            self.layout.addWidget(self.comboBoxes[number], i, 1)
            self.lineEdits[number] = QLineEdit()
            self.layout.addWidget(self.lineEdits[number], i, 2)
            number += 1

        self.button = QPushButton('Save configuration')
        self.button.clicked.connect(self.save_config)
        self.layout.addWidget(self.button, len(self.filenames)+1, 2)

        self.show()

    def save_config(self):
        print('Saving configuration')
        with open('custom.py', 'w') as f:
            f.write('import supplant' + '\n')
            f.write('\n')
            f.write('sim = supplant.Configuration()' + '\n')
            for i, combo in enumerate(self.comboBoxes):
                if combo.currentText() == self.options[0]:
                    f.write(f'sim.add_constant(\'{self.labels[i].text()}\', {self.lineEdits[i].text()})' + '\n')
                elif combo.currentText() == self.options[1]:
                    f.write(f'sim.add_variable(\'{self.labels[i].text()}\', [{self.lineEdits[i].text()}])' + '\n')
                elif combo.currentText() == self.options[2]:
                    f.write(f'sim.add_dependent(\'{self.labels[i].text()}\', [{self.lineEdits[i].text()}], \'__TODO__\')' + '\n')
            f.write('sim.write_configurations()' + '\n')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec_())
