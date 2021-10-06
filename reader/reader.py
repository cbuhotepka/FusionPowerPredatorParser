import math
from pathlib import Path

from chardet import UniversalDetector

from .filters import filter_end_symbol
from .validators import validate_http_https, validate_repeat_one_character_all_line

MIDDLEWARE = [
    filter_end_symbol,
    validate_http_https,
    validate_repeat_one_character_all_line

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
        self._fix_nulls_file_generator = self._fix_nulls(self._file)
        self._skip_rows(skip)

    def open(self, encoding=None, skip=0):
        _encoding = encoding or self._encoding
        self._file = self._path.open(encoding=_encoding, errors='replace')
        self._fix_nulls_file_generator = self._fix_nulls(self._file)
        self._skip_rows(skip)
        return self

    def readline(self):
        try:
            _line = self._readline()
            _res_line = self._swipe_by_list_middleware(_line)
        except StopIteration:
            _res_line = None
        return _res_line

    def _readline(self):
        return next(self._fix_nulls_file_generator)

    def _skip_rows(self, skip: int):
        for _ in range(skip):
            self.readline()
        return skip

    @staticmethod
    def _fix_nulls(f, hit=math.inf):
        while hit > 0:
            try:
                s = f.readline()
            except UnicodeDecodeError as e:
                continue
            if not s:
                break
            # line = s.replace('\0', '')
            line = s
            hit -= 1
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
        self.close()

    def close(self):
        self._file.close()
