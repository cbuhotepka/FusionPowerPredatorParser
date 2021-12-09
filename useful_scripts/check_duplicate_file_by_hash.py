import difflib
import hashlib
import os
from itertools import permutations

DISK = 'S'

class Directory:

    def __init__(self, path):
        self._path = path
        self._files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                self._files.append(self._md5(os.path.join(root, file)))

    def _md5(self, path: str):
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def __mod__(self, other: "Directory"):
        matcher = difflib.SequenceMatcher(None, self._files, other._files)
        return matcher.ratio()


# drc1 = Directory('matrix')
# drc2 = Directory('.idea')
# print(drc1 % drc2)

for i in os.listdir(f'{DISK}://Source/db'):
    if len(os.listdir(f'{DISK}://Source/db/{i}')) > 1:
        dirs = []
        double_dirs = set()
        for dir in os.listdir(f'{DISK}://Source/db/{i}'):
            dirs.append(Directory(f'{DISK}://Source/db/{i}/{dir}'))

       # print(dirs)
        for d1, d2 in permutations(dirs, 2):
            if d1 % d2 > 0.49 and (d2, d1) not in double_dirs:
                double_dirs.add((d1, d2))
                print(d1._path, d2._path)