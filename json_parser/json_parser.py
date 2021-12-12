import csv
import json
import os
import subprocess
from itertools import repeat
from pathlib import Path

import dpath.util

from engine_modul.interface import UserInterface


class ConvertorJSON:
    """Конвертор JSON"""

    def __init__(self, file):
        self.json_file = file
        self.json_data = None
        self.interface = UserInterface()
        self.sequence_keys = []
        self.handlers = {
            'list': self._get_list_data,
            'dict': self._get_dict_data,
            'str': lambda string, key: {key: string},
        }
        self.headers = set()

    def _read_json_file(self):
        """Чтение JSON файла"""
        with open(self.json_file, 'r', encoding='utf-8') as json_file:
            try:
                self.json_data = json.load(json_file)
            except json.decoder.JSONDecodeError as ex:
                self.interface.error(ex)

    def _print_json_data(self):
        printed_rows = 0
        self.interface.print_key_value_JSON(self.json_file, limit=15)

    def _get_user_input(self) -> str:
        """Запрос у пользователя режима парсинга JSON"""
        while True:
            answer = self.interface.ask_mode_parsing_JSON()
            if answer == 'p':
                return answer
            elif answer == 'o':
                subprocess.run(f'Emeditor "{self.json_file}"')
                self.interface.pause()
            else:
                return answer

    def _search_key_in_dict(self, key: str, dict_for_search: dict):
        """Поиск позиции введенного ключа"""
        if key in dict_for_search.keys():
            self.sequence_keys.append(key)
            return True
        else:
            for sub_key, value in dict_for_search.items():
                if type(value) == dict:
                    find_key = self._search_key_in_dict(key, value)
                    if find_key:
                        self.sequence_keys.append(sub_key)
                        return True
                    return False

    def _get_data_for_string_from_dict(self) -> list:
        """Генерация данных из словаря для формирования строк"""
        keys_string = '/' + '/'.join(self.sequence_keys)
        # keys_string = self.sequence_keys[0]
        type_data = self._get_type(dpath.util.get(self.json_data, keys_string))
        if type_data == 'dict':
            for key, value in dpath.util.get(self.json_data, keys_string).items():
                row = self.handlers[self._get_type(value)](value, key)
                yield row
        elif type_data == 'list':
            for item in dpath.util.get(self.json_data, keys_string):
                row = self.handlers[self._get_type(item)](item)
                yield row

    def _get_data_for_string_from_list(self):
        """Генерация данных из списка для формирования строк"""
        for item in self.json_data:
            yield self.handlers[self._get_type(item)](item, key='_')

    def _get_type(self, data: any) -> str:
        """Определяет тип данных"""
        if type(data) == dict:
            return 'dict'
        elif type(data) == list:
            return 'list'
        elif type(data) == str:
            return 'str'
        else:
            return 'error'

    def _get_list_data(self, ls: list, key='') -> dict:
        """Генератор tuple из списка"""
        result = dict()
        additional_number = 0
        for item in ls:
            additional_number += 1
            if type(item) is str:
                result[key + f'_{additional_number}'] = item
            if type(item) is dict:
                result.update(self._get_dict_data(item))
            elif type(item) is list:
                result.update(self._get_list_data(key=key, ls=item))
        return result

    def _get_dict_data(self, dc: dict, key=None) -> dict:
        """получение значений словаря"""
        result = dict()
        for key, value in dc.items():
            if type(value) is str or type(value) is int:
                result[key] = value
            elif type(value) is dict:
                result.update(self._get_dict_data(value))
            elif type(value) is list:
                result.update(self._get_list_data(key=key, ls=value))
        return result

    def _get_full_list_headers(self, generator_of_dict):
        """формирование списка названий столбцов"""
        for dict_item in generator_of_dict():
            new_keys = set(dict_item.keys())
            if not self.headers.issuperset(new_keys):
                self.headers.update(new_keys)

    def write_to_file(self, strings_generator) -> str:
        """Запись данных в CSV"""
        csv_path = os.path.join(str(self.json_file) + '_converted.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=list(self.headers))
            writer.writeheader()
            for row in strings_generator():
                if not self.headers == set(row.keys()):
                    diff = list(self.headers.difference(set(row.keys())))
                    row.update(dict(zip(diff, repeat(''))))
                writer.writerow(row)
        self.json_data = None
        return csv_path

    def get_string(self, answer):
        """Генерация строки"""
        if answer == 'l':
            return self._get_data_for_string_from_list
        else:
            self._search_key_in_dict(key=answer, dict_for_search=self.json_data)
            return self._get_data_for_string_from_dict

    def run(self) -> str:
        self._print_json_data()
        answer = self._get_user_input()
        if answer == 'p':
            self.interface.error("Pass json file!")
            return ''

        self._read_json_file()
        strings_generator = self.get_string(answer)
        self._get_full_list_headers(strings_generator)
        return self.write_to_file(strings_generator)


if __name__ == '__main__':
    conv = ConvertorJSON('tests\\test_file.json')
    conv.run()
