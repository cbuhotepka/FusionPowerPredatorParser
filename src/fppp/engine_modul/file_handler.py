import csv
import re
from collections import Counter

from rich.console import Console
from pathlib import Path
from celery.result import AsyncResult

from .interface import UserInterface
from .normalize_col_names import normalize_col_names
from .store import ASSERT_NAME, COLUMN_NAME_TRIGGERS
from ..json_parser.json_parser import ConvertorJSON
from ..reader import Reader
from ..writer import Writer
from .utils import find_delimiter
from ..validator.validator import Validator
from ..celery_parser import daemon_parse, ParserResponse
from rich.progress import track
from .store import PATTERN_TEL_PASS, PATTERN_USERMAIL_USERNAME_PASS, PATTERN_UID_UN_IP_UM_PASS

console = Console()


class FileHandler:
    """
    Класс для хранения параметров и методов файла
    """

    def __init__(self, file_path, writer_data, auto_parse, full_auto, daemon=False):
        self.file_path = Path(file_path)
        self.writer_data = writer_data
        self.reader = Reader(file_path)
        self.writer = Writer(**writer_data)

        self.auto_parse = auto_parse
        self.full_auto = full_auto
        self.daemon = daemon
        self.daemon_task: AsyncResult = None

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
        self.reader.open()
        for i, line in enumerate(self.reader):
            list_line.append(line)
            if i > 35:
                break

        if len(list_line) > 25:
            list_line = list_line[5:]
        try:
            return find_delimiter(list_line)
            # return csv.Sniffer().sniff(''.join(list_line), delimiters=',:;\t').delimiter
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

    def get_num_columns(self):
        """
        Расчет количества разделителей в строке
        @return:
        """
        _sum_delimiter = 0
        _sum_lines = 0
        _counter = Counter()
        pat = re.compile(f'{self.delimiter}')
        self.reader.open()
        lines = []
        for i, line in enumerate(self.reader):
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
        self.reader.open()
        for i, line in enumerate(self.reader):

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

    # =================================================================================
    def parse_file(self):
        if self.daemon:
            self.daemon_task = daemon_parse.delay(
                keys=self.keys,
                num_columns=self.num_columns,
                delimiter=self.delimiter,
                skip=self.skip,
                file_path=str(self.file_path),
                writer_data=self.writer_data,
            )
        else:
            self.simple_parse()

    def simple_parse(self):
        self.writer.start_new_file(self.file_path, self.delimiter if self.delimiter != '\t' else ';')
        with console.status('[bold blue]Подсчет строк...', spinner='point', spinner_style="bold blue") as status:
            count_rows_in_file = self.reader.get_count_rows()
            console.print(f'[yellow]Строк в файле: {count_rows_in_file}')
        validator = Validator(self.keys, self.num_columns, self.delimiter)
        self.reader.open(skip=self.skip)
        for line in track(self.reader, description='[bold blue]Парсинг файла...', total=count_rows_in_file):

            for fields_data in validator.get_fields(line):

                # Пропуск записи если в полях меньше 2 не пустых значений
                count_not_empty_values = sum(map(lambda x: bool(x), fields_data.values()))
                if fields_data['algorithm']:
                    if count_not_empty_values < 3:
                        continue
                else:
                    if count_not_empty_values < 2:
                        continue

                # Запись полей в файл
                self.writer.write(fields_data)

    def rehandle_file_parameters(self):
        """
        Получение параметров файла: разделитель, количество столбцов, название столбцов
        @return:
        """
        self.interface.show_file(self.reader)
        self.handle_file()
        self.interface.show_delimiter(self.delimiter)
        self.interface.show_num_columns(self.num_columns + 1)

    def convert_json(self) -> str:
        """Запускает конвертор JSON"""
        convertor = ConvertorJSON(file=self.file_path)
        converted_file = convertor.run()
        return converted_file

    def autoparse(self) -> bool:
        if self.auto_parse and self.delimiter and (
                self.is_simple_file(PATTERN_TEL_PASS, self.reader)):
            self.get_keys('1=tel, 2=password')
            self.num_columns = 1
            console.print('[cyan]' + 'Автопарсинг tel password')
            return True
        elif self.auto_parse and self.delimiter and (
                self.is_simple_file(PATTERN_USERMAIL_USERNAME_PASS, self.reader)):
            self.get_keys(f'1=user_mail_name, 2=password')
            self.num_columns = 1
            console.print('[cyan]' + f'Автопарсинг umn/un password')
            return True
        elif self.auto_parse and self.delimiter and ('1:Anonymous:::' in self.reader.open().readline(500)):
            self.get_keys(f'1=uid, 2=un, 3=ip, 4=um, 5=p')
            self.num_columns = 4
            console.print('[cyan]' + f'Автопарсинг uid un ip um pass')
            return True
        else:
            return False
        
    def __str__(self):
        return str(self.file_path.name)

    def __repr__(self):
        return self.__str__()
