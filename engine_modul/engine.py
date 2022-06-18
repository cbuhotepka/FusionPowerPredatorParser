from folder_parser.store import ERROR_EXTENSIONS
import os
import subprocess

from rich.console import Console
from rich.prompt import Prompt, Confirm

from engine_modul.file_handler import FileHandler
from engine_modul.interface import UserInterface
from engine_modul.store import PATTERN_TEL_PASS, PATTERN_USERMAIL_USERNAME_PASS, PATTERN_UID_UN_IP_UM_PASS
from folder_parser.folder_parser import FolderParser
from folder_parser.directory_class import Directory, DirStatus
from json_parser.json_parser import ConvertorJSON
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
        self.daemon_processes = {}
        self.file_handler = None
        self.handler_folders = None
        self.interface = UserInterface()

    def autoparse(self):
        if self.auto_parse and self.file_handler.delimiter and (
                self.file_handler.is_simple_file(PATTERN_TEL_PASS, self.file_handler.file_path)):
            self.file_handler.get_keys('1=tel, 2=password')
            self.handler_folders.current_folder.all_files_status.add('parse')
            self.file_handler.num_columns = 1
            console.print('[cyan]' + 'Автопарсинг tel password')
            return True
        elif self.auto_parse and self.file_handler.delimiter and (
                self.file_handler.is_simple_file(PATTERN_USERMAIL_USERNAME_PASS, self.file_handler.file_path)):
            self.file_handler.get_keys(f'1=user_mail_name, 2=password')
            self.handler_folders.current_folder.all_files_status.add('parse')
            self.file_handler.num_columns = 1
            console.print('[cyan]' + f'Автопарсинг umn password')
            return True
        elif self.auto_parse and self.file_handler.delimiter and ('1:Anonymous:::' in self.file_handler.reader.open().readline()):
            self.file_handler.get_keys(f'1=uid, 2=un, 3=ip, 4=um, 5=p')
            self.handler_folders.current_folder.all_files_status.add('parse')
            self.file_handler.num_columns = 4
            console.print('[cyan]' + f'Автопарсинг uid un ip um pass')
            return True
        else:
            return False

    def rehandle_file_parameters(self):
        """
        Получение параметров файла: разделитель, количество столбцов, название столбцов
        @return:
        """
        self.interface.show_file(self.file_handler.reader)
        self.file_handler.handle_file()
        self.interface.show_delimiter(self.file_handler.delimiter)
        self.interface.show_num_columns(self.file_handler.num_columns + 1)

    def manual_parsing_menu(self):
        """
        Ручной парсинг
        @return:
        """
        menu = True
        while menu:
            mode = self.interface.ask_mode_handle()
            if mode == 'jp':
                return mode
            mode = self.handler_mode(mode)
            if mode in ['p', 'l', 'e', 't', 'jp']:
                return mode

            self.file_handler.get_column_names(self.full_auto)
            self.interface.show_num_columns(self.file_handler.num_columns + 1)
            _init_cols_keys = self.file_handler.column_names

            while True:
                self.file_handler.num_columns = self.interface.ask_num_cols(self.file_handler.num_columns)
                if self.file_handler.num_columns != -1:
                    menu = False
                else:
                    break
                _cols_keys = self.interface.ask_cols_keys(self.file_handler.column_names)
                if not _cols_keys:
                    self.file_handler.column_names = ''
                    _init_cols_keys = ''
                    continue
                else:
                    self.file_handler.column_names = _cols_keys
                try:
                    self.file_handler.get_keys()
                except Exception as ex:
                    print(f'Ошибка в ключах: {ex}')
                    continue
                max_key = max(self.file_handler.keys, key=lambda x: int(x[0]))
                if not max_key:
                    continue
                self.file_handler.skip = self.interface.ask_skip_lines(self.file_handler.skip)
                if (self.file_handler.num_columns + 1) >= int(max_key[0]) and self.file_handler.skip != -1:
                    break
                self.file_handler.column_names = _init_cols_keys

    def handler_mode(self, input_mode):
        mode = input_mode
        while True:
            if mode == 'p':
                self.handler_folders.current_folder.all_files_status.add('pass')
                self.handler_folders.skip_folder()
                return mode
            elif mode == 'l':
                self.handler_folders.current_folder.all_files_status.add('trash')
                return mode
            elif mode == 'o':
                # Открыть в EmEditor
                subprocess.run(f'Emeditor "{self.file_handler.file_path}"')
                self.interface.pause()
                self.rehandle_file_parameters()
            elif mode == 'n':
                # Открыть в Notepad++
                subprocess.run(f'notepad++ "{self.file_handler.file_path}"')
                self.rehandle_file_parameters()
            elif mode == 'd':
                self.file_handler.delimiter = self.interface.ask_delimiter()
                self.file_handler.get_num_columns()
            elif mode == 'e':
                # Перенести папку в ERROR
                self.handler_folders.current_folder.all_files_status.add('error')
                try:
                    self.file_handler.reader.close()
                    self.handler_folders.skip_folder(move_to='Error')
                    return mode
                except Exception as ex:
                    console.print(f'[magenta]Не могу переместить[/magenta]: "[red]{ex}[/red]"')
                    answer = Prompt.ask(f"[green]Если все ОК нажмите Enter", choices=['y', 'n'], default='y')
                    if answer == 'y':
                        mode = 'p'
                        return mode
                    raise ex
            elif mode == 't':
                try:
                    self.file_handler.reader.close()
                    self.handler_folders.current_folder.all_files_status.add('trash')
                    self.handler_folders.skip_folder(move_to='Trash')
                    return mode
                except Exception as ex:
                    console.print(f'[magenta]Не могу переместить[/magenta]: "[red]{ex}[/red]"')
                    answer = Prompt.ask(f"[green]Если все ОК нажмите Enter", choices=['y', 'n'], default='y')
                    if answer == 'y':
                        mode = 'p'
                        return mode
                    raise ex
            elif mode == 'start':
                self.handler_folders.current_folder.all_files_status.add('parse')
                break
            mode = self.interface.ask_mode_handle()
            if mode in ('jp', ):
                break
        return mode

    def parsing_file(self):
        mode = ''
        self.rehandle_file_parameters()
        if not self.auto_parse or self.file_handler.num_columns == 0 or not self.autoparse():
            if self.full_auto:
                mode = 'p'
                return mode
            mode = self.manual_parsing_menu()
            if mode in ['l', 'p', 't', 'e', 'jp']:
                return mode

        self.file_handler.parse_file(self.daemon)

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

    def convert_json(self, file_path) -> str:
        """Запускает конвертор JSON"""
        convertor = ConvertorJSON(file=file_path)
        converted_file = convertor.run()
        return converted_file

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
                    
                    self.file_handler = FileHandler(file, self.writer_data)
                    # Отлов ошибок для непрерывания full_auto
                    try:
                        self.interface.show_left_dirs(self.handler_folders.left_dirs)
                        self.interface.show_left_files(dir.left_files)
                        mode = self.parsing_file()
                        if mode == 'jp':
                            converted_file = self.convert_json(file)
                            if not converted_file:
                                mode = 'l'
                            else:
                                dir.insert_in_done_parsed_file(file)
                                file = converted_file
                                self.file_handler.reader = Reader(converted_file)
                                mode = self.parsing_file()
                    except Exception as e:
                        if self.full_auto:
                            mode = 'p'
                        else:
                            if not Confirm.ask(f'Ошибка при парсинге файла [magenta]{file.name}[/], пропустить его?'):
                                raise e
                            else:
                                continue
                    if mode in ['p', 't', 'e']:
                        break
                    if not self.daemon:
                        dir.insert_in_done_parsed_file(file)

                # Определение условий
                command_path = os.path.join(dir.path, '_command_.txt')
                is_other_command = os.path.getsize(command_path) > 2 if os.path.exists(command_path) else True
                all_trash = self.handler_folders.current_folder.all_files_status == {'trash'}
                dir_not_skip = self.handler_folders.current_folder.status != DirStatus.SKIP

                # Если все файлы пропущены, статус папки не SKIP и нет других распарсенных файлов, то в трэш
                if all_trash and dir_not_skip and is_other_command:
                    try:
                        self.file_handler.reader.close()
                        self.handler_folders.skip_folder(move_to='Trash')
                    except Exception as ex:
                        console.print(f'[magenta]Не могу переместить[/magenta]: "[red]{ex}[/red]"')
                        answer = Prompt.ask(f"[green]Если все ОК нажмите Enter", choices=['y', 'n'], default='y')
                        if answer != 'y':
                            raise ex
                        break
                if self.file_handler:
                    self.file_handler.writer.finish()
                    status_is_parse = self.handler_folders.current_folder.status == DirStatus.PARSE
                    files_status_contains_parse = 'parse' in self.handler_folders.current_folder.all_files_status
                    if status_is_parse and files_status_contains_parse:
                        dir.write_commands(self.file_handler.writer.commands)
                        self.handler_folders.done_folder()
            else:
                self.interface.print_dirs_status(str(dir.path), dir.status.value)
