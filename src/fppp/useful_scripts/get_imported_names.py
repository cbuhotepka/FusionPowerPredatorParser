import os

from folder_parser.directory_class import Directory
from folder_parser.store import BASE_TYPES

ROOT_PATH = 'Z:/'
DIRS_FILE = 'C:/move.txt'


class NamesGetter:
    def __init__(self, user_number: int):
        self.user_number = f'blitz{user_number}'
        self.path_imported = os.path.join(ROOT_PATH, self.user_number, 'Imported')

    def run(self):
        self.iterate_dirs()

    def iterate_dirs(self):
        for base_type in BASE_TYPES:
            for folder in self._get_dirs(base_type):
                directory = Directory(path=folder, base_type=base_type)
                print(f"'{directory.base_info['name']}',")

    def _get_dirs(self, base_type: str) -> str:
        path = os.path.join(self.path_imported, base_type)
        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):
                yield str(os.path.join(path, item))


if __name__ == '__main__':
    user_number = input('Enter user number: ')
    getter = NamesGetter(int(user_number))
    getter.run()
