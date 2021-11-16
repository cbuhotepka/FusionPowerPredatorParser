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
            if type(value) is list and len(value) > 0 and type(value[0]) is dict:
                for list_item in value:
                    yield self._get_dict_data(list_item)

    def _get_list_data(self, key, ls: list) -> list:
        """Генератор tuple из списка"""
        result = []
        for item in ls:
            if type(item) is str:
                result.append(tuple([key, item]))
            if type(item) is dict:
                result.extend(self._get_dict_data(item))
            elif type(item) is list:
                result.extend(self._get_list_data(key, item))
        return result

    def _get_dict_data(self, dc: dict) -> list:
        """получение значений словаря"""
        result = []
        for key, value in dc.items():
            if type(value) is str or type(value) is int:
                result.append(tuple([key, value]))
            elif type(value) is dict:
                result.extend(self._get_dict_data(value))
            elif type(value) is list:
                result.extend(self._get_list_data(key, value))
        return result

    def write_to_file(self):
        pass

    def get_string(self) -> str:
        """Генерация строки"""
        pass

    def run(self):
        self._read_json_file()
        result = [ item for item in self._walk_to_json_data()]
        print(result)

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