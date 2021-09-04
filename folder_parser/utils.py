from chardet.universaldetector import UniversalDetector
from .store import BANNED_SYMBOL


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

def is_escape_file(file_name: str):
    file_name = file_name.lower()
    return any(
        file_name.startswith('_'),
        file_name.endswith('_rewrite.txt'),
        file_name.endswith('.rewrite'),
        file_name == 'readme.txt',
    )