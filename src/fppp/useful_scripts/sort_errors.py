import os
import shutil
import time
from pathlib import Path
from typing import Generator
from py_dotenv import read_dotenv

from rich.console import Console
from rich.prompt import Prompt

import logging
from ..config import config

PD = config['PARSER']['local_drive']
SD = config['PARSER']['remote_drive']

console = Console()

TYPE_BASE = ''

log = logging.getLogger(__name__)


# logging.basicConfig(filename='sorted_debug.log', encoding='utf-8', level=logging.DEBUG)


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


def move_dir(base_dir, src_dir, dest_path):
    if not os.path.exists(dest_path):
        log.debug(f'Создание папок {dest_path}')
        os.makedirs(dest_path, exist_ok=True)
    try:
        log.debug(f'Перемещение {src_dir} -> {dest_path}')
        with console.status('[bold blue]Перемещение папки...', spinner='point', spinner_style="bold blue"):
            shutil.move(src_dir, dest_path)
            dir_to_delete = Path(base_dir).parent
            if os.path.exists(dir_to_delete) and not os.listdir(dir_to_delete):
                log.debug(f'Папка пуста.\n Удаляю -> {dir_to_delete}')
                console.print(f"[yellow]Папка пуста!.\n Удаляю -> {dir_to_delete}")
                shutil.rmtree(dir_to_delete)
    except OSError as ex:
        log.debug(f'Ошибка перемещения {ex}')
        console.print(f"[bold red]{src_dir} - Не могу переместить!")
    finally:
        log.debug('-' * 30)
        log.debug(' ')


def start_check(all_dirs: Generator):
    # Итерируемся по каталогам
    done_check_path = os.path.join(START_PATH, 'check_complete.txt')

    for dir in all_dirs:
        if TYPE_BASE == 'db':
            base_dir = os.path.join(*Path(dir.absolute()).parts[:5])
        else:
            base_dir = os.path.join(*Path(dir.absolute()).parts[:4])
        # (1) - Инициализация папки
        path_to_dir = str(dir.absolute())
        all_files = get_all_files_in_dir(path_to_dir)
        log.debug(f'>>>\nПроверка папки -> {path_to_dir}')
        if not all_files:
            console.print(f"[bold red]{path_to_dir} - Папка пуста")
            log.debug(f'---\nПапак пуста -> {path_to_dir}\n---')
            continue
        console.print(f"[bold cyan]{path_to_dir}")
        console.print(f"[bold green]--Файлов в папке -> {len(all_files)}")
        log.debug(f"--Файлов в папке -> {len(all_files)}")

        extensions = get_extensions(all_files)
        log.debug(f'Полученные расширения --> {extensions}')
        console.print(f"[bold cyan]Полученные расширения --> {extensions}'")
        type_files = get_type(extensions)
        # if type_files == 'MIXED':
        #     console.print(f"[bold red]{path_to_dir} - Mixed")
        #     log.debug(f'Папка Mixed!!\n\n')
        #     continue
        # else:
        if TYPE_BASE == 'db':
            base_name = Path(base_dir).parts[-2]
            dest_path = os.path.join(DESTINATION, type_files, TYPE_BASE, base_name)
        else:
            dest_path = os.path.join(DESTINATION, type_files, TYPE_BASE)
        move_dir(base_dir, path_to_dir, dest_path)


def get_extensions(all_files: list) -> set:
    # log.debug('\n->\nПроверка расширений....')
    # log.debug(f'all_files -> {all_files}')
    all_extension = set()
    for file in all_files:
        # log.debug(f'file -> {file}')
        suffix = file.suffix.lower()
        # log.debug(f'suffix -> {suffix}')
        all_extension.add(file.suffix.lower())
    return all_extension


def get_all_files_in_dir(path_to_dir):
    # Сбор всех файлов с папки
    all_files: list[Path] = []
    for root, dirs, files in os.walk(path_to_dir):
        # log.debug(f'Список файлов -> {files}')
        files = list(filter(lambda x: x != 'readme.txt', files))
        all_files.extend([Path(os.path.join(root, f)) for f in files])
    return all_files


def get_type(extensions: set) -> str:
    """получения типа базы"""
    ALL_TYPES = {
        '.txt': 'CSV',
        '.csv': 'CSV',
        '.tsv': 'CSV',
        '.xls': 'XLS',
        '.xlsx': 'XLS',
        '.dat': 'CRONOS',
        '.tad': 'CRONOS',
        '.sql': 'SQL',
        '.json': 'JSON',
        '.xml': 'XML',
        '.pdf': 'PDF',
        '.zip': 'ARCH',
        '.rar': 'ARCH',
        '.7z': 'ARCH',
        '.tgz': 'ARCH',
        '.gzip': 'ARCH',
        '.gz': 'ARCH',
    }
    types = set()
    for ext in extensions:
        if type_ := ALL_TYPES.get(ext, None):
            types.add(type_)
        else:
            return 'MIXED'
    if len(types) > 1:
        return 'MIXED'
    else:
        log.debug(f'Type base -> {types}')
        return types.pop()


def start():
    if TYPE_BASE == 'db':
        iter_dirs = iter_for_db(START_PATH)
    else:
        iter_dirs = iter_for_combo(START_PATH)
    start_check(iter_dirs)


def main():
    global START_PATH, TYPE_BASE, DESTINATION, file_handler, log
    TYPE_BASE = Prompt.ask('Тип папки', choices=['combo', 'db'])
    log.setLevel('DEBUG')
    START_PATH = os.path.join(f'{SD}:\\Error', TYPE_BASE)
    DESTINATION = os.path.join(f'{SD}:\\sorted_error\\')
    file_handler = logging.FileHandler(filename=os.path.join(START_PATH, 'sorting.log'), encoding='utf-8')
    log.addHandler(file_handler)
    start()


if __name__ == '__main__':
    main()
