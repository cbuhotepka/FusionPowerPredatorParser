import math
from pathlib import Path

from chardet import UniversalDetector

from .filters import filter_end_symbol
from .validators import validate_http_https, validate_repeat_one_character_all_line

MIDDLEWARE = [
    filter_end_symbol,
    validate_http_https,
    # validate_repeat_one_character_all_line

]


class Reader:
    _MIDDLEWARE_LIST = MIDDLEWARE
    _NUM_LINES_FOR_CHECK_ENCODING = 10_000

    def __init__(self, path: str, encoding=None, skip=0):

        self._path = Path(path)
        self.file_path = path
        self._check_path()
        _encoding = encoding or self._encoding
        self._file = self._path.open(encoding=_encoding)
        self._skip_rows(skip)

    def readline(self):
        try:
            _line = self._readline()
            _res_line = self._swipe_by_list_middleware(_line)
        except StopIteration:
            _res_line = None
        return _res_line

    def _readline(self):
        _line = self.fix_nulls(self._file, hit=1)
        return next(_line)

    def _skip_rows(self, skip: int):
        for _ in range(skip):
            self.readline()

    @staticmethod
    def fix_nulls(f, hit=math.inf):
        if f.mode == 'rb':
            count = 0
            while count <= hit:
                try:
                    s = f.readline()
                    if not s:
                        break
                    line = s.replace(b'\0', b'').replace(b'\r', b'')
                    line = line.decode('utf-8')
                    # print(line)
                except UnicodeDecodeError as e:
                    # print(e)
                    continue
                count += 1
                yield line
        elif f.mode == 'r':
            count = 0
            while count <= hit:
                try:
                    s = f.readline()
                except UnicodeDecodeError as e:
                    continue
                if not s:
                    break
                line = s.replace('\0', '')
                count += 1
                yield line
        return None

    @property
    def _encoding(self):
        _detector = UniversalDetector()
        with self._path.open(mode='rb') as fh:
            for line in fh.readlines(self._NUM_LINES_FOR_CHECK_ENCODING):
                _detector.feed(line)
                if _detector.done:
                    break
            _detector.close()
        return _detector.result['encoding']

    def _swipe_by_list_middleware(self, line):
        _new_line = line

        # Прогон строки по списку функций, чтобы вернуть чистую строку
        for func in self._MIDDLEWARE_LIST:
            _new_line = func(_new_line)
            if not _new_line:
                break

        return _new_line

    def _check_path(self):
        if not self._path.exists():
            raise ValueError(f'Файл {self._path} не найден.')

        if not self._path.is_file():
            raise ValueError(f'{self._path} является папкой.')

    def __enter__(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        _line = self._readline()
        _result_line = self._swipe_by_list_middleware(_line)
        return _result_line

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()
