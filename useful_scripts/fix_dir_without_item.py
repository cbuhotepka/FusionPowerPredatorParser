import logging
import os
import re
import shutil
import uuid
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)


def is_it_item(name: str):
    _pattern = '([a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12})|item\d+'
    logging.debug(name)
    return bool(re.match(_pattern, name))


def get_item_without_directory(path: str):
    _items_without_dir = []
    for item in os.listdir(path):
        _is_it_item = is_it_item(Path(item).name)
        logging.debug(_is_it_item)
        if not _is_it_item:
            _items_without_dir.append(item)
    return _items_without_dir


def fix_dir(db_path: str):
    items_without_dir = get_item_without_directory(db_path)
    if items_without_dir:
        new_dir = os.path.join(db_path, str(uuid.uuid4()))
        os.mkdir(new_dir)
        for item in items_without_dir:
            shutil.move(os.path.join(db_path, item), new_dir)


if __name__ == '__main__':
    base_path = input('Input db base path (*/1/db/) >>> ')
    for db_path in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, db_path)):
            fix_dir(os.path.join(base_path, db_path))
