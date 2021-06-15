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

        self.sim = supplant.Configuration(sys.argv[1])
        self.filenames, self.content = self.sim.check()
        self.content = list(dict.fromkeys(self.content)) # remove duplicates
        self.options = ['constant', 'variable', 'dependent']
        self.labels = self.content.copy()
        self.comboBoxes = self.content.copy()
        self.lineEdits = self.content.copy()
        self.dependentBoxes = self.content.copy()
        number = 0
        for i in range(len(self.content)):
            self.labels[number] = QLabel(self.content[i])
            self.layout.addWidget(self.labels[number], i, 0)
            self.comboBoxes[number] = QComboBox()
            self.comboBoxes[number].addItems(self.options)
            self.comboBoxes[number].currentIndexChanged.connect(self.on_combobox_changed)
            # TODO: Create comboBox with labels as options when selecting 'dependent' option
            self.layout.addWidget(self.comboBoxes[number], i, 1)
            self.lineEdits[number] = QLineEdit()
            self.layout.addWidget(self.lineEdits[number], i, 2)
            number += 1

        self.button = QPushButton('Save configuration')
        self.button.clicked.connect(self.save_config)
        self.layout.addWidget(self.button, len(self.content)+1, 0)

        self.show()

    def on_combobox_changed(self):
        for i, combo in enumerate(self.comboBoxes):
            if combo.currentIndex() == 2:
                if type(self.dependentBoxes[i]) == QComboBox:
                    pass
                else:
                    self.dependentBoxes[i] = QComboBox()
                    self.dependentBoxes[i].addItems(self.content)
                    self.layout.addWidget(self.dependentBoxes[i], i, 3)

    def save_config(self):
        print('Saving configuration')
        skeleton = sys.argv[1]
        with open('custom.py', 'w') as f:
            f.write('import supplant' + '\n')
            f.write('\n')
            f.write(f'sim = supplant.Configuration(\'{skeleton}\')' + '\n')
            for i, combo in enumerate(self.comboBoxes):
                if combo.currentText() == self.options[0]:
                    f.write(f'sim.add_constant(\'{self.labels[i].text()}\', \'{self.lineEdits[i].text()}\')' + '\n')
                elif combo.currentText() == self.options[1]:
                    list_string = str(self.lineEdits[i].text()).split()
                    list_string = [str(i) for i in list_string]
                    f.write(f'sim.add_variable(\'{self.labels[i].text()}\', {list_string})' + '\n')
                elif combo.currentText() == self.options[2]:
                    list_string = str(self.lineEdits[i].text()).split()
                    list_string = [str(i) for i in list_string]
                    f.write(f'sim.add_dependent(\'{self.labels[i].text()}\', {list_string}, \'{self.dependentBoxes[i].currentText()}\')' + '\n')
            f.write('sim.write_configurations()' + '\n')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    GUI = MainWindow()
    GUI.show()
    sys.exit(app.exec_())
