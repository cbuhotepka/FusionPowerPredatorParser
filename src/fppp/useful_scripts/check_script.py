import os
import re
import time
from pathlib import Path
from typing import Generator
import subprocess

from rich.console import Console
from rich.prompt import Prompt
import json
import utils

from store import ASSERT_NAME
from ..config import config

user = config['CLICKHOUSE']['username']
password = config['CLICKHOUSE']['password']
PD = config['PARSER']['remote_drive']

console = Console()

TYPE_BASE = ''
gl_num_columns = None


class CommandData:

    def __init__(self, date, name, source):
        self.user = user
        self.password = password
        self.date = date
        self.name = name
        self.source = source
        self.file = None
        self.cols = None
        self.delimiter = None
        self.algorithm = None


def start(auto_parse, full_auto):
    start_path = os.path.join(f'{PD}:\\', 'Source', TYPE_BASE)
    if TYPE_BASE == 'db':
        iter_dirs = iter_for_db(start_path)
    else:
        iter_dirs = iter_for_combo(start_path)
    start_check(iter_dirs, auto_parse, full_auto)


def iter_for_db(start_path):
    parsing_complete = get_list_dirs_for_pass(start_path)

    _counter = len(os.listdir(start_path))
    for root_name in os.listdir(start_path):
        _counter -= 1
        print()
        console.print(f"[bold green]Папок осталось {_counter}")
        if not os.path.isdir(os.path.join(start_path, root_name)):
            continue
        for item_name in os.listdir(os.path.join(start_path, root_name)):
            item = Path(os.path.join(start_path, root_name, item_name))
            if item.is_dir():
                if str(item.absolute()) in parsing_complete:
                    console.print(f'[bold yellow]{item.absolute()}')
                else:
                    console.print(f'[bold green]{item.absolute()}')
                    yield item
            else:
                continue


def iter_for_combo(start_path):
    parsing_complete = get_list_dirs_for_pass(start_path)

    # Генератор, возвращает папку в каталоге ~/Source/combo
    _counter = len(os.listdir(start_path))
    for p in os.listdir(start_path):
        item = Path(os.path.join(start_path, p))
        if item.is_dir():
            _counter -= 1
            print()
            console.print(f"[bold green]Папок осталось {_counter}")
            if str(item.absolute()) in parsing_complete:
                console.print(f'[bold green]{item.absolute()}')
                continue
            yield item


def get_list_dirs_for_pass(path):
    if os.path.exists(os.path.join(path, 'check_complete.txt')):
        parsing_complete = Path(os.path.join(path, 'check_complete.txt')).open(encoding='utf-8').readlines()
        parsing_complete = list(map(lambda x: x.replace('\n', ''), parsing_complete))
    else:
        parsing_complete = []

    return parsing_complete


def start_check(all_dirs: Generator, auto_parse, full_auto):
    # Итерируемся по каталогам
    path_to_type = Path(f'C:\\Source\\{TYPE_BASE}')
    done_check_path = os.path.join(path_to_type, 'check_complete.txt')

    for dir in all_dirs:
        if TYPE_BASE == 'db':
            base_dir = os.path.join(*Path(dir.absolute()).parts[:5])
        else:
            base_dir = os.path.join(*Path(dir.absolute()).parts[:4])
        command_data_change = False
        done_check_file = open(done_check_path, 'a', encoding='utf-8')
        # (1) - Инициализация папки
        path_to_dir = str(dir.absolute())
        all_files = get_all_files_in_dir(path_to_dir)
        if not all_files:
            console.print(f"[bold red]{path_to_dir} - Папка пуста")
            continue
        console.print(f"[bold cyan]{path_to_dir}")
        console.print(f"[bold green]--Файлов в папке -> {len(all_files)}")
        data_for_command = CommandData(**get_meta_for_db(dir, full_auto))
        # Обработака command файла
        command_file_path = os.path.join(base_dir, '_command_.txt')
        new_commands_data = get_old_command_data(command_file_path)
        left_files = len(all_files)
        for file in all_files:
            ready = False
            data_for_command.file = os.path.basename(file)
            while not ready:
                try:
                    # Показ первых строк
                    utils.show_file(file)
                    console.print('[cyan]' + str(file))
                    console.print(f"[bold green]**Файлов осталось-> {left_files}")
                    choice = Prompt.ask(f"[green]Что делаем?",
                                        choices=['g', 'e', 'd', 'o'],
                                        default='g')

                    if choice == 'g':
                        break
                    elif choice == 'd':
                        new_commands_data.pop(str(file), None)
                        command_data_change = True
                        break
                    elif choice == 'o':
                        subprocess.run(f'Emeditor {file}')
                        continue
                    else:
                        command_data_change = True
                        get_file_parameters(data_for_command, file)
                    new_commands_data[str(file)] = get_db_command(data_for_command)
                    pass_file = Prompt.ask('[yellow]Все правильно?', choices=['y', 'n'], default='y')
                    if pass_file == 'y':
                        ready = True
                except Exception as ex:
                    print(ex)
            left_files -= 1
        if command_data_change:
            update_command_file(command_file_path, new_commands_data)
        done_check_file.write(str(dir) + '\n')
        done_check_file.close()


