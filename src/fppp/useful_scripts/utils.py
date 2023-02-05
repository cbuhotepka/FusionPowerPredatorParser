import math
import time

from chardet.universaldetector import UniversalDetector
from collections import Counter, OrderedDict

from rich.highlighter import RegexHighlighter
from rich.progress import Progress, track
from rich.prompt import Prompt
from rich.text import Text
from rich.theme import Theme

from Regex import regex_dict, rs
from hash_identifer import identify_hashes
import os
import shutil
import pandas
from pathlib import Path
import re
from rich.console import Console

from validator import validate_field as vf, get_hash_type, get_field_type
from normalize_col_names import normalize_col_names
from store import BANNED_SYMBOL, DELIMITERS, COLUMN_NAME_TRIGGERS, ASSERT_NAME, ALLOW_EXTENSION, DELETE_VALUES_LIST

import subprocess
import sys
import csv

from ..config import config

maxInt = sys.maxsize
while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)


class DelimiterHighlighter(RegexHighlighter):
    base_style = "text."
    highlights = [r"(?P<all>.)", r"(?P<delimiter>[,:;|])"]


theme = Theme({"text.delimiter": "bold red", "text.all": "yellow"})
console = Console()
console_for_show = Console(highlighter=DelimiterHighlighter(), theme=theme)

SD = config['PARSER']['local_drive']
PD = config['PARSER']['remote_drive']
FIXPY = config['FIXPY']['file_name']


def get_encoding_file(path):
    # return 'utf-8'
    detector = UniversalDetector()
    with open(path, 'rb') as fh:
        for line in fh.readlines(10000):
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding'] or 'utf-8'


def get_plain_files(files_paths):
    return files_paths


def get_db_command(**kwargs):
    data = kwargs
    data['name'] = data['name'].replace("'", '')
    data['source'] = data['source'].replace("'", '')

    cmd = f"python3 {FIXPY}" \
          f" --date {data['date']}" \
          f" --delimiter" \
          f" '{data['delimiter']}'" \
          f" --name '{data['name']}'" \
          f" --source '{data['source']}'" \
          f" --type database" \
          f" --user {data['user']}" \
          f" --password {data['password']}" \
          f" --database db_{data['user']}" \
          f" --src '../files/{data['file']}'" \
          f" --colsname '{data['cols']}" \
          f" --quotes"
    if data['algorithm']:
        cmd += f" --algorithm '{data['algorithm']}'"
    return cmd + '\n'


def get_combo_command(**kwargs):
    data = kwargs
    data['name'] = data['name'].replace("'", '')
    data['source'] = data['source'].replace("'", '')

    cmd = f"python3 {FIXPY}" \
          f" --user {data['user']}" \
          f" --password {data['password']}" \
          f" --database db_{data['user']}" \
          f" --date {data['date']}" \
          f" --delimiter" \
          f" '{data['delimiter']}'" \
          f" --name '{data['name']}'" \
          f" --source '{data['source']}'" \
          f" --type combo" \
          f" --src '../files/{data['file']}'" \
          f" --colsname '{','.join(data['cols'])}'" \
          f" --quotes"
    if data['algorithm']:
        cmd += f" --algorithm '{data['algorithm']}'"
    return cmd + '\n'


class HashManager:

    def get_type_hash(self, path):
        m = self.parse(path)
        occurence_count = Counter(m.values())
        if not occurence_count.values():
            return None
        return occurence_count.most_common(1)[0][0]

    def hash_type(self, word):
        algorithms = identify_hashes(word)
        return algorithms[0] if algorithms else None

    def parse(self, file):
        path = Path(file)
        if not path.is_file():
            raise TypeError("unknown path")

        hash_arr = {}
        c = 0
        with open(file, "r", encoding=get_encoding_file(file), errors='ignore') as f:
            for line in f.readlines():
                c += 1
                if c > 10000:
                    break
                for word in re.findall(r"[^\s:,]+", line):
                    hash = self.hash_type(word)
                    if hash:
                        hash_arr[word] = hash

        return hash_arr


