import os
from pathlib import Path
from datetime import time

from store import ERROR_EXTENSIONS


USER = os.environ.get('USER_NAME', 'er')
PASSWORD = os.environ.get('USER_PASSWORD', 'qwerty123')
PARSING_DISK = os.environ.get('PARSING_DISK_NAME', 'C')
SOURCE_DISK = os.environ.get('SOURCE_DISK_NAME', 'W')

BASE_TYPES = ['db', 'combo']


def is_escape_file(file_name: str):
    file_name = file_name.lower()
    return any(
        file_name.startswith('_'),
        file_name.endswith('_rewrite.txt'),
        file_name == 'readme.txt',
    )


class Direcotry:
    def __init__(self, path, base_type):
        if base_type not in BASE_TYPES:
            raise ValueError(f"Wrong base type provided: {base_type}")
        self.path = path if isinstance(path, Path) else Path(path)
        self.name = self.path.name
        self.base_type = base_type

        self.all_files = self.get_all_files()
        self.base_info = self.get_base_info()

    def get_all_files(self):
        all_files: list[Path] = []
        for root, dirs, files in os.walk(self.path):
            files = list(filter(lambda x: not is_escape_file(x), files))
            return [Path(os.path.join(root, f)) for f in files]

    def get_base_info(self):
        path_to_readme = os.path.join(self.path, 'readme.txt')
        source = ''
        date = ''

        if utils.check_base_name(dir.absolute().parent.name):
            name = dir.absolute().parent.name
        else:
            name = None

        if os.path.exists(path_to_readme):
            encod = utils.get_encoding_file(path_to_readme)
            readme = open(path_to_readme, encoding=encod)
            args = readme.readlines()
            i = 0
            date = args[i].replace("\n", "")
            _name, source = utils.get_source_from_readme(path_to_readme, encod)
            if not name:
                name = _name
        else:
            source = 'OLD DATABASE'

        # Если дата в неверном формате, то взять дату создания файла
        if not re.search(r'\d{4}-\d{2}-\d{2}', date):
            date = get_date_create(dir)
            print('Смена даты на', date)
        if not name and not full_auto:
            console.print(f"[yellow]{dir.absolute().parent.name}")
            console.print("[yellow]Не корректное имя!")
            name = Prompt.ask('Name: ')
        elif not name:
            return None, None, None
        return {'name': name, 'date': date, 'source': source}

    def get_oldest_file_date(self):
        dates = []
        for file_path in self.all_files:
            file = Path(file_path)
            create_date = file.stat().st_mtime
            str_date = time.ctime(create_date)
            date = time.strptime(str_date)
            dates.append(date.strftime("%Y-%m-%d"))
        date = min(dates)
        return date


class FolderParser:
    def __init__(self, base_type):
        if base_type not in BASE_TYPES:
            raise ValueError(f"Wrong base type provided: {base_type}")
        self.base_type = base_type
        self.path = os.path.join(PARSING_DISK, 'Source')
        
        self.get_complete_dirs()    # устанавливает: complete_dirs_name, complete_dirs, complete_dirs_file
        self.get_passed_dirs()      # устанавливает: passed_dirs_name, passed_dirs, passed_dirs_file


    def get_complete_dirs(self):
        """ Читаем из файла все завершённые папки, открываем dirs_complete.txt для записи """
        self.complete_dirs_name = Path(os.path.join(self.path, 'dirs_complete.txt'))
        if self.complete_dirs_name.exists():
            with open(self.complete_dirs_name, 'r', encoding='utf-8', errors='replace') as f:
                self.complete_dirs = list(map(lambda x: x.strip(), f.readlines()))
        else:
            self.complete_dirs = []
        self.complete_dirs_file = open(self.complete_dirs_name, 'a+', encoding='utf-8', errors='replace')

    def get_passed_dirs(self):
        """ Читаем из файла все пропущенные папки, открываем dirs_passed.txt для записи """
        self.passed_dirs_name = Path(os.path.join(self.path, 'dirs_passed.txt'))
        if self.passed_dirs_name.exists():
            with open(self.passed_dirs_name, 'r', encoding='utf-8', errors='replace') as f:
                self.passed_dirs = list(map(lambda x: x.strip(), f.readlines()))
        else:
            self.passed_dirs = []
        self.passed_dirs_file = open(self.passed_dirs_name, 'a+', encoding='utf-8', errors='replace')

    @property
    def all_folders(self):
        """ Возвращает все папки для парсинга в виде Path """
        try:
            return self._all_folders
        except AttributeError:
            self._all_folders = []
            if self.base_type == 'db':
                for root_name in os.listdir(self.path):
                    if not os.path.isdir(os.path.join(self.path, root_name)):
                        continue
                    for item_name in os.listdir(os.path.join(self.path, root_name)):
                        item = Path(os.path.join(self.path, root_name, item_name))
                        if item.is_dir():
                            self._all_folders.append(item)
            else:
                for root_name in os.listdir(self.path):
                    combo_dir = Path(os.path.join(self.path, root_name))
                    if combo_dir.is_dir():
                        self._all_folders.append(combo_dir)
            return self._all_folders
    
    def iterate(self):
        for folder in self.all_folders:
            if str(folder.absolute()) in self.complete_dirs:
                # console.print(f'[bold green]{folder.absolute()}')
                continue
            elif str(folder.absolute()) in self.passed_dirs:
                # console.print(f'[bold yellow]{folder.absolute()}')
                continue
            self.current_folder = Direcotry(folder, self.base_type)