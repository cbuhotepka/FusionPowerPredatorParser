import hashlib
from pathlib import Path

BUF_SIZE = 65536  # lets read stuff in 64kb chunks!


def get_hash(file: Path):
    """Получение хэша файла"""
    md5 = hashlib.md5()
    # sha1 = hashlib.sha1()

    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            # sha1.update(data)
    return md5.hexdigest()
