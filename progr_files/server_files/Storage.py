import pickle
import os
from os.path import join

current_dir = os.path.dirname(__file__)[:-12]


class Storage:
    def __init__(self, storage_dir=join(current_dir, 'DB'),
                 pack_len=1024):
        self.dict_dir = join(storage_dir, 'dict')
        self.data_dir = join(storage_dir, 'data')
        self.log_dir = join(storage_dir, 'app_log')
        self.pack_len = pack_len
        for directory in [self.data_dir, self.log_dir]:
            if not os.path.exists(directory):
                open(directory, 'w').close()
        self.dictionary = self._load_dict()
        if not os.stat(self.log_dir).st_size == 0:
            self._retrieve_data()

    def add(self, key, value):
        try:
            key, value = str(key), str(value)
        except ValueError:
            print('Incorrect type')
            return
        with open(self.data_dir, 'a') as file:
            start = file.tell()
            file.write(value)
            end = file.tell()
        self._add_log('add', key, (start, end - start))
        self.dictionary[key] = (start, end - start)

    def get(self, key):
        try:
            key = str(key)
        except ValueError:
            print('Incorrect key type')
            return
        if not self.contains_key(key):
            return 'KeyError'
        start, length = self.dictionary[key]
        with open(self.data_dir) as file:
            file.seek(start)
            return file.read(length)

    def contains_key(self, key):
        try:
            key = str(key)
        except ValueError:
            print('Incorrect key type')
            return
        return key in self.dictionary.keys()

    def remove_key(self, key):
        try:
            key = str(key)
        except ValueError:
            print('Incorrect key type')
            return
        self.dictionary.pop(key)
        self._add_log('rm', key)

    def commit(self):
        self._commit_dict()

    def close(self):
        self.commit()

    def _retrieve_data(self):
        with open(self.log_dir, 'r') as log:
            while True:
                command = log.readline()[:-1]
                if command == '':
                    break
                if 'rm' in command:
                    self.dictionary.pop(command.split(' ')[1])
                    continue
                key = command.split(' ')[1]
                position = log.readline()[:-1].split(';')
                self.dictionary[key] = (int(position[0]), int(position[1]))
        self._commit_dict()

    def _add_log(self, command: str, key: str, position=None):
        with open(self.log_dir, 'a') as log:
            if position is not None:
                log.write("{0} {1}\n{2};{3}\n".format(command, key, *position))
            else:
                log.write("{0} {1}\n".format(command, key))

    def _commit_dict(self):
        with open(self.dict_dir, 'wb') as file:
            pickle.dump(self.dictionary, file)
        open(self.log_dir, 'w').close()

    def _load_dict(self):
        if os.path.exists(self.dict_dir):
            with open(self.dict_dir, 'rb') as file:
                return pickle.load(file)
        return dict()

    def _defrag(self):
        with open(self.data_dir + '_new', 'w') as new_file:
            for key in self.dictionary.keys():
                start = new_file.tell()
                for package in self.get(key):
                    new_file.write(package)
                end = new_file.tell()
                self.dictionary[key] = (start, end - start)
        os.remove(self.data_dir)
        os.rename(self.data_dir + '_new', self.data_dir)
        self._commit_dict()
