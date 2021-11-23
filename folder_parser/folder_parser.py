import datetime
import enum
import json
from logging import ERROR
import os
import re
import shutil
import time
from pathlib import Path

from folder_parser.store import ERROR_EXTENSIONS
from folder_parser import utils
from pyunpack import Archive
from cronos_dump import is_cronos, convert_to_csv

USER = os.environ.get('USER_NAME', 'er')
PASSWORD = os.environ.get('USER_PASSWORD', 'qwerty123')
PARSING_DISK = os.environ.get('PARSING_DISK_NAME', 'C')
SOURCE_DISK = os.environ.get('SOURCE_DISK_NAME', 'W')

BASE_TYPES = ['db', 'combo']


class Status(enum.Enum):
    PARSE = 'for parsing'
    DONE = 'done'
    SKIP = 'skipped'
    ERROR = 'error folder'


class Directory:

    def __init__(self, path, base_type, status=Status.PARSE, reparse_file_state=False):
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

        if self.status == Status.PARSE:
            self.all_files = self._get_all_files()
            if self.all_files:
                self.parse_files = self._get_parse_files()
                self.files_count = len(self.all_files)
                self.left_files = len(self.parse_files) + 1
            self.command_file = open(os.path.join(self.path, '_command_.txt'), 'w', encoding='utf-8', errors='replace')
            if not self.all_files:
                self.status = Status.ERROR
            try:
                self.base_info = self._get_base_info()
            except:
                self.status = Status.ERROR

    def iterate(self):
        for file in self.parse_files:
            _, extension = os.path.splitext(file)
            if not extension.lower() in ERROR_EXTENSIONS:
                self.left_files -= 1
                yield file

    def write_commands(self, commands: dict):
        """ Принимает команды в виде словаря {rewrite_file: command} """
        if not self.command_file:
            raise AttributeError("У папки нет command-файла. Проверьте статус папки (PARSE)")
        json.dump(commands, self.command_file)

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
                print('Found cronos. Converting to csv...')
                if root == str(self.path):
                    convert_to_csv(root, output_dir=os.path.join(root, 'cronos'))
                else:
                    convert_to_csv(root)
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


