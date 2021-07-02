import subprocess
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


def run_case(solver, case):
    print('Running blockMesh')
    block_run = BasicRunner(argv=['blockMesh', '-case', case], silent=True)
    block_run.start()
    print(f'Running {solver}')
    solver_run = BasicRunner(argv=[solver, '-case', case], silent=True)
    solver_run.start()

def get_solver(file):
    parsed = ParsedParameterFile(file)
    return parsed['application']