manager = HashManager()


def show_file(file: Path):
    """Print 15 line from parsing file
    Args:
        file (Path): file for parsing
    """
    console_for_show.print(f'[bold magenta]{file.absolute()}')
    console_for_show.print("[magenta]" + '-' * 200, overflow='crop')
    encod = get_encoding_file(file.absolute())
    with file.open('r', encoding=encod) as f:
        for i, line in enumerate(fix_nulls(f, hit=15)):
            line_to_show = line[:1000] if len(line) > 3000 else line
            try:
                console_for_show.print(line_to_show, end='', )
            except:
                continue
    print('\n')


def get_column_names(file_path: Path, auto: bool, delimiter: str = None) -> str:
    """Get column names from first string of file
    Args:
        file_path (Path): parsing file
        auto (bool, optional): mode parsing auto or No
    Returns:
        _colsname (str): 1=un,2=upp,3=h or None
    """
    with file_path.open('r', encoding='utf-8') as f:
        column_names_line = None
        for i, line in enumerate(fix_nulls(f, hit=15)):

            # Finding line with column names
            if i < 6 and not column_names_line:
                _new_line = line.lower()
                for trigger in COLUMN_NAME_TRIGGERS:
                    if re.search(trigger, _new_line):
                        column_names_line = re.sub(r'\n$', '', line)
                        break
                    else:
                        column_names_line = ''
        # Printing and copying possible column names
        if column_names_line and not auto:
            _colsname = normalize_col_names(string=column_names_line, delimiter=delimiter)
            console.print(f'[magenta]Определены столбцы[/magenta]: "[green]{_colsname}[/green]"')
            _answer = Prompt.ask('[magenta]Все правильно?', choices=['y', 'n'], default='y')
            if _answer == 'y':
                return _colsname
        return None


def get_keys_short(inp):
    """
    :param inp: "1=um, 3=un, 4=upp"
    :return: Строка с полными названиями колонок
    """

    args_inp = inp.split(',')
    key_res = []
    args_inp = inp.split(',')  # [1=uai, 2=uai, 3=tel]
    key_res = []
    for arg in args_inp:
        arg = arg.strip()
        data_key = arg.split('=')
        if data_key[1] in list(ASSERT_NAME.keys()):
            key_res.append((data_key[0] + '=' + ASSERT_NAME[data_key[1]]))
        elif data_key[1] in list(ASSERT_NAME.values()):
            key_res.append((data_key[0] + '=' + data_key[1]))
        else:
            raise ValueError('Bad field name')
    return ','.join(key_res)


def get_keys(inp):
    """
    :param inp: "1=usermail, 3=username"
    :return: keys [(tuple)]: (, colsname_plain  Порядок для бд, ключи для fix.py
    """
    inp = get_keys_short(inp)
    args_inp = inp.split(',')
    key_res = []
    for arg in args_inp:
        arg = arg.strip()
        data_key = arg.split('=')
        key_res.append(data_key[1])
    colsname_plain = key_res[::]
    if 'user_additional_info' in colsname_plain:
        while colsname_plain.count('user_additional_info') > 0:
            colsname_plain.remove('user_additional_info')
        colsname_plain.append('user_additional_info')
    keys = [tuple(i.split('=')) for i in args_inp]
    return keys, colsname_plain


def write_to_complete(dir, type):
    with open(os.path.join(f'{PD}:\\', 'Source', type, 'parsing_complete.txt'), 'a', encoding='utf-8') as f:
        f.write("\n" + str(dir.absolute()))


def write_to_passed_dirs(dir, type):
    with open(os.path.join(f'{PD}:\\', 'Source', type, 'passed_dirs.txt'), 'a', encoding='utf-8') as f:
        f.write("\n" + str(dir.absolute()))


