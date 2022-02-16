import csv
import re
from collections import Counter

from rich.console import Console

from engine_modul.interface import UserInterface
from engine_modul.normalize_col_names import normalize_col_names
from engine_modul.store import ASSERT_NAME, COLUMN_NAME_TRIGGERS
from reader import Reader

console = Console()


class FileHandler:
    """
    Класс для хранения параметров и методов файла
    """

    def __init__(self, file, file_path):
        self.file = file
        self.file_path = file_path
        self.delimiter = None
        self.num_columns = None
        self.interface = UserInterface()
        self.keys = None
        self.cols_name = None
        self.column_names = None
        self.skip = 0

    def handle_file(self):
        self.delimiter = self.get_delimiter()
        self.get_num_columns()

    def get_delimiter(self):
        """
        Получение разделителя
        :param path: путь до csv
        :return: dialect
        """
        list_line = []
        self.file.open()
        for i, line in enumerate(self.file):
            list_line.append(line)
            if i > 35:
                break

        if len(list_line) > 25:
            list_line = list_line[5:]
        try:
            return csv.Sniffer().sniff(''.join(list_line), delimiters=',:;\t').delimiter
        except csv.Error:
            return None

    def is_simple_file(self, pattern, file: Reader, deep_line_check=100, top_skip=10):
        """
        Метод для автопарсинга

        @param pattern:
        @param file:
        @param deep_line_check:
        @return:
        """
        file.open()
        coefficient = 0.5
        result = 0
        count_check_rows = 0
        for i, line in enumerate(file):
            count_check_rows += 1
            if i > top_skip and re.match(pattern, line):
                result += 1
            if i > deep_line_check + top_skip:
                break
        if result > abs(count_check_rows * coefficient - top_skip):
            return True
        return False

    def get_keys(self, input_keys=None):
        """
        Функция преобразования введенных ключей

        @param input_keys: "1=usermail, 3=username"
        :return: keys [(tuple)]: (, colsname_plain  Порядок для бд, ключи для fix.py

        """
        if not input_keys:
            input_keys = self.column_names
        args_inp = input_keys.split(',')
        key_res = []
        keys = []
        for arg in args_inp:
            splited_key_data = None
            arg = arg.strip()
            index_and_key = arg.split('=')
            if len(index_and_key) < 2:
                raise ValueError()
            if 'uai' in index_and_key[1]:
                col_name = 'user_additional_info'
                if '+' in index_and_key[1]:
                    add_info = index_and_key[1].split('+')[1]
                    splited_key_data = (index_and_key[0], 'user_additional_info', add_info)
                else:
                    splited_key_data = (index_and_key[0], 'user_additional_info', '')
            elif index_and_key[1] in list(ASSERT_NAME.keys()):
                col_name = ASSERT_NAME[index_and_key[1]]
                splited_key_data = (index_and_key[0], ASSERT_NAME[index_and_key[1]])
            elif index_and_key[1] in list(ASSERT_NAME.values()):
                col_name = index_and_key[1]
                splited_key_data = (index_and_key[0], index_and_key[1])
            else:
                raise ValueError('Bad field name')
            key_res.append(col_name)
            keys.append(splited_key_data)
        colsname_plain = key_res[::]
        if 'user_additional_info' in colsname_plain:
            while colsname_plain.count('user_additional_info') > 0:
                colsname_plain.remove('user_additional_info')
            colsname_plain.append('user_additional_info')
        self.keys = keys
        self.cols_name = colsname_plain
        return keys, colsname_plain

    def get_count_rows(self):
        self.file.open()
        def foo(x): print(x); return 1
        count = sum(1 for _ in self.file)
        return count

    def get_num_columns(self):
        """
        Расчет количества разделителей в строке
        @return:
        """
        _sum_delimiter = 0
        _sum_lines = 0
        _counter = Counter()
        pat = re.compile(f'{self.delimiter}')
        self.file.open()
        lines = []
        for i, line in enumerate(self.file):
            lines.append(line)
            if i == 25:
                break
        n = 0 if len(lines) < 10 else 5
        for i, line in enumerate(lines):
            if i >= n and (line != '' or line != '\n'):
                line = re.sub(r'(\"[^\"]*?\")', '', line)
                _sum_delimiter += len(re.findall(pat, line))
                _counter[_sum_delimiter] += 1
            _sum_delimiter = 0

        _result = max(dict(_counter).items(), key=lambda item: item[1])[0]
        # if _sum_delimiter and _sum_lines:
        #     _result = _sum_delimiter // _sum_lines
        self.num_columns = _result
        return _result or 1

    def get_column_names(self, auto: bool) -> str:
        """
        Поиск заголовков столбцов
        Args:
            file_path (Path): parsing file
            auto (bool, optional): mode parsing auto or No
        Returns:
            _colsname (str): 1=un,2=upp,3=h or None
        """
        column_names_line = None
        self.file.open()
        for i, line in enumerate(self.file):

            # Finding line with column names
            if i < 6 and not column_names_line:
                _new_line = line.lower()
                for trigger in COLUMN_NAME_TRIGGERS:
                    if re.search(trigger, _new_line):
                        column_names_line = re.sub(r'\n$', '', line)
                        break
                    else:
                        column_names_line = ''
            # Printing and copying possible column names
            if column_names_line and not auto:
                self.column_names = normalize_col_names(string=column_names_line, delimiter=self.delimiter)
                _answer = self.interface.ask_column_names(self.column_names)
                if _answer:
                    self.skip = 1
                else:
                    self.column_names = ''
            return self.column_names