class FolderParser:
    def __init__(self, base_type):
        if base_type not in BASE_TYPES:
            raise ValueError(f"Wrong base type provided: {base_type}")
        self.base_type = base_type
        self.path = os.path.join(f"{PARSING_DISK}:\\", 'Source', self.base_type)
        self.current_folder = None


        self.get_complete_dirs()  # устанавливает: complete_dirs_name, complete_dirs, complete_dirs_file
        self.get_passed_dirs()  # устанавливает: passed_dirs_name, passed_dirs, passed_dirs_file
        self.left_dirs = self.count_left_dirs()

    def get_complete_dirs(self):
        """ Читаем из файла все завершённые папки, открываем _dirs_complete_.txt для записи """
        self.complete_dirs_name = Path(os.path.join(self.path, '_dirs_complete_.txt'))
        if self.complete_dirs_name.exists():
            with open(self.complete_dirs_name, 'r', encoding='utf-8', errors='replace') as f:
                self.complete_dirs = list(map(lambda x: x.strip(), f.readlines()))
        else:
            self.complete_dirs = []
        # self.complete_dirs_file = open(self.complete_dirs_name, 'a+', encoding='utf-8', errors='replace')

    def get_passed_dirs(self):
        """ Читаем из файла все пропущенные папки, открываем _dirs_passed_.txt для записи """
        self.passed_dirs_name = Path(os.path.join(self.path, '_dirs_passed_.txt'))
        if self.passed_dirs_name.exists():
            with open(self.passed_dirs_name, 'r', encoding='utf-8', errors='replace') as f:
                self.passed_dirs = list(map(lambda x: x.strip(), f.readlines()))
        else:
            self.passed_dirs = []
        self.passed_dirs_file = open(self.passed_dirs_name, 'a+', encoding='utf-8', errors='replace')

    @property
    def all_folder_paths(self):
        """ Возвращает все папки для парсинга в виде Path """
        try:
            return self._all_folder_paths
        except AttributeError:
            self._all_folder_paths = []
            if self.base_type == 'db':
                for root_name in os.listdir(self.path):
                    if not os.path.isdir(os.path.join(self.path, root_name)):
                        continue
                    for item_name in os.listdir(os.path.join(self.path, root_name)):
                        item = Path(os.path.join(self.path, root_name, item_name))
                        if item.is_dir():
                            self._all_folder_paths.append(item)
            else:
                for root_name in os.listdir(self.path):
                    combo_dir = Path(os.path.join(self.path, root_name))
                    if combo_dir.is_dir():
                        self._all_folder_paths.append(combo_dir)
            return self._all_folder_paths

    def count_left_dirs(self):
        left_dirs = len(self.all_folder_paths)
        for folder in self.all_folder_paths:
            if str(folder.absolute()) in self.complete_dirs or str(folder.absolute()) in self.passed_dirs:
                left_dirs -= 1
        return left_dirs

    def iterate(self, reparse_file_state):
        for folder in self.all_folder_paths:
            if str(folder.absolute()) in self.complete_dirs:
                self.current_folder = Directory(folder, self.base_type, status=Status.DONE, reparse_file_state=reparse_file_state)
            elif str(folder.absolute()) in self.passed_dirs:
                self.current_folder = Directory(folder, self.base_type, status=Status.SKIP, reparse_file_state=reparse_file_state)
            else:
                self.current_folder = Directory(folder, self.base_type, reparse_file_state=reparse_file_state)
                self.left_dirs -= 1
            yield self.current_folder

    def close_folder(self):
        self.current_folder.close()

    def skip_folder(self, move_to=None):
        self.passed_dirs.append(str(self.current_folder.path.absolute()))
        with open(self.passed_dirs_name, 'a+', encoding='utf-8', errors='replace') as _f:
            _f.write(str(self.current_folder.path.absolute()) + '\n')
        self.current_folder.status = Status.SKIP
        self.current_folder.close()
        if move_to:
            self.current_folder.move_to(move_to)

    def done_folder(self):
        self.complete_dirs.append(str(self.current_folder.path.absolute()))
        with open(self.complete_dirs_name, 'a+', encoding='utf-8', errors='replace') as _f:
            _f.write(str(self.current_folder.path.absolute()) + '\n')
        self.current_folder.status = Status.DONE
        self.current_folder.close()

    def finish(self):
        if self.complete_dirs_file:
            self.complete_dirs_file.close()
        if self.passed_dirs_file:
            self.passed_dirs_file.close()

    def __str__(self):
        return f"Fusion-Power-Predator-{self.base_type.upper()}-Parser"


if __name__ == '__main__':
    print('\n' * 20)
    folder_parser = FolderParser(base_type='db')
    # Читает или создаёт complete_dirs, passed_dirs
    print(folder_parser)

    print(folder_parser.complete_dirs)
    print(folder_parser.passed_dirs)

    for i, dir in enumerate(folder_parser.iterate()):
        # Смотрит все папки, устанавливает self.current_folder на текущую инициализирует и возвращает Directory()
        # dir.name, dir.path, dir.base_type, dir.status
        # если статус PARSE:
        # создаёт и открывает self.command_file, инициализирует self.all_files (пути), self.base_info - {name: '', date: '', source: ''}
        print()
        print('___' * 30, '\nNEW DIRECTORY')
        print('CURRENT FOLDER:', folder_parser.current_folder)
        print('BASE INFO:', dir.base_info)
        print('FILES COUNT:', dir.files_count)
        print('EXTENSIONS:', dir.files_extensions)
        print('ERROR/ALL FILES:', f'{dir.error_files_count}/{dir.files_count}')

        if dir.status == Status.PARSE:
            for file in dir.iterate():
                # возвращает путь до файла
                print('  >', file)

            dir.write_commands({'rewrite_file_path': 'command 1', f'file {i}': f'command {i}'})
            # dir.write_commands(commands: {rewrite_file: command})

            if dir.name == 'item2':
                folder_parser.skip_folder()
            elif dir.name == 'item4':
                folder_parser.done_folder()

        elif dir.status == Status.ERROR:
            folder_parser.skip_folder()

        print('OUTCOME:', folder_parser.current_folder)
        # folder_parser.skip_folder(move_to='')
        # # записывает папку в passed_dirs, закрывает папку
        # # если указан move_to - перемещает папку

        # folder_parser.done_folder()
        # # записывает папку в complete_dirs, закрывает папку, перемещает в Imported
