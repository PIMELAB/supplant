import glob
import os


class Configuration:
    def __init__(self, skeleton):
        if skeleton[-1] == '/':
            self.skeleton = skeleton[:-1]
        else:
            self.skeleton = skeleton
        self.files = []
        self.folders = []
        self.read_files(self.skeleton)
        self.constants = {}
        self.variables = {}
        self.dependents = {}
        self.relations = {}
        self.counters = {}

    def read_files(self, skeleton):
        all_files = glob.glob(f'{skeleton}/**', recursive=True)
        for file_ in all_files:
            if os.path.isfile(file_):
                self.files.append(file_)
            else:
                self.folders.append(file_)

    def add_constant(self, key, value):
        self.constants[key] = value

    def add_variable(self, key, values):
        self.variables[key] = values

    def add_dependent(self, key, value, parent):
        self.dependents[key] = value
        self.relations[key] = parent

    def add_counter(self, key):
        self.counters[key] = True
        self.constants[key] = 0

    def replace_words(self, string, words):
        for key, value in words.items():
            string = string.replace(key, str(value))
        return string

    def check(self, pattern='__'):
        content = []
        filenames = []
        for file_ in self.files:
            with open(file_, 'r') as f:
                for line in f:
                    splitted = line.split('__')
                    if len(splitted) > 1:
                        content.append(splitted[1])
                        filenames.append(file_)
        return filenames, content

    def write_case_files(self, id_):
        case_name = f'case_{id_}'
        for folder in self.folders:
            new_folder = folder.replace(self.skeleton, case_name)
            os.makedirs(new_folder, exist_ok=True)

        for key, value in self.counters.items():
            self.constants[key] = id_

        for file_ in self.files:
            content = open(file_, 'r').read()
            content = self.replace_words(content, self.constants)
            new_file = file_.replace(self.skeleton, case_name)
            with open(new_file, 'w') as f:
                f.write(content)

    def write_configurations(self):
        id_ = 0
        var_names = []

        for key, value in self.variables.items():
            var_names.append(key)

        if len(self.variables) == 0:
            self.write_case_files(0)

        elif len(self.variables) == 1:
            for count_i, i  in enumerate(self.variables[var_names[0]]):
                print(i, var_names[0])
                self.constants[var_names[0]] = i
                for dep_key, dep_value in self.dependents.items():
                    if self.relations[dep_key] == var_names[0]:
                        self.constants[dep_key] = dep_value[count_i]
                    else:
                        print(f'Wrong parent {self.relations[dep_key]}')
                self.write_case_files(id_)
                id_ += 1

        elif len(self.variables) == 2:
            for count_i, i in enumerate(self.variables[var_names[0]]):
                for count_j, j in enumerate(self.variables[var_names[1]]):
                    self.constants[var_names[0]] = i
                    self.constants[var_names[1]] = j
                    for dep_key, dep_value in self.dependents.items():
                        if self.relations[dep_key] == var_names[0]:
                            self.constants[dep_key] = dep_value[count_i]
                        elif self.relations[dep_key] == var_names[1]:
                            self.constants[dep_key] = dep_value[count_j]
                        else:
                            print(f'Wrong parent: {self.relations[dep_key]}')
                    self.write_case_files(id_)
                    id_ += 1

        elif len(self.variables) == 3:
            for count_i, i in enumerate(self.variables[var_names[0]]):
                for count_j, j in enumerate(self.variables[var_names[1]]):
                    for count_k, k in enumerate(self.variables[var_names[2]]):
                        self.constants[var_names[0]] = i
                        self.constants[var_names[1]] = j
                        self.constants[var_names[2]] = k
                        for dep_key, dep_value in self.dependents.items():
                            if self.relations[dep_key] == var_names[0]:
                                self.constants[dep_key] = dep_value[count_i]
                            elif self.relations[dep_key] == var_names[1]:
                                self.constants[dep_key] = dep_value[count_j]
                            elif self.relations[dep_key] == var_names[2]:
                                self.constants[dep_key] = dep_value[count_k]
                            else:
                                print(f'Wrong parent: {self.relations[dep_key]}')
                        self.write_case_files(id_)
                        id_ += 1
        else:
            print('Number of variables out of range')