def move_to(dir, type_base, destination):
    # path_source = C:\Source\db\database\item1
    # path_source = C:\Source\combo\database
    path_source = str(dir)
    if not os.path.exists(path_source):
        print("Папка перемещена")
        return
    # base_source = S:\Source\db\database\item1
    base_source = path_source.replace(f'{PD}:', f'{SD}:')

    # basedir = C:\Source\db\database
    base_dir = os.path.join(*Path(path_source).parts[:4])

    if type_base == 'combo':
        # base = database
        base = Path(path_source).parts[3]

        # base_dest = S:\Error\combo
        base_dest = os.path.join(f'{SD}:\\', destination.capitalize(), type_base)

        # path_move = C:\Error\combo
        path_move = os.path.join(f'{PD}:\\', destination.capitalize(), type_base)

        # os.system("pause")
    else:
        # C:\Souce\db\database\item1
        # _database = item1
        base = Path(path_source).parts[4]
        # base = database
        _database = Path(path_source).parts[3]

        # path_move = C:\Error\db\database
        path_move = Path(os.path.join(f'{PD}:\\', destination.capitalize(), type_base, _database))

        # base_dest = S:\Error\db\database
        base_dest = os.path.join(f'{SD}:\\', destination.capitalize(), type_base, _database)

    os.makedirs(str(path_move), exist_ok=True)
    if os.path.exists(os.path.join(path_move, base)):
        shutil.rmtree(os.path.join(path_move, base))
    # Перемещение
    shutil.move(str(path_source), str(path_move))
    shutil.move(base_source, base_dest)
    # Чистка пустых папок
    if os.path.exists(base_dir) and not os.listdir(base_dir):
        shutil.rmtree(base_dir)
    _base_rm = os.path.join(*Path(base_source).parts[:4])
    if os.path.exists(_base_rm) and not os.listdir(_base_rm):
        shutil.rmtree(_base_rm)


def clean_from_avoided_delimiters(matched_list, delimiter):
    changing_pattern = {
        ':': ';', ';': ':',
        ',': '.', '.': ',',
        '	': ' ',
    }
    if delimiter in changing_pattern.keys():
        return [a.replace(delimiter, changing_pattern[delimiter]) for a in matched_list]
    return matched_list


def csv_write_2(path: Path, keys: list, colsnames, delimiter: str, skip: int, num_columns):
    """[summary]
     if re.match(r'(?<=[\t\s:;,])\B[A-Za-z\d\./\$=]{8,129}[^~&|!_;:\^@\s]\b(?=[\t\s:;,])', value):
    Args:
        path (Path): [description]
        keys [(tuple)]: [description]
        colsnames ([type]): [description]
        delimiter (str): [description]
        skip (int): [description]
    Returns:
        [type]: [description]
    """
    new_delimiter = ';' if delimiter in ['\t', '|'] else delimiter

    base_name = os.path.splitext(str(path.absolute()))[0]
    read_encoding = get_encoding_file(path.absolute())
    file_for_reading = path.open('r', newline="", encoding=read_encoding)
    files_to_writing = {}
    fixer = fix_nulls(file_for_reading)

    data_for_command = {}

    for _ in range(skip):
        try:
            next(fixer)
        except StopIteration:
            pass
    with console.status('[bold blue]Подсчет строк...', spinner='point', spinner_style="bold blue") as status:
        count_rows_in_file = get_count_rows(path, read_encoding)
        console_for_show.print(f'[yellow]Строк в файле: {count_rows_in_file}')
    columns_number = max(list(int(a[0]) for a in keys))
    handler_line = HandlerLine(keys, path, delimiter, num_columns, skip)
    for fields in track(handler_line.get_fields(), description='[bold blue]Парсинг файла...', total=count_rows_in_file):
        _cols_name = handler_line.get_cols_name()
        algorithm = ''
        _email = ''

        if 'hash' in _cols_name:
            algorithm = get_hash_type(fields[_cols_name.index('hash')]) or 'unknown'
        if 'usermail' in _cols_name:
            _email = '_email'

        main_string = f'{new_delimiter}'.join(fields)
        _writing_file_name = f'{base_name}{_email}_{algorithm}_rewrite.txt'
        if _writing_file_name not in data_for_command.keys():
            data_for_command[_writing_file_name] = tuple([_cols_name, algorithm])

        if _writing_file_name not in files_to_writing.keys():
            files_to_writing[_writing_file_name] = open(_writing_file_name, 'w', encoding='utf-8')
        files_to_writing[_writing_file_name].write(main_string + '\n')

    for key, f in files_to_writing.items():
        files_to_writing[key] = Path(f.name)
        f.close()
    file_for_reading.close()

    return data_for_command


