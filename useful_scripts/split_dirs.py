import os
import shutil
import time
from pathlib import Path
from typing import Generator

from rich.console import Console
from rich.prompt import Prompt

import logging

PD = 'E'
console = Console()

TYPE_BASE = ''

log = logging.getLogger(__name__)


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
            if TYPE_BASE == 'db' and os.path.exists(base_dir) and not os.listdir(base_dir):
                log.debug(f'Папка пуста.\n Удаляю -> {base_dir}')
                console.print(f"[yellow]Папка пуста!.\n Удаляю -> {base_dir}")
                shutil.rmtree(base_dir)
    except OSError as ex:
        log.debug(f'Ошибка перемещения {ex}')
        console.print(f"[bold red]{src_dir} - Не могу переместить!")
    finally:
        log.debug('-' * 30)
        log.debug(' ')


def start_split(all_dirs: Generator):
    # Итерируемся по каталогам
    dirs_counter = 1
    dir_number = 1
    for dir in all_dirs:
        if TYPE_BASE == 'db':
            base_dir = os.path.join(*Path(dir.absolute()).parts[:6])
            base_name = Path(base_dir).parts[-1]
            dest_path = os.path.join(DESTINATION, str(dir_number), base_name)
        else:
            # base_dir = os.path.join(*Path(dir.absolute()).parts[:5])
            base_dir = None
            dest_path = os.path.join(DESTINATION, str(dir_number))
        try:
            path_to_dir = str(dir.absolute())
            move_dir(base_dir, path_to_dir, dest_path)
            console.print(f"[bold green]{dir} - moved!")
            log.info(f"Moved dir: {dir}")
        except:
            console.print(f"[bold red]{dir} - not moved!")
            log.error(f"Can't move dir: {dir}")
        if dirs_counter == SIZE_DIR:
            dir_number += 1
            dirs_counter = 0
        dirs_counter += 1


def start():
    if TYPE_BASE == 'db':
        iter_dirs = iter_for_db(START_PATH)
    else:
        iter_dirs = iter_for_combo(START_PATH)
    start_split(iter_dirs)


if __name__ == '__main__':
    TYPE_BASE = Prompt.ask('Тип папки', choices=['combo', 'db'])
    log.setLevel('DEBUG')
    START_PATH = os.path.join(f'{PD}:\\errors_do_not_touch\\Sorted\\XLS', TYPE_BASE)
    DESTINATION = os.path.join(f'{PD}:\\errors_do_not_touch\\Sorted\\XLS\\Split\\', TYPE_BASE)
    SIZE_DIR = 25
    file_handler = logging.FileHandler(filename=os.path.join(START_PATH, 'splitting.log'), encoding='utf-8')
    log.addHandler(file_handler)
    start()
