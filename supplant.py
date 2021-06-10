import glob
import os


class Configuration:
    def __init__(self, skeleton):
        self.skeleton = skeleton
        self.files = []
        self.folders = []
        self.read_files(self.skeleton)
        self.constants = {}
        self.variables = {}

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

    def replace_words(self, string, words):
        for key, value in words.items():
            string = string.replace(key, str(value))
        return string

    def write_case_files(self, id_):
        case_name = f'case_{id_}'
        for folder in self.folders:
            new_folder = folder.replace(self.skeleton, case_name)
            os.makedirs(new_folder, exist_ok=True)

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

        if len(self.variables) == 1:
            for i in self.variables[var_names[0]]:
                self.constants[var_names[0]] = i
                self.write_case_files(id_)
                id_ += 1

        elif len(self.variables) == 2:
            for i in self.variables[var_names[0]]:
                for j in self.variables[var_names[1]]:
                    self.constants[var_names[0]] = i
                    self.constants[var_names[1]] = j
                    self.write_case_files(id_)
                    id_ += 1

        elif len(self.variables) == 3:
            for i in self.variables[var_names[0]]:
                for j in self.variables[var_names[1]]:
                    for k in self.variables[var_names[2]]:
                        self.constants[var_names[0]] = i
                        self.constants[var_names[1]] = j
                        self.constants[var_names[2]] = k
                        self.write_case_files(id_)
                        id_ += 1
        else:
            print('Number of variables out of range')
