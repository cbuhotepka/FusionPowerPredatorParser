import json
import re
from reader.reader import Reader
from validator.hash_identifer import identify_hashes


class Extractor:

    def __init__(self):
        self._data = dict()
        self._handlers = {
            'usermail': self._usermail,
            'username': self._username,
            'hash': self._hash,
            'tel': self._tel,
            'ipaddress': self._ip,
            'address': self._address,
        }

    def run(self, path, target_names: list, delimiter=','):
        with Reader(path, encoding='utf-8') as rf, open(result_path := path + '_extracted.json', 'w') as wf:
            for line in rf:
                _data = {tg: [] for tg in target_names}
                for col in line.split(delimiter):
                    for tg in target_names:
                        _match = self._handlers[tg](col)
                        if _match:
                            _data[tg].append(_match)
                wf.write(json.dumps(_data) + '\n')
        return result_path

    def _username(self, value: str):
        if m := re.match(r"^[^|/\\\[\]\(\):;,]{3,16}$", value.strip('"\t ')) and value.strip(
                '"\t ') not in self.domains:
            return m.group()
        return dict()

    def _usermail(self, value: str):
        if m := re.match(r"[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5}", value.strip('"\t\' ')):
            return m.group()
        return dict()

    def _hash(self, value: str):
        return self._get_hash_type(value)

    def _tel(self, value: str):
        v = value.strip('"\t\' ')
        if m := re.match(r'[+]?[\d\.\s\(]{2,}[_\-]?\d+[_\-]?[\d\.\)\s]+', v):
            if not re.search(r'(\d{4}|\d{2}|\d{1})-(\d{4}|\d{2}|\d{1})-(\d{4}|\d{2}|\d{1})', v):
                return m.group()
        return dict()

    def _ip(self, value: str):
        pattern_ip = r'([2][0-5][(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' \
                     r'\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
        if m := re.match(pattern_ip, value.strip('"')):
            return m.group()
        return dict()

    def _address(self, value: str):
        if m := re.match(r'(?:\s*([\w\d\.]+\s+){3,}\s*)', value.strip('"\t\' ')):
            return m.group()
        return dict()

    def _get_hash_type(self, value):
        # for pandas nan
        if str(value) == 'nan' or value == None:
            return ''
        algorithms = identify_hashes(value)
        return algorithms[0] if algorithms else ''


class Handler:

    def __init__(self, regex: str, name: str):
        self._regex = re.compile(regex)
        self._name = name

    def find(self, s) -> dict:
        _match = self._regex.findall(s)
        print(_match)
        _s = [i[0] if type(i) is tuple else i for i in _match]
        return {self._name: _s}


extractor = Extractor()

if __name__ == '__main__':
    path = input('path >>> ')
    target_names = input('target names (through a space) >>> ')
    delimiter = input('delimiter >>> ')
    extractor.run(path, target_names.split(), delimiter)
