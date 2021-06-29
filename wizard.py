import os.path
import sys
from PyQt5.QtWidgets import *#QApplication, QGridLayout, QPushButton, QToolButton, QWidget, QLineEdit, QLabel, QComboBox, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy

import supplant


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Layouts and main structure definition
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.main_layout = QHBoxLayout(self.widget)
        #self.layout = QVBoxLayout(self.widget)#QGridLayout(self.widget)
        self.layout = QVBoxLayout()
        self.layout_preview = QVBoxLayout()
        self.frame = QFrame()
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.resize(300, 300)
        self.layout_preview.addWidget(self.frame)
        self.main_layout.addLayout(self.layout)
        self.main_layout.addLayout(self.layout_preview)
        self.layout_preview.addWidget(QPushButton('Run'))
        self.setWindowTitle('Configuration Wizard')
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Declaring variables
        self.groupBoxes = {}
        self.layoutBoxes = {}
        self.content = []
        self.filenames = []
        self.labels = []
        self.units = []
        self.comboBoxes = []
        self.lineEdits = []
        self.dependentBoxes = []

        # Menu bar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        #self.menubar.setGeometry(QRect(0, 0, 968, 30))

        ## File
        self.menuFile = QMenu('&File')
        self.actionOpen = QAction('&Open', self.menuFile)
        self.actionSave = QAction('&Save', self.menuFile)
        self.actionExit = QAction('&Exit', self.menuFile)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        ## Help
        self.menuHelp = QMenu('&Help')
        self.actionAbout = QAction('&About', self.menuHelp)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuHelp.menuAction())

        # Status bar
        self.statusbar = QStatusBar(self)
        #self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('Working!')

        # Settings Box
        self.settings_box = QGroupBox('Settings')
        self.settings_box.setAlignment(4)
        self.layout_settings = QGridLayout()
        self.settings_box.setLayout(self.layout_settings)
        self.layout_settings.addWidget(QLabel('Skeleton Folder'), 0, 0)
        self.skeleton_folder = QLineEdit()
        self.skeleton_path = ''
        self.toolButton_browse_skeleton = QToolButton(text='...')
        self.layout_settings.addWidget(self.skeleton_folder, 0, 1)
        self.layout_settings.addWidget(self.toolButton_browse_skeleton, 0, 2)

        self.combo_box_doe = QComboBox()
        self.combo_box_doe.addItem('Full Factorial')
        self.layout_settings.addWidget(QLabel('DOE'), 1, 0)
        self.layout_settings.addWidget(self.combo_box_doe)

        self.options = ['constant', 'variable', 'dependent']

        self.layout.addLayout(self.layout_settings)

        # Connections
        self.toolButton_browse_skeleton.clicked.connect(self.open_folder)


        # Add group boxes to the vertical layout
        self.layout.addWidget(self.settings_box)

        self.button = QPushButton('Save configuration')
        self.button.clicked.connect(self.save_config)

        if len(sys.argv) > 1:
            self.skeleton_path = os.path.abspath(sys.argv[1])
            self.sim = supplant.Configuration(self.skeleton_path)
            self.skeleton_folder.setText(self.skeleton_path)
            self.load_case()
        else:
            self.open_folder()

        self.show()

    def open_folder(self):
        """ Open file dialog to choose a folder
        """
        foldername = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if foldername:
            self.skeleton_path = foldername
            self.skeleton_folder.setText(foldername)
            self.load_case()

    def load_case(self):
        self.sim = supplant.Configuration(self.skeleton_path)
        self.filenames, self.content = self.sim.check()
        self.content = list(dict.fromkeys(self.content))  # remove duplicates

        # Assign layout to group boxes
        for i in range(len(self.content)):
            group_name = self.content[i].split(',')[0]
            self.groupBoxes[group_name] = QGroupBox(group_name)
            self.groupBoxes[group_name].setAlignment(4)
            self.layoutBoxes[group_name] = QGridLayout()
            self.groupBoxes[group_name].setLayout(self.layoutBoxes[group_name])
            self.layoutBoxes[group_name].addWidget(QLabel('Type'), 0, 0)
            self.layoutBoxes[group_name].addWidget(QLabel('Variable'), 0, 1)
            self.layoutBoxes[group_name].addWidget(QLabel('Value'), 0, 2)
            self.layoutBoxes[group_name].addWidget(QLabel('Unit'), 0, 3)
            self.layoutBoxes[group_name].addWidget(QLabel('Depends'), 0, 4)
            self.layoutBoxes[group_name].addWidget(QHLine(), 1, 0, 1, 5)

        #self.options = ['constant', 'variable', 'dependent']
        self.labels = self.content.copy()
        self.units = self.content.copy()
        self.comboBoxes = self.content.copy()
        self.lineEdits = self.content.copy()
        self.dependentBoxes = self.content.copy()
        number = 0
        for row in range(len(self.content)):
            group_name, var_name, unit = self.content[row].split(',')
            self.labels[number] = QLabel(var_name)
            self.layoutBoxes[group_name].addWidget(self.labels[number], row + 2, 1)
            self.comboBoxes[number] = QComboBox()
            self.comboBoxes[number].addItems(self.options)
            self.comboBoxes[number].currentIndexChanged.connect(self.on_combobox_changed)
            self.units[number] = QLabel(unit)
            self.layoutBoxes[group_name].addWidget(self.units[number], row + 2, 3)
            self.dependentBoxes[number] = QComboBox()
            self.layoutBoxes[group_name].addWidget(self.comboBoxes[number], row + 2, 0)
            self.lineEdits[number] = QLineEdit()
            self.layoutBoxes[group_name].addWidget(self.lineEdits[number], row + 2, 2)
            number += 1

        for group in self.groupBoxes:
            self.layout.addWidget(self.groupBoxes[group])
            self.layout.addItem(self.verticalSpacer)

    def on_combobox_changed(self):
        """
        Populate the dependents comboBox
        """
        for row, combo in enumerate(self.comboBoxes):
            group_name = self.content[row].split(',')[0]
            if combo.currentIndex() == 2:
                self.dependentBoxes[row] = QComboBox()  # TODO: Make only an update to the box, not a new one
                self.layoutBoxes[group_name].addWidget(self.dependentBoxes[row], row+2, 4)
                for j, var in enumerate(self.comboBoxes):
                    if var.currentText() == 'variable':
                        self.dependentBoxes[row].addItem(self.labels[j].text())

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
