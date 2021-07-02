import subprocess
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyQt5.QtCore import Qt, QRunnable, pyqtSignal, pyqtSlot, QObject, QThread


class Worker(QObject):
    """ Worker thread
    """
    finished = pyqtSignal()
    finished_mesh = pyqtSignal()
    finished_solver = pyqtSignal()
    stoped_mesh = pyqtSignal()
    stoped_solver = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(self, solver, case):
        super(Worker, self).__init__()
        self.solver = solver
        self.case = case
        self.block_run = BasicRunner(argv=['blockMesh', '-case', self.case], silent=True)
        self.solver_run = BasicRunner(argv=[self.solver, '-case', self.case], silent=True)

    @pyqtSlot()
    def run_mesh(self):
        print('Running blockMesh NEW')
        # block_run = BasicRunner(argv=['blockMesh', '-case', self.case], silent=True)
        self.block_run.start()
        self.finished_mesh.emit()

    @pyqtSlot()
    def run_solver(self):
        print(f'Running {self.solver} NEW')
        # solver_run = BasicRunner(argv=[self.solver, '-case', self.case], silent=True)
        self.solver_run.start()
        self.finished_solver.emit()

    @pyqtSlot()
    def run(self):
        self.run_mesh()
        self.run_solver()
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self.block_run.stopGracefully()
        self.stoped_mesh.emit()
        self.solver_run.stopGracefully()
        self.stoped_solver.emit()


def get_solver(file):
    parsed = ParsedParameterFile(file)
    return parsed['application']