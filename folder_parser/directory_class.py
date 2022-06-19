import datetime
import enum
import json
from logging import ERROR
import os
import re
import shutil
import time
from pathlib import Path

from dpath.util import new

from pyunpack import Archive
from cronos_dump import is_cronos, convert_to_csv

from . import utils
from .store import BASE_TYPES, PARSING_DISK, SOURCE_DISK, ERROR_EXTENSIONS


class DirStatus(enum.Enum):
    PARSE = 'for parsing'
    DONE = 'done'
    SKIP = 'skipped'
    ERROR = 'error folder'
    PENDING = 'pending'


class Directory:

    def __init__(self, path, base_type, status=DirStatus.PARSE, reparse_file_state=False):
        self.reparse_files_state = reparse_file_state
        if base_type not in BASE_TYPES:
            raise ValueError(f"Wrong base type provided: {base_type}")
        self.path = path if isinstance(path, Path) else Path(path)
        self.name = self.path.name
        self.base_type = base_type
        self.status = status
        self.done_parse = False

        self.base_info = None
        self.files_extensions = {}
        self.error_files_count = 0
        self.done_parsed_path = os.path.join(self.path, 'done_parsed_file.txt')
        self.done_parsed_file = []
        self.all_files_status = set()
        self.all_files = None
        self.pending_files = {}
        self.commands = {}

        if self.status == DirStatus.PARSE:
            self.all_files = self._get_all_files()
            if self.all_files:
                self.parse_files = self._get_parse_files()
                self.files_count = len(self.all_files)
                self.left_files = len(self.parse_files) + 1
            self.command_file = open(os.path.join(self.path, '_command_.txt'), 'w', encoding='utf-8', errors='replace')
            if not self.all_files:
                self.status = DirStatus.ERROR
            try:
                self.base_info = self._get_base_info()
            except:
                self.status = DirStatus.ERROR

    def iterate(self, auto_parse):
        for file in self.parse_files:
            _, extension = os.path.splitext(file)
            if not extension.lower() in ERROR_EXTENSIONS:
                self.left_files -= 1
                # if extension.lower() == '.json' and not auto_parse:
                    # TODO Убрать вызов
                    # new_file = self.convert_json(file)
                    # self.insert_in_done_parsed_file(file)
                    # if new_file:
                    #     yield new_file
                    # else:
                    #     continue
                # else:
                yield file

    # TODO Убрать функцию
    # def convert_json(self, file_path) -> str:
    #     """Запускает конвертор JSON"""
    #     convertor = ConvertorJSON(file=file_path)
    #     converted_file = convertor.run()
    #     return converted_file

    def write_commands(self):
        """ Принимает команды в виде словаря {rewrite_file: command} """
        if not self.command_file:
            raise AttributeError("У папки нет command-файла. Проверьте статус папки (PARSE)")
        json.dump(self.commands, self.command_file)

    def close(self):
        if self.command_file:
            self.command_file.close()

    def move_to(self, destination):
        # path_source = C:\Source\db\database\item1
        # path_source = C:\Source\combo\database
        path_source = str(self.path)
        if not os.path.exists(path_source):
            return "Папка не существует"
        # base_source = S:\Source\db\database\item1
        base_source = path_source.replace(f'{PARSING_DISK}:', f'{SOURCE_DISK}:')

        # basedir = C:\Source\db\database
        base_dir = os.path.join(*Path(path_source).parts[:4])

        if self.base_type == 'combo':
            # base = database
            base = Path(path_source).parts[3]

            # base_dest = S:\Error\combo
            base_dest = os.path.join(f'{SOURCE_DISK}:\\', destination.capitalize(), self.base_type)

            # path_move = C:\Error\combo
            path_move = os.path.join(f'{PARSING_DISK}:\\', destination.capitalize(), self.base_type)

        else:
            # C:\Souce\db\database\item1
            # _database = item1
            base = Path(path_source).parts[4]
            # base = database
            _database = Path(path_source).parts[3]

            # path_move = C:\Error\db\database
            path_move = Path(os.path.join(f'{PARSING_DISK}:\\', destination.capitalize(), self.base_type, _database))

            # base_dest = S:\Error\db\database
            base_dest = os.path.join(f'{SOURCE_DISK}:\\', destination.capitalize(), self.base_type, _database)

        os.makedirs(str(path_move), exist_ok=True)
        os.makedirs(str(base_dest), exist_ok=True)
        if os.path.exists(os.path.join(path_move, base)):
            shutil.rmtree(os.path.join(path_move, base))
        # Перемещение
        shutil.move(str(path_source), str(path_move))
        shutil.move(base_source, base_dest)
        # Чистка пустых папок
        if os.path.exists(base_dir) and not os.listdir(base_dir):
            shutil.rmtree(base_dir)
        _base_rm = os.path.join(*Path(base_source).parts[:4])
        if os.path.exists(_base_rm) and not os.listdir(_base_rm):
            shutil.rmtree(_base_rm)

    def _get_all_files(self, paths_for_pass=[]):
        """ Возвращает все файлы"""

        all_files: list[Path] = []
        for root, dirs, files in os.walk(self.path):
            if root in paths_for_pass:
                continue
            is_cronos_dir = any([is_cronos(f) for f in files])
            if is_cronos_dir:
                print(f'{root} dir is cronos. Converting to csv...')
                output_dir = os.path.join(root, 'csv')
                try:
                    convert_to_csv(root, output_dir=output_dir, remove_if_exist=True)
                except ImportError:
                    self.status = ERROR
                    return None
                return self._get_all_files(paths_for_pass=paths_for_pass + [root])

            for f in files:
                file = Path(os.path.join(root, f))
                is_archive = utils.is_archive(f)
                if f not in paths_for_pass and is_archive:
                    print('ARCHIVE UNPACKING:', f)
                    try:
                        Archive(file).extractall(file.parent)
                    except:
                        self.status = ERROR
                        return None
                    return self._get_all_files(paths_for_pass=paths_for_pass + [f])
                # if f not in paths_for_pass and not utils.is_escape_file(f) and f.endswith('.json'):
                #     print('JSON CONVERTING:', f)
                #     try:
                #         conv = ConvertorJSON(str(file.absolute()))
                #         conv.run()
                #     except ImportError:
                #         self.status = ERROR
                #         return None
                #     return self._get_all_files(paths_for_pass=paths_for_pass + [f])

                if not utils.is_escape_file(f) and not is_archive:
                    all_files.append(file)
        return all_files

    def _get_parse_files(self):
        """ Возвращает все файлы кроме readme, _command_ и т.п. """
        self._get_done_parsed_file()

        parse_files: list[Path] = []
        for file in self.all_files:
            if not self.reparse_files_state and str(file) in self.done_parsed_file:
                self.all_files_status.add('parse')
                continue
            parse_files.append(file)
            extension = file.suffix
            extension = extension.lower()
            self.files_extensions[extension] = self.files_extensions.get(extension, 0) + 1
            if extension in ERROR_EXTENSIONS:
                self.error_files_count += 1

        return parse_files

    def _get_done_parsed_file(self):
        if os.path.exists(self.done_parsed_path):
            with open(self.done_parsed_path, 'r', encoding='utf-8') as done_parsed_file:
                self.done_parsed_file = [x := re.sub('\n', '', line) for line in done_parsed_file.readlines()]
        else:
            self.done_parsed_file = []

    def _check_done_parse_all(self, all_files):
        if self.done_parsed_file and not all_files:
            self.done_parse = True


    def insert_in_done_parsed_file(self, file_path):
        with open(self.done_parsed_path, 'a', encoding='utf-8') as done_parsed_file:
            done_parsed_file.write(str(file_path) + '\n')

    def _get_base_info(self):
        source = ''
        date = ''
        name = self._get_base_name_from_folder()  # Имя из названия папки
        _name, source, date = self._get_info_from_readme()
        name = _name if not name else name
        if not source:
            source = 'OLD DATABASE' if self.base_type == 'db' else 'OLD COMBO'
        if not date:
            if self.base_type == 'combo':
                date = self._get_date_from_folder()

        # Если дата в неверном формате, то взять дату создания файла
        if not date or not re.search(r'\d{4}-\d{2}-\d{2}', date):
            date = self._get_oldest_file_date()
        return {'name': name, 'date': date, 'source': source}

    def _get_base_name_from_folder(self):
        if utils.check_bad_symbol(self.path.absolute().parent.name):
            if self.base_type == 'db':
                return self.path.absolute().parent.name
            else:
                return self.name.split('_', 2)[2].replace('_', ' ')
        return None

    def _get_date_from_folder(self):
        return self.name.split('_', 2)[0]

    def _get_oldest_file_date(self):
        dates = []
        for file_path in self.all_files:
            file = Path(file_path)
            create_date = file.stat().st_mtime
            str_date = time.ctime(create_date)
            date = datetime.datetime(*(time.strptime(str_date)[0:6]))
            dates.append(date.strftime("%Y-%m-%d"))
        date = min(dates)
        return date

    def _get_info_from_readme(self):
        path_to_readme = os.path.join(self.path, 'readme.txt')
        if not os.path.exists(path_to_readme):
            return None, None, None
        encoding = utils.get_encoding_file(path_to_readme)
        readme_string = open(os.path.join(self.path, 'readme.txt'), encoding=encoding).readlines()
        _date = readme_string[0].replace("\n", "") if readme_string else ''
        _source = None
        _name = readme_string[1].replace("\n", "") if len(readme_string) > 1 else ''
        for line in readme_string:
            if re.match(r'https?://', line):
                _source = re.match(r'https?://[\w\d\-=\\/._?#!]+', line.replace("\n", "")).group(0)
                break
            elif re.match(r'OLD (D|C)', line):
                _source = re.match(r'OLD (D|C)[\w]+', line.replace("\n", "")).group(0)
                break
        return _name, _source, _date

    def __str__(self):
        return f"[{self.status.value}] {self.path}"