def is_simple_file(pattern, file):
    result = 0
    encod = get_encoding_file(file.absolute())
    with file.open('r', encoding=encod) as read_file:
        for i, line in enumerate(fix_nulls(read_file, hit=25)):
            if i > 10 and re.match(pattern, line):
                result += 1
    if result > 5:
        return True
    return False


def cleaner_blank_of_line(input_string: str) -> str:
    clean = re.compile('|'.join(item for item in DELETE_VALUES_LIST))
    output_string = clean.sub("", input_string)
    return output_string


def is_email(value):
    if re.match(r'[\d\w]+[\w\d_\.+\-@]+@[\d\w]+[\w\d\.\-_]+\.[\w]{2,5}', value):
        return True
    return False


def validate_field(s, key):
    if not s:
        return False
    value = s.strip(' \t')
    # print(s, value)
    if key == 'hash':
        return bool(manager.hash_type(value))
    if key not in regex_dict:
        return True
    return bool(rs[key].search(value))


def check_file_on_wrapper(path, tag, delimiter):
    if not delimiter:
        return False
    with open(path, encoding=get_encoding_file(path), errors='ignore') as f:
        if tag == 'anonymous':
            for _ in range(5):
                if "1:Anonymous:::" in f.readline():
                    return True
        if tag == 'login:pass':
            using_password = set()
            using_password_count = 0
            n = 100
            err = 0
            valid_usermail_string_count = 0
            valid_username_string_count = 0
            for _ in range(n):
                s = f.readline().strip()
                if not s:
                    continue
                s = s.split(delimiter)
                if len(s) != 2:
                    err += 1
                    continue
                login, password = s[0], s[1].replace('\n', '')
                if not password or not (rs['userpass_plain'].search(password) or manager.hash_type(password)):
                    err += 1
                    continue
                if password in using_password:
                    using_password_count += 1
                    if using_password_count > 0.3 * n:
                        return False
                using_password.add(password)

                if rs['usermail'].search(login):
                    valid_usermail_string_count += 1
                elif rs['username'].search(login):
                    valid_username_string_count += 1
                else:
                    err += 1
            if valid_usermail_string_count > err + valid_username_string_count:
                return 'usermail'
            if valid_username_string_count > err + valid_usermail_string_count:
                return 'username'
        if tag == 'uid_usrn_ip_usrm_hash_salt':
            keys_name_regex_tab = r"userid\s+username\s+ipaddress\s+email\s+token\s+secret"
            # keys_name_regex_colon = r".*:.*:.*:.*:.*:.*[^:]$"
            keys_name_find = False
            err = 0
            for i in range(20):
                s = f.readline()
                if re.search(keys_name_regex_tab, s) and len(s.split('\t')) == 6:
                    return '\t', i + 1


def xlsx_to_txt(path):
    name = os.path.splitext(path)[0] + '.txt'
    with open(name, 'w', encoding=get_encoding_file(path), errors='ignore') as file:
        pandas.read_excel(path).to_csv(file, index=False)
    return name


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
            if line == '' or line == '\n' or line == '\r\n' or line == '\r':
                continue
            if re.match(r'^https?:.*', line, flags=re.IGNORECASE):
                continue
            count += 1
            yield line
    elif f.mode == 'r':
        count = 0
        while count <= hit:
            try:
                s = f.readline()
                if not s:
                    break
                line = s.replace('\0', '')
                # print(line)
            except UnicodeDecodeError as e:
                continue
            if line == '' or line == '\n' or line == '\r\n' or line == '\r':
                continue
            if re.match(r'^https?:.*', line, flags=re.IGNORECASE):
                continue
            count += 1
            yield line


