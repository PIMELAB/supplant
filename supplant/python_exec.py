import subprocess
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyQt5.QtCore import Qt, QRunnable, pyqtSignal, pyqtSlot, QObject, QThread


class Worker(QObject):
    """ Worker thread
    """
    finished = pyqtSignal()
    stoped = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(self, case):
        super(Worker, self).__init__()
        self.case = case
        self.f = open(f'{self.case}/output.txt', 'w')

        #subprocess.call(["/home/myuser/run.sh", "/tmp/ad_xml", "/tmp/video_xml"], stdout=f)

    @pyqtSlot()
    def run(self):
        self.run = subprocess.Popen(['python', f'{self.case}/main.py'], stdout=self.f)
        self.finished.emit()

    @pyqtSlot()
    def stop(self):
        self.stoped_solver.emit()