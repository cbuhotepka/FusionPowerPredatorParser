import os
import logging
from rich.console import Console

from useful_scripts.file_hasher import get_hash

console = Console()

log = logging.getLogger(__name__)
f_handler = logging.FileHandler(f'{__name__}.log')
c_handler = logging.StreamHandler()
log.addHandler(f_handler)
log.addHandler(c_handler)

START_PATH = 'S:\\Source\\db'


def get_base():
    """Генератор по базам"""
    for root, base_list, _ in os.walk(START_PATH):
        for base in base_list:
            log.debug(f"Check base -> {root + base}")
            yield base
        break


def get_item(base):
    """Генератор item"""
    for root, items, _ in os.walk(base):
        for item in items:
            log.debug(f"Check base -> {root + item}")
            yield base
        break


def get_file(base_path: str) -> str:
    """Генератор файлов в базе"""
    for item, dirs, files in os.walk(base_path):
        for file in files:
            if file not in ['readme.txt']:
                log.debug(f'return {item + file}')
                yield item + file


def check_base(base_hashes: list):
    if not base_hashes or len(base_hashes) == 1:
        return False
    for base_hash in base_hashes:
        for item_hashes in base_hashes[1:]:
            if base_hash == item_hashes:
                log.debug()
                return True


def run():
    for base in get_base():
        base_hashes = []
        for item in get_item(base):
            item_hashes = set()
            for file in get_file(item):
                hash = get_hash(file)
                item_hashes.add(hash)
            base_hashes.append(item_hashes)



if __name__ == '__main__':
    run()