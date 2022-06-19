from folder_parser.store import ERROR_EXTENSIONS
import os
import subprocess

from rich.console import Console
from rich.prompt import Prompt, Confirm

from engine_modul.file_handler import FileHandler
from engine_modul.interface import UserInterface
from engine_modul.store import FileMode
from folder_parser.folder_parser import FolderParser
from folder_parser.directory_class import Directory, DirStatus
from reader.reader import Reader


user = os.environ.get('USER_NAME')
password = os.environ.get('USER_PASSWORD')
PD = os.environ.get('PARSING_DISK_NAME')
SD = os.environ.get('SOURCE_DISK_NAME')
TOO_MANY_FILES_TRESHOLD = int(os.environ.get('TOO_MANY_FILES_TRESHOLD', 100))
console = Console()


class Engine:

    def __init__(self, auto_parse, full_auto, error_mode, daemon=False):
        self.type_base = None
        self.auto_parse = auto_parse
        self.full_auto = full_auto
        self.error_mode = error_mode
        self.daemon = daemon
        self.handler_folders = None
        self.interface = UserInterface()

    def manual_parsing_menu(self) -> FileMode:
        """
        Ручной парсинг
        @return:
        """
        menu = True
        dir = self.handler_folders.current_folder
        while menu:
            mode = self.interface.ask_mode_handle()
            if mode == FileMode.JSON_PARSER:
                return mode
            mode = self.handler_mode(mode)
            if mode in [FileMode.PASS_DIR, FileMode.SKIP_FILE, FileMode.ERROR_DIR, FileMode.TRASH_DIR, FileMode.JSON_PARSER]:
                return mode

            dir.file_handler.get_column_names(self.full_auto)
            self.interface.show_num_columns(dir.file_handler.num_columns + 1)
            _init_cols_keys = dir.file_handler.column_names

            while True:
                dir.file_handler.num_columns = self.interface.ask_num_cols(dir.file_handler.num_columns)
                if dir.file_handler.num_columns != -1:
                    menu = False
                else:
                    break
                _cols_keys = self.interface.ask_cols_keys(dir.file_handler.column_names)
                if not _cols_keys:
                    dir.file_handler.column_names = ''
                    _init_cols_keys = ''
                    continue
                else:
                    dir.file_handler.column_names = _cols_keys
                try:
                    dir.file_handler.get_keys()
                except Exception as ex:
                    print(f'Ошибка в ключах: {ex}')
                    continue
                max_key = max(dir.file_handler.keys, key=lambda x: int(x[0]))
                if not max_key:
                    continue
                dir.file_handler.skip = self.interface.ask_skip_lines(dir.file_handler.skip)
                if (dir.file_handler.num_columns + 1) >= int(max_key[0]) and dir.file_handler.skip != -1:
                    break
                dir.file_handler.column_names = _init_cols_keys

    def handler_mode(self, mode) -> FileMode:
        dir = self.handler_folders.current_folder
        while True:
            if mode == FileMode.PASS_DIR:
                self.handler_folders.current_folder.all_files_status.add('pass')
                self.handler_folders.skip_folder()
                return mode
            elif mode == FileMode.SKIP_FILE:
                self.handler_folders.current_folder.all_files_status.add('trash')
                return mode
            elif mode == FileMode.OPEN_FILE:
                # Открыть в EmEditor
                subprocess.run(f'Emeditor "{dir.file_handler.file_path}"')
                self.interface.pause()
                dir.file_handler.rehandle_file_parameters()
            elif mode == FileMode.OPEN_IN_NOTEPAD:
                # Открыть в Notepad++
                subprocess.run(f'notepad++ "{dir.file_handler.file_path}"')
                dir.file_handler.rehandle_file_parameters()
            elif mode == FileMode.DELIMITER:
                dir.file_handler.delimiter = self.interface.ask_delimiter()
                dir.file_handler.get_num_columns()
            elif mode == FileMode.ERROR_DIR:
                # Перенести папку в ERROR
                self.handler_folders.current_folder.all_files_status.add('error')
                try:
                    dir.file_handler.reader.close()
                    self.handler_folders.skip_folder(move_to='Error')
                    return mode
                except Exception as ex:
                    console.print(f'[magenta]Не могу переместить[/magenta]: "[red]{ex}[/red]"')
                    answer = Prompt.ask(f"[green]Если все ОК нажмите Enter", choices=['y', 'n'], default='y')
                    if answer == 'y':
                        mode = FileMode.PASS_DIR
                        return mode
                    raise ex
            elif mode == FileMode.TRASH_DIR:
                try:
                    dir.file_handler.reader.close()
                    self.handler_folders.current_folder.all_files_status.add('trash')
                    self.handler_folders.skip_folder(move_to='Trash')
                    return mode
                except Exception as ex:
                    console.print(f'[magenta]Не могу переместить[/magenta]: "[red]{ex}[/red]"')
                    answer = Prompt.ask(f"[green]Если все ОК нажмите Enter", choices=['y', 'n'], default='y')
                    if answer == 'y':
                        mode = FileMode.PASS_DIR
                        return mode
                    raise ex
            elif mode == FileMode.START:
                self.handler_folders.current_folder.all_files_status.add('parse')
                break
            mode = self.interface.ask_mode_handle()
            if mode in (FileMode.JSON_PARSER, ):
                break
        return mode

    def parsing_file(self):
        mode = None
        dir = self.handler_folders.current_folder
        dir.file_handler.rehandle_file_parameters()

        parse_automaticly = dir.file_handler.autoparse()
        if parse_automaticly:
            self.handler_folders.current_folder.all_files_status.add('parse')

        if not self.auto_parse or dir.file_handler.num_columns == 0 or not parse_automaticly:
            if self.full_auto:
                return FileMode.PASS_DIR
            mode = self.manual_parsing_menu()
            if mode in [FileMode.SKIP_FILE, FileMode.PASS_DIR, FileMode.TRASH_DIR, FileMode.ERROR_DIR, FileMode.JSON_PARSER]:
                return mode

        dir.file_handler.parse_file()

    def check_error_extensions(self, dir: Directory):
        """ Возвращает True если есть error-файлы или файлов слишком много """
        error = False
        if not self.error_mode and dir.error_files_count:
            console.print(f'Error-файлы в папке: [red]{dir.error_files_count}[/red]/{dir.files_count}')
            console.print(
                ', '.join(
                    [f"{'[red]'*(k in ERROR_EXTENSIONS)}'{k}': {v}{'[/red]'*(k in ERROR_EXTENSIONS)}" 
                    for k, v in dir.files_extensions.items()]
                )
            )
            error = True
        elif not self.error_mode and dir.files_count >= TOO_MANY_FILES_TRESHOLD:
            console.print(f'[red]Слишком много файлов: {dir.files_count}')
            error = True
        else:
            console.print(f'\n\n[cyan]Количество файлов: {dir.files_count}')

        return error

    def start(self):
        self.type_base = self.interface.ask_type_base()
        _reparse_file_state = self.interface.ask_reparse_file()
        self.handler_folders = FolderParser(self.type_base)
        for dir in self.handler_folders.iterate(_reparse_file_state):
            if dir.status == DirStatus.PARSE:
                self.interface.print_dirs_status(str(dir.path), dir.status)
                if self.check_error_extensions(dir):
                    try:
                        self.handler_folders.skip_folder(move_to='Error')
                        console.print(f'[magenta]В ERROR:[/magenta] "[red]{str(dir.path)}[/red]"')
                    except Exception as ex:
                        console.print(f'[magenta]Не могу переместить[/magenta]: "[red]{ex}[/red]"')
                        answer = Prompt.ask(f"[green]Если все ОК нажмите Enter", choices=['y', 'n'], default='y')
                        if answer != 'y':
                            raise ex
                    continue
                self.handler_folders.current_folder.all_files_status.clear()
                self.writer_data = {
                    'base_type': dir.base_type,
                    'base_name': dir.base_info['name'],
                    'base_source': dir.base_info['source'],
                    'base_date': dir.base_info['date']
                }
                for file in dir.iterate(self.auto_parse):
                    
                    dir.file_handler = FileHandler(file, self.writer_data, self.auto_parse, self.full_auto, self.daemon)
                    # Отлов ошибок для непрерывания full_auto
                    try:
                        self.interface.show_left_dirs(self.handler_folders.left_dirs)
                        self.interface.show_left_files(dir.left_files)
                        mode = self.parsing_file()
                        if mode == FileMode.JSON_PARSER:
                            converted_file = dir.file_handler.convert_json()
                            if not converted_file:
                                mode = FileMode.SKIP_FILE
                            else:
                                dir.insert_in_done_parsed_file(file)
                                file = converted_file
                                dir.file_handler.reader = Reader(converted_file)
                                mode = self.parsing_file()
                    except Exception as e:
                        if self.full_auto:
                            mode = FileMode.PASS_DIR
                        else:
                            if not Confirm.ask(f'Ошибка при парсинге файла [magenta]{file.name}[/], пропустить его?'):
                                raise e
                            else:
                                continue
                    if mode in [FileMode.PASS_DIR, FileMode.TRASH_DIR, FileMode.ERROR_DIR]:
                        dir.pending_files = []
                        break

                    if not self.daemon:
                        dir.finish_file()
                    else:
                        dir.add_pending_file()

                # Определение условий
                command_path = os.path.join(dir.path, '_command_.txt')
                is_other_command = os.path.getsize(command_path) > 2 if os.path.exists(command_path) else True
                all_trash = self.handler_folders.current_folder.all_files_status == {'trash'}
                dir_not_skip = self.handler_folders.current_folder.status != DirStatus.SKIP

                # Если все файлы пропущены, статус папки не SKIP и нет других распарсенных файлов, то в трэш
                if all_trash and dir_not_skip and is_other_command:
                    try:
                        dir.file_handler.reader.close()
                        self.handler_folders.skip_folder(move_to='Trash')
                    except Exception as ex:
                        console.print(f'[magenta]Не могу переместить[/magenta]: "[red]{ex}[/red]"')
                        answer = Prompt.ask(f"[green]Если все ОК нажмите Enter", choices=['y', 'n'], default='y')
                        if answer != 'y':
                            raise ex
                        break

                if self.daemon:
                    self.handler_folders.add_current_to_pending_dirs()
                    self.handler_folders.check_pending_dirs()

                elif dir.file_handler:
                    status_is_parse = self.handler_folders.current_folder.status == DirStatus.PARSE
                    files_status_contains_parse = 'parse' in self.handler_folders.current_folder.all_files_status
                    if status_is_parse and files_status_contains_parse:
                        self.handler_folders.done_folder()
            else:
                self.interface.print_dirs_status(str(dir.path), dir.status.value)
