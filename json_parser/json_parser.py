import os
import json
import shutil
from typing import Counter


class ConvertorJSON:
    """Конвертор JSON"""

    def __init__(self, file):
        self.json_file = file
        self.json_data = None

    def _read_json_file(self):
        """Чтение JSON файла"""
        with open(self.json_file, 'r', encoding='utf-8') as json_file:
            self.json_data = json.load(json_file)

    def _walk_to_json_data(self) -> list:
        """проход по структуре JSON"""
        for key, value in self.json_data.items():
            result = []
            if type(value) is str:
                result.append(tuple([key, value]))
            elif type(value) is list:
                for item in self._get_list_data(key, value):
                    result.append(item)
            elif type(value) is dict:
                for item in self._get_dict_data(value):
                    result.append(item)
            yield result

    def _get_list_data(self, key, ls: list) -> tuple:
        """Генератор tuple из списка"""
        for item in ls:
            if type(item) is dict:
                for res in self._get_dict_data(item):
                    yield res
            elif type(item) is list:
                for res in self._get_list_data(key, item):
                    yield res
            else:
                yield tuple([key, item])

    def _get_dict_data(self, dc: dict) -> tuple:
        """получение значений словаря"""
        for key, value in dc.items():
            if type(value) is dict:
                for res in self._get_dict_data(value):
                    yield res
            elif type(value) is list:
                for res in self._get_list_data(key, value):
                    yield res
            else:
                yield tuple([key, value])

    def write_to_file(self):
        pass

    def get_string(self) -> str:
        """Генерация строки"""
        pass

    def run(self):
        self._read_json_file()

#
# def parse_users(path, site_name, readme_path):
#     print('-' * 5, path, '-' * 5)
#     with open(path, 'r', encoding='utf-8') as json_file:
#         data = json_file.read()
#
#     res = json.loads(data)
#
#     try:
#         os.mkdir(site_name)
#     except FileExistsError:
#         pass
#
#     with open(os.path.join(site_name, 'users.txt'), 'w', encoding='utf-8') as res_f:
#
#
#
#
if __name__ == '__main__':
    conv = ConvertorJSON('tests\\test_file.json')
    conv.run()