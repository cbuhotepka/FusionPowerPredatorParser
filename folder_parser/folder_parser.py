from logging import ERROR
import os
from pathlib import Path
from rich.console import Console

from .directory_class import Directory, DirStatus
from .store import (
    BASE_TYPES,
    PARSING_DISK,

)

console = Console()


class FolderParser:
    def __init__(self, base_type):
        if base_type not in BASE_TYPES:
            raise ValueError(f"Wrong base type provided: {base_type}")
        self.base_type = base_type
        self.path = os.path.join(f"{PARSING_DISK}:\\", 'Source', self.base_type)
        self.current_folder = None


        self.get_complete_dirs()  # устанавливает: complete_dirs_name, complete_dirs
        self.get_passed_dirs()  # устанавливает: passed_dirs_name, passed_dirs
        self.pending_dirs: list[Directory] = []
        self.left_dirs = self.count_left_dirs()

    def add_current_to_pending_dirs(self):
        self.current_folder.status = DirStatus.PENDING
        self.pending_dirs.append(self.current_folder)

    def check_pending_dirs(self):
        console.print("\nCHECKING PENDING DIRS:")
        for dir in self.pending_dirs:
            console.print("\n -", dir)
            dir.check_pending_files()

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
        # self.passed_dirs_file = open(self.passed_dirs_name, 'a+', encoding='utf-8', errors='replace')

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
                self.current_folder = Directory(folder, self.base_type, status=DirStatus.DONE, reparse_file_state=reparse_file_state)
            elif str(folder.absolute()) in self.passed_dirs:
                self.current_folder = Directory(folder, self.base_type, status=DirStatus.SKIP, reparse_file_state=reparse_file_state)
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
        self.current_folder.status = DirStatus.SKIP
        self.current_folder.close()
        if move_to:
            self.current_folder.move_to(move_to)

    def done_folder(self, dir=None):
        dir = dir if dir else self.current_folder
        dir.write_commands()
        self.complete_dirs.append(str(dir.path.absolute()))
        with open(self.complete_dirs_name, 'a+', encoding='utf-8', errors='replace') as _f:
            _f.write(str(dir.path.absolute()) + '\n')
        dir.status = DirStatus.DONE
        dir.close()

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

        if dir.status == DirStatus.PARSE:
            for file in dir.iterate():
                # возвращает путь до файла
                print('  >', file)

            dir.write_commands({'rewrite_file_path': 'command 1', f'file {i}': f'command {i}'})
            # dir.write_commands(commands: {rewrite_file: command})

            if dir.name == 'item2':
                folder_parser.skip_folder()
            elif dir.name == 'item4':
                folder_parser.done_folder()

        elif dir.status == DirStatus.ERROR:
            folder_parser.skip_folder()

        print('OUTCOME:', folder_parser.current_folder)
        # folder_parser.skip_folder(move_to='')
        # # записывает папку в passed_dirs, закрывает папку
        # # если указан move_to - перемещает папку

        # folder_parser.done_folder()
        # # записывает папку в complete_dirs, закрывает папку, перемещает в Imported
