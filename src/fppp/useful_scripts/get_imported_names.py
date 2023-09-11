import datetime
import os
import re
import time
from pathlib import Path

from chardet import UniversalDetector

ROOT_PATH = 'Z:/'


BANNED_SYMBOL = ['Ð', 'œ', '\x9d', 'ž', '\x90', '˜', '—', '°', '±', 'Ñ', 'ƒ', '³', '¾', '\x81', '‡', 'µ', 'º']
BANNED_SYMBOL += ['¡', 'Â', 'š', '²', 'ˆ', '¿', '§', '•', '¥', '¯', '®', '›', '¦', 'ð', 'Ÿ', '¹', 'â', '‹', 'Œ', '·']


def get_encoding_file(path):
    detector = UniversalDetector()
    with open(path, 'rb') as fh:
        for line in fh.readlines(10000):
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']


def check_bad_symbol(string: str):
    for ch in BANNED_SYMBOL:
        if ch in string:
            return False
    return True


class Dir:
    def __init__(self, path, base_type):
        self.path = path if isinstance(path, Path) else Path(path)
        self.name = self.path.name
        self.base_type = base_type
        self.base_info = self._get_base_info()

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
        if check_bad_symbol(self.path.absolute().parent.name):
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
        encoding = get_encoding_file(path_to_readme) or 'utf-8'
        try:
            readme_string = open(os.path.join(self.path, 'readme.txt'), encoding=encoding).readlines()
        except:
            readme_string = open(os.path.join(self.path, 'readme.txt'), encoding='utf-8').readlines()
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


class NamesGetter:
    def __init__(self, user_number: int):
        self.user_number = f'blitz{user_number}'
        self.path_imported = os.path.join(ROOT_PATH, self.user_number, 'Imported')

    def run(self):
        self.iterate_dirs()

    def iterate_dirs(self):
        for base_type in ['db', 'combo']:
            for folder in self._get_dirs(base_type):
                directory = Dir(path=folder, base_type=base_type)
                print(f"'{directory.base_info['name']}',")

    def _get_dirs(self, base_type: str) -> str:
        path = os.path.join(self.path_imported, base_type)
        for item in os.listdir(path):
            if not os.path.isfile(os.path.join(path, item)):
                yield str(os.path.join(path, item))


if __name__ == '__main__':
    user_number = input('Enter user number: ')
    getter = NamesGetter(int(user_number))
    getter.run()