def get_old_command_data(command_file_path: str) -> dict:
    console.print('[cyan]' + str(command_file_path))
    if not os.path.exists(command_file_path):
        Prompt.ask('[red]Отсутствует комманд файл. Продолжаем?', choices=['y', 'n'], default='y')
    elif os.path.getsize(command_file_path) == 0:
        Prompt.ask('[red]Комманд файл пуст. Продолжаем?', choices=['y', 'n'], default='y')
    else:
        with open(command_file_path, 'r', encoding='utf-8') as command_file:
            return json.load(command_file)
    return {}


def update_command_file(command_file_path, new_command_data: dict):
    rename_command_file(command_file_path)
    if not new_command_data:
        console.print('[red]Отсутствуют данные для записи в комманд!')
        return
    with open(command_file_path, 'w', encoding='utf-8') as command_file:
        json.dump(new_command_data, command_file)


def rename_command_file(command_file_path):
    console.print(f'[red]{command_file_path}')
    while True:
        try:
            os.rename(command_file_path, os.path.join(os.path.split(command_file_path)[0], 'OLD-command.txt'))
            break
        except OSError as er:
            console.print(f'[red]{er}')
            console.print(f'[red]{os.path.join(os.path.split(command_file_path)[0])}')
            answer = Prompt.ask('[red]Не могу перместить комманд файл. Повторить?', choices=['y', 'n'], default='y')
            if answer == 'n':
                return False
    return True


def get_file_parameters(data_for_command: CommandData, file: Path):
    data_for_command.delimiter = Prompt.ask('[magenta]Разделитель', choices=[':', ',', ';', r'\t', '|'])
    console.print('[cyan]' + str(file))
    data_for_command.cols = get_keys(Prompt.ask('[cyan]Колонки'))
    data_for_command.algorithm = Prompt.ask('[green]Какой алгоритм?', default='')


def get_meta_for_db(dir: Path, full_auto):
    path_to_readme = os.path.join(dir, 'readme.txt')
    source = ''
    date = ''

    if utils.check_bad_symbol(dir.absolute().parent.name):
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


def get_all_files_in_dir(path_to_dir):
    # Сбор всех файлов с папки
    all_files: list[Path] = []
    for root, dirs, files in os.walk(path_to_dir):
        files = list(filter(lambda x: x.endswith('.rewrite'), files))
        all_files.extend([Path(os.path.join(root, f)) for f in files])

    return all_files


def get_date_create(dir):
    path_to_dir_in_parsing_disk = str(dir.absolute())
    dates = []
    for item in get_all_files_in_dir(dir):
        file_path = os.path.join(path_to_dir_in_parsing_disk, item)
        if os.path.isfile(file_path):
            file = Path(file_path)
            create_date = file.stat().st_mtime
            str_date = time.ctime(create_date)
            date = time.strptime(str_date)
            y, m, d = date.tm_year, date.tm_mon, date.tm_mday
            y = y if not y < 10 else f'0{y}'
            m = m if not m < 10 else f'0{m}'
            d = d if not d < 10 else f'0{d}'
            dates.append(f'{y}-{m}-{d}')
    date = min(dates)
    return date


def get_keys(inp):
    """
    :param inp: "1=um, 3=un, 4=upp"
    :return: Строка с полными названиями колонок
    """

    args_inp = inp.split('_')  # [1=uai, 2=uai, 3=tel]
    key_res = []
    for arg in args_inp:
        if arg in list(ASSERT_NAME.keys()):
            key_res.append(ASSERT_NAME[arg])
        else:
            raise ValueError('Bad field name')
    return ','.join(key_res)


def get_db_command(data: CommandData) -> str:
    cmd = f"python3 fix.py" \
          f" --date {data.date}" \
          f" --delimiter" \
          f" '{data.delimiter}'" \
          f" --name '{data.name}'" \
          f" --source '{data.source}'" \
          f" --type database" \
          f" --user {data.user}" \
          f" --password {data.password}" \
          f" --database db_{data.user}" \
          f" --src '../files/{data.file}'" \
          f" --colsname '{data.cols}'" \
          f" --quotes"
    if data.algorithm:
        cmd += f" --algorithm '{data.algorithm}'"
    return cmd


if __name__ == '__main__':
    TYPE_BASE = Prompt.ask('Тип папки', choices=['combo', 'db'])
    start(False, False)