def get_source_from_readme(readme: str, encod):
    _source = None
    _name = None
    if os.path.exists(readme) and open(readme, 'r', encoding=encod).read(1024):
        _readme_string = open(readme, encoding=encod).readlines()
        _name = _readme_string[0].replace("\n", "")
        for line in _readme_string:

            if re.match(r'https?://', line):
                _source = re.match(r'https?://[\w\d\-=\\/\._\?]+', line.replace("\n", "")).group(0)
                break
            elif re.match(r'OLD (D|C)', line):
                _source = re.match(r'OLD (D|C)[\w]+', line.replace("\n", "")).group(0)
                break
    if not _source:
        if re.match(r'.*Source[\\|/]combo[\\|/]', str(readme)):
            _source = 'OLD COMBOS'
        else:
            _source = 'OLD DATABASE'
    return _name, _source


def get_list_dirs_for_pass(path):
    passed_dirs = Path(os.path.join(path, 'passed_dirs.txt')).open(encoding='utf-8').readlines()
    passed_dirs = list(map(lambda x: x.strip(), passed_dirs))

    parsing_complete = Path(os.path.join(path, 'parsing_complete.txt')).open(encoding='utf-8').readlines()
    parsing_complete = list(map(lambda x: x.replace('\n', ''), parsing_complete))

    return parsing_complete, passed_dirs


def fix_file(path: Path):
    new_path = Path(os.path.splitext(str(path.absolute()))[0] + '_gotovo.txt')
    new_file = new_path.open('w', encoding='utf-8')
    with console.status('[bold blue]Ремонт файла...') as status:
        for i, s in enumerate(fix_nulls(path.open('r', encoding='utf-8'))):
            new_file.write(s)

            # if i % (abs(len(str(i)) - 2) + 1) == 0:
            #     status.update(f'[bold blue]Ремонт файла, обработано {i} строк')
    new_file.close()
    return new_path


def get_delimiter(path: Path):
    """
    Получение разделителя
    :param path: путь до csv
    :return: dialect
    """
    f = path.open('r', encoding='utf-8')
    try:
        return csv.Sniffer().sniff(''.join([i for i in fix_nulls(f, hit=20)]), delimiters=',:;\t').delimiter
    except csv.Error:
        return None


def get_all_files_in_dir(path_to_dir):
    # Сбор всех файлов с папки
    all_files: list[Path] = []
    for root, dirs, files in os.walk(path_to_dir):
        files = list(filter(lambda x: not x.startswith('_')
                                      and not x.endswith('_rewrite.txt')
                                      and not x.endswith('_bad_rows.txt')
                                      and not x.lower() == 'readme.txt'
                                      and not x.lower() == 'done_parse_file.txt'
                                      and not '_rewrite_' in x
                                      and not x.endswith('_gotovo.txt'), files))
        path_files: list[Path] = [Path(os.path.join(root, f)) for f in files]

        clean_files = []
        for p in path_files:
            clean_files.append(p)

        all_files += clean_files
    return all_files


def parsing_file(files):
    pass


def fix_row(gen, delimiter):
    """ Экранирование крайних кавычек перед разделителем в строке,
        дабы csv.reader не думал, что следующая строка относится к этой... балбес"""
    for line in gen:
        # yield re.sub(delimiter + r'["]([^"]+$)', delimiter + r"\"\1", line)
        yield re.sub(delimiter + r'["]([^"]+$)', delimiter + r'\"\1', line)


def check_bad_symbol(line):
    for ch in BANNED_SYMBOL:
        if ch in set(line):
            return False
    return True


def check_extension(file, type_base):
    error_extension = os.path.join(f'{PD}:\\Source', type_base, 'error_extension.txt')
    with open(error_extension, 'a', encoding='utf-8') as error_file:
        filename, extension = os.path.splitext(file)
        if extension.lower() in ALLOW_EXTENSION:
            return True
        error_file.write(str(file))
        error_file.write('\n')
        return False


