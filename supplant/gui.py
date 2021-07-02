import os.path
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QCursor, QColor
from PyQt5.QtCore import Qt, QRunnable, pyqtSignal, pyqtSlot, QObject, QThread
from multiprocessing import Pool
import subprocess
import time
from . import doe
from . import openfoam



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
        self.setWindowTitle('Configuration Wizard')
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        ## Left panel
        self.layout_left = QVBoxLayout()


        ## Right panel
        self.layout_right = QVBoxLayout()
        self.tabWidget = QTabWidget()
        self.tab_doe = QWidget()
        self.tabWidget.addTab(self.tab_doe, 'DOE')
        self.table_doe = QTableWidget()
        self.table_doe.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_doe.customContextMenuRequested.connect(self.table_doe_context_menu)
        #self.table_doe.verticalHeader().setVisible(False)
        self.layout_doe = QGridLayout()
        self.tab_doe.setLayout(self.layout_doe)
        self.layout_doe.addWidget(self.table_doe)
        self.layout_right.addWidget(self.tabWidget)
        self.pushButton_preview = QPushButton('Preview')
        self.pushButton_preview.clicked.connect(self.bake_cases)
        self.layout_right.addWidget(self.pushButton_preview)


        self.main_layout.addLayout(self.layout_left)
        self.main_layout.addLayout(self.layout_right)

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
        self.options = ['constant', 'variable', 'dependent']
        self.table_rows = []
        self.of_solver = ''
        self.running_threads = {}
        self.running_workers = {}

        # Menu bar
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        ## File
        self.menuFile = QMenu('&File')
        self.actionOpen = QAction('&Open', self.menuFile)
        self.actionOpen.setIcon(QIcon.fromTheme('document-open'))
        self.actionSave = QAction('&Save', self.menuFile)
        self.actionSave.setIcon(QIcon.fromTheme('document-save'))
        self.actionSaveAs = QAction('S&ave As', self.menuFile)
        self.actionSaveAs.setIcon(QIcon.fromTheme('document-save-as'))
        self.actionExit = QAction('&Exit', self.menuFile)
        self.actionExit.setIcon(QIcon.fromTheme('application-exit'))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        ## Help
        self.menuHelp = QMenu('&Help')
        self.actionAbout = QAction('&About', self.menuHelp)
        self.actionAbout.setIcon(QIcon.fromTheme('help-about'))
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuHelp.menuAction())

        # Status bar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('Working!')

        # Settings Box
        self.settings_box = QGroupBox('Settings')
        self.settings_box.setAlignment(4)
        self.settings_box.setMaximumWidth(400)
        self.layout_settings = QGridLayout()
        self.settings_box.setLayout(self.layout_settings)
        self.layout_settings.addWidget(QLabel('Skeleton Folder'), 0, 0)
        self.skeleton_folder = QLineEdit()
        self.skeleton_path = ''
        self.toolButton_browse_skeleton = QToolButton(text='...')
        self.toolButton_browse_skeleton.clicked.connect(self.open_folder)
        self.layout_settings.addWidget(self.skeleton_folder, 0, 1)
        self.layout_settings.addWidget(self.toolButton_browse_skeleton, 0, 2)
        self.combo_box_doe = QComboBox()
        self.combo_box_doe.addItem('Full Factorial')
        self.layout_settings.addWidget(QLabel('DOE'), 1, 0)
        self.layout_settings.addWidget(self.combo_box_doe)
        self.layout_left.addLayout(self.layout_settings)
        self.layout_left.addWidget(self.settings_box)

        self.button = QPushButton('Save configuration')
        self.button.clicked.connect(self.save_config)

        if len(sys.argv) > 1:
            self.skeleton_path = os.path.abspath(sys.argv[1])
            self.sim = doe.Configuration(self.skeleton_path)
            self.skeleton_folder.setText(self.skeleton_path)
            self.load_case()
            self.populate_doe()
        else:
            self.open_folder()

    def open_folder(self):
        """ Open file dialog to choose a folder
        """
        foldername = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if foldername:
            self.skeleton_path = foldername
            self.skeleton_folder.setText(foldername)
            self.load_case()
            self.populate_doe()

    def load_case(self):
        """
        Load case using supplant API (doe) and create selection boxes
        """
        self.sim = doe.Configuration(self.skeleton_path)
        self.filenames, self.content = self.sim.check()
        self.content = list(dict.fromkeys(self.content))  # remove duplicates
        self.check_software()

    def check_software(self):
        for file in self.sim.files:
            if file.find('controlDict') >= 0:
                self.of_solver = openfoam.get_solver(file)

    def populate_doe(self):
        # Assign layout to group boxes
        for i in range(len(self.content)):
            if len(self.content[i].split(',')) == 3:
                group_name = self.content[i].split(',')[0]
            else:
                group_name = self.filenames[i].split('/')
                group_name = '/'.join(group_name[-3:])
            self.groupBoxes[group_name] = QGroupBox(group_name)
            self.groupBoxes[group_name].setAlignment(4)
            self.groupBoxes[group_name].setMaximumWidth(400)
            self.layoutBoxes[group_name] = QGridLayout()
            self.groupBoxes[group_name].setLayout(self.layoutBoxes[group_name])
            self.layoutBoxes[group_name].addWidget(QLabel('Type'), 0, 0)
            self.layoutBoxes[group_name].addWidget(QLabel('Variable'), 0, 1)
            self.layoutBoxes[group_name].addWidget(QLabel('Value'), 0, 2)
            self.layoutBoxes[group_name].addWidget(QLabel('Unit'), 0, 3)
            self.layoutBoxes[group_name].addWidget(QLabel('Depends'), 0, 4)
            self.layoutBoxes[group_name].addWidget(QHLine(), 1, 0, 1, 5)

        self.labels = self.content.copy()
        self.units = self.content.copy()
        self.comboBoxes = self.content.copy()
        self.lineEdits = self.content.copy()
        self.dependentBoxes = self.content.copy()

        # Add items to group boxes
        number = 0
        for row in range(len(self.content)):
            if len(self.content[row].split(',')) == 3:
                group_name, var_name, unit = self.content[row].split(',')
            else:
                group_name = self.filenames[row].split('/')
                group_name = '/'.join(group_name[-3:])
                var_name = self.content[row]
                unit = '-'
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

        # Add group boxes to the vertical layout
        for group in self.groupBoxes:
            self.layout_left.addItem(self.verticalSpacer)
            self.layout_left.addWidget(self.groupBoxes[group])

    def bake_cases(self):
        self.load_case()
        for index, value in enumerate(self.comboBoxes):
            var_type = value.currentText()
            var_name = self.content[index]
            var_value = self.lineEdits[index].text()
            var_depends = self.dependentBoxes[index].currentText()
            if var_type == self.options[0]: # constant
                self.sim.add_constant(var_name, var_value)
            elif var_type == self.options[1]: # variable
                self.sim.add_variable(var_name, var_value.split(','))
            elif var_type == self.options[2]: # dependent
                for deps in self.content:
                    if var_depends in deps:
                        self.sim.add_dependent(var_name, var_value.split(','), deps)
        self.table_rows = self.sim.write_configurations()
        self.preview_table()

    def preview_table(self):
        col_size = len(self.table_rows[0])+1
        row_size = len(self.table_rows)
        # Empty all columns and rows before creating a new one
        while self.table_doe.rowCount() > 0:
            self.table_doe.removeRow(0)
        while self.table_doe.columnCount() > 0:
            self.table_doe.removeColumn(0)
        labels = list(self.sim.constants.keys())
        if ',' in labels[0]:
            labels = [x.split(',')[1] for x in labels]
        cases = [f'case_{x}' for x in range(row_size)]
        # Create empty columns
        for col in range(col_size):
            self.table_doe.insertColumn(col)
        # Create empty rows
        for row in range(row_size):
            self.table_doe.insertRow(row)
        # Populate cells
        for row in range(row_size):
            self.table_doe.setItem(row, 0, QTableWidgetItem('Ready'))
            self.table_doe.item(row, 0).setBackground(QColor(Qt.lightGray))
            for col in range(col_size-1):
                self.table_doe.setItem(row, col+1, QTableWidgetItem(self.table_rows[row][col]))
        # Set initial status
        labels.insert(0, 'Status     ')
        self.table_doe.setHorizontalHeaderLabels(labels)
        self.table_doe.setVerticalHeaderLabels(cases)
        self.table_doe.resizeColumnsToContents()
        self.table_doe.resize

    def on_combobox_changed(self):
        """
        Populate the dependents comboBox
        """
        for row, combo in enumerate(self.comboBoxes):
            group_name = self.content[row].split(',')[0].strip(' ')
            if combo.currentIndex() == 2:
                self.dependentBoxes[row] = QComboBox()  # TODO: Make only an update to the box, not a new one
                self.layoutBoxes[group_name].addWidget(self.dependentBoxes[row], row+2, 4)
                for j, var in enumerate(self.comboBoxes):
                    if var.currentText() == 'variable':
                        self.dependentBoxes[row].addItem(self.labels[j].text().strip(' '))

    def table_doe_context_menu(self, event):
        """
        Add right mouse click options to the GUI
        """
        row = self.table_doe.rowAt(event.y())
        # ignore menu if no row is selected
        if row == -1:
            return

        case = self.table_doe.verticalHeaderItem(row).text()
        table_menu = QMenu(self)
        case_label = QAction(case)
        case_label.setDisabled(True)
        run_action = QAction('Run', self)
        stop_action = QAction('Stop', self)
        preview_action = QAction('Preview', self)
        #results_action = QAction('Results', self)
        table_menu.addAction(case_label)
        table_menu.addSeparator()
        table_menu.addAction(run_action)
        table_menu.addAction(stop_action)
        table_menu.addAction(preview_action)
        #table_menu.addAction(results_action)
        table_menu.popup(QCursor.pos())
        action = table_menu.exec_(self.table_doe.mapToGlobal(event))

        if action == run_action:
            if case in self.running_threads.keys():
                print(f'{case} already exists')
            else:
                print(f"Running case {row}")
                self.table_doe.item(row, 0).setText('Running')
                self.table_doe.item(row, 0).setForeground(QColor(Qt.darkYellow))
                self.running_threads[case] = QThread()
                self.running_workers[case] = openfoam.Worker(self.of_solver, case)
                self.running_workers[case].moveToThread(self.running_threads[case])
                self.running_threads[case].started.connect(self.running_workers[case].run)
                self.running_threads[case].start()
                self.running_workers[case].finished.connect(lambda: self.thread_complete(row))
        elif action == stop_action:
            if case in self.running_threads.keys():
                if self.running_threads[case].isRunning():
                    print(f'Stopping {case}')
                    self.running_workers[case].stop()
                    self.running_threads[case].terminate()
                    self.table_doe.item(row, 0).setText('Stopped')
                    self.table_doe.item(row, 0).setForeground(QColor(Qt.darkRed))
            else:
                print(f"{case} is empty")

        elif action == preview_action:
            print(f"Preview of {case}")

    def thread_complete(self, row):
        self.table_doe.item(row, 0).setText('Finished')
        self.table_doe.item(row, 0).setForeground(QColor(Qt.darkGreen))
        #case = self.table_doe.verticalHeaderItem(row).text()
        print('FINISHED!!!')

    def save_config(self):
        print('Saving configuration')
        skeleton = sys.argv[1]
        with open('custom.py', 'w') as f:
            f.write('import doe' + '\n')
            f.write('\n')
            f.write(f'sim = doe.Configuration(\'{skeleton}\')' + '\n')
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