def get_count_rows(file, encoding):
    with open(file, 'r', encoding=encoding or 'utf-8') as f:
        count = sum(1 for _ in fix_nulls(f))
    return count


def get_num_columns(file, delimiter):
    encod = get_encoding_file(file)
    _sum_delimiter = 0
    _sum_lines = 0

    pat = re.compile(f'{delimiter}')

    with open(file, 'r', encoding=encod or 'utf-8') as read_file:
        for i, line in enumerate(fix_nulls(read_file, hit=60)):
            if i > 10 and (line != '' or line != '\n'):
                line = re.sub(r'(\"[^\"]*?\")', '', line)
                _sum_delimiter += len(re.findall(pat, line))
                _sum_lines += 1

    if _sum_delimiter and _sum_lines:
        _result = _sum_delimiter // _sum_lines
        return _result
    return 0


class HandlerLine:

    def __init__(self, keys, path, delimiter, num_columns, skip):
        self.index_columns = []
        self.columns_name_index = OrderedDict()
        self.keys = keys
        self.path = path
        self.delimiter = delimiter
        self.num_columns = num_columns
        self.file = None
        self.bad_rows_file = None
        self.input_cols_names = []
        self.output_cols_names = []
        self.output_fields = []
        self.skip = skip

    def handler_line(self, line):
        self.split_line_to_fields()

    def handler_fields(self) -> list:
        index_umn = self.columns_name_index.get('user_mail_name')
        index_un = self.columns_name_index.get('username')
        index_um = self.columns_name_index.get('usermail')
        index_p = self.columns_name_index.get('password')
        index_h = self.columns_name_index.get('hash')
        index_ip = self.columns_name_index.get('ipaddress')
        index_upp = self.columns_name_index.get('userpass_plain')
        index_t = self.columns_name_index.get('tel')
        index_uai = self.columns_name_index.get('user_additional_info')
        for fields in self.split_line_to_fields():
            _result_fields = []
            new_fields = [fields[:]]
            self.output_cols_names = self.input_cols_names[:]
            if index_un is not None and index_um is not None:
                if self.is_usermail(new_fields[0][index_un]):
                    if new_fields[0][index_un] == new_fields[0][index_um]:
                        new_fields[0][index_un] = ''
                    else:
                        new_fields.append(new_fields[0])
                        new_fields[1][index_um] = new_fields[0][index_un]
                        new_fields[0][index_un] = ''
                        new_fields[1][index_un] = ''

                elif not self.is_username(new_fields[0][index_un]):
                    new_fields[0][index_un] = ''
            if index_umn is not None:
                _index = self.output_cols_names.index('user_mail_name')
                self.output_cols_names[_index] = 'usermail' if self.is_usermail(fields[index_umn]) else 'username'
                if self.output_cols_names[_index] == 'username' and not self.is_username(new_fields[0][index_umn]):
                    new_fields[0][index_umn] = ''
            if index_um is not None:
                if not self.is_usermail(new_fields[0][index_um]):
                    new_fields[0][index_um] = ''
                else:
                    new_fields[0][index_um] = self.get_usermail(new_fields[0][index_um])
            if index_un is not None:
                if not self.is_username(new_fields[0][index_un]):
                    new_fields[0][index_un] = ''
            if index_p is not None:
                _index = self.output_cols_names.index('password')
                self.output_cols_names[_index] = 'hash'
                if len(new_fields[0]) >= index_p + 1 and new_fields[0][index_p]:
                    algorithm = get_hash_type(new_fields[0][index_p]) or ''
                    if not algorithm:
                        self.output_cols_names[_index] = 'userpass_plain'
                else:
                    self.output_cols_names[_index] = 'userpass_plain'
            if index_t is not None:
                if not self.is_tel(new_fields[0][index_t]):
                    new_fields[0][index_t] = ''
            if index_ip is not None:
                if not self.is_ip(new_fields[0][index_ip]):
                    new_fields[0][index_ip] = ''

            if index_upp is not None:
                if not self.is_upp(new_fields[0][index_upp]):
                    new_fields[0][index_upp] = ''

            for _fields in new_fields:
                _result_fields.clear()
                for index in self.index_columns:
                    _result_fields.append(_fields[index])
                if index_uai:
                    add_info = "|".join(cleaner_blank_of_line(_fields[i]) for i in index_uai)
                    _result_fields.append(add_info)
                if len([x for x in _fields if x]) < 2:
                    continue
                yield _result_fields

    def is_username(self, value: str) -> bool:
        if re.match(r"^\w{,3}\.\w{2,3}$", value):
            return False
        if re.match(r"^[^|/\\\[\]\(\):;,]{4,16}$", value):
            return True
        return False

    def is_usermail(self, value: str) -> bool:
        if re.match(r"[\"\']*[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5}[\"\']*", value):
            return True
        return False

    def get_usermail(self, value: str) -> str:
        return re.search(r"[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5}", value).group(0)

    def is_upp(self, value: str) -> bool:
        if re.match(r"[\"\']*[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5}[\"\']*", value):
            return False
        return True

    def is_hash(self, value: str) -> bool:
        return get_hash_type(value)

    def username_or_usermail(self, value):
        _result = 'usermail' if rs['usermail'].search(value) else 'username'
        return _result

    def is_tel(self, value: str) -> bool:
        if re.match(r'[+]?[\d\.\s\(]{2,}[_\-]?\d+[_\-]?[\d\.\)\s]+', value.strip('"')):
            return True
        return False

    def is_ip(self, value: str) -> bool:
        pattern_ip = r'^([2][0-5][(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)' \
                     r'\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(pattern_ip, value.strip('"')):
            return True
        return False

    def split_line_to_fields(self):
        counter_lines = 0
        counter_bad_line = 0
        pattern = re.compile(f'^' +
                             f'(?:((?:\"[^\"]*?\")|(?:[^{self.delimiter}]*)){self.delimiter})' * self.num_columns +
                             f'((?:\"[^\"]*?\")|(?:[^{self.delimiter}]*))')
        pat = re.compile(f'{self.delimiter}')
        for line in fix_nulls(self.file):
            counter_lines += 1
            if counter_lines <= self.skip:
                continue
            line = re.sub(r'(\n$)|(\r$)', '', line)
            line = cleaner_blank_of_line(line)
            match = re.match(pattern, line)
            if not match:
                continue
            if not check_bad_symbol(line):
                counter_bad_line += 1
                self.bad_rows_file.write(line)
                self.bad_rows_file.write('\n')
                continue
            if len(match.groups()) != self.num_columns + 1:
                self.bad_rows_file.write(line)
                self.bad_rows_file.write('\n')
                continue
            _fields = list(match.groups())
            yield _fields

    def handler_keys(self):
        for item in sorted(self.keys, key=lambda i: i[0]):
            if item[1] != 'user_additional_info':
                self.columns_name_index[item[1]] = int(item[0]) - 1
                self.index_columns.append(int(item[0]) - 1)
                self.input_cols_names.append(item[1])
            else:
                self.columns_name_index.setdefault(item[1], [])
                self.columns_name_index[item[1]].extend([int(item[0]) - 1])
        if 'user_additional_info' in self.columns_name_index.keys():
            self.input_cols_names.append('user_additional_info')

    def get_fields(self) -> list:
        self.handler_keys()
        read_encoding = get_encoding_file(self.path.absolute())
        self.file = self.path.open('r', newline="", encoding=read_encoding)
        bad_rows_path = Path(os.path.splitext(str(self.path.absolute()))[0] + '_bad_rows.txt')
        self.bad_rows_file = bad_rows_path.open('w', encoding='utf-8')
        for output_fields in self.handler_fields():
            if len([item for item in output_fields if item]) < 2:
                continue
            yield output_fields
        self.bad_rows_file.close()

    def get_cols_name(self):
        return self.output_cols_names


class CreateOutputFile:

    def __init__(self):
        pass
