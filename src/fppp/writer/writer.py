import os

from .store import COLS_LONG
from ..config import config

USER = config['CLICKHOUSE']['username']
PASSWORD = config['CLICKHOUSE']['password']
FIXPY = config['FIXPY']['file_name']
PARSING_DISK = config['PARSER']['local_drive']
SOURCE_DISK = config['PARSER']['remote_drive']

BASE_TYPES = ['db', 'combo']


class WriterFile:
    def __init__(self, initial_name, path, cols, delimiter, algorithm, base_info):
        base_info_list = ['name', 'date', 'source', 'type']
        for info in base_info_list:
            if info not in base_info.keys():
                raise ValueError(f"No {info} in base_info provided")
        self.initial_name = initial_name
        self.path = path
        self.cols = [c for c in cols if c != 'algorithm']
        self.delimiter = delimiter
        self.algorithm = algorithm
        self.base_info = base_info

        self.file = open(self.full_path, 'w', encoding='utf-8', errors='replace')

    def __del__(self):
        if hasattr(self, 'file') and self.file:
            self.file.close()

    def close(self):
        if hasattr(self, 'file') and self.file:
            self.file.close()

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            self._name = '.'.join(self.initial_name.split('.')[:-1]) + '_' + '_'.join(
                COLS_LONG[a] for a in self.cols if a != 'algorithm')
            if self.algorithm:
                self._name += '_' + self.algorithm
            self._name += '.rewrite'
            return self._name

    @property
    def full_path(self):
        try:
            return self._full_path
        except AttributeError:
            self._full_path = os.path.join(self.path, self.name)
            return self._full_path

    @property
    def command(self):
        try:
            return self._command
        except AttributeError:
            self._command = f"python3 {FIXPY}" \
                            f" --date {self.base_info['date']}" \
                            f" --delimiter" \
                            f" '{self.delimiter}'" \
                            f" --name '{self.base_info['name']}'" \
                            f" --source '{self.base_info['source']}'" \
                            f" --type {'database' if self.base_info['type'] == 'db' else 'combo'}" \
                            f" --user {USER}" \
                            f" --password {PASSWORD}" \
                            f" --database db_{USER}" \
                            f" --src '../files/{self.name}'" \
                            f" --colsname '{','.join(self.cols)}'" \
                            f" --quotes"
            if self.algorithm and self.algorithm != 'unknown':
                self._command += f" --algorithm '{self.algorithm}'"
            return self._command

    def write(self, data):
        if set(self.cols) != set(data.keys()):
            raise ValueError(
                f"Not matching columns in data provided!\nFile cols: {self.cols}\nData keys: {data.keys()}")
        self.file.write(self.delimiter.join([data[col] for col in self.cols]) + '\n')


class Writer:
    def __init__(self, base_type, base_name, base_source, base_date):
        if base_type not in BASE_TYPES:
            raise ValueError(f"Wrong base type provided: {base_type}")
        self.base_type = base_type
        self.base_name = base_name.replace("'", '')
        self.base_source = base_source.replace("'", '')
        self.base_date = base_date

        self.current_file = None  # Путь + имя текущего файла
        self.current_delimiter = ';'
        self.rewrite_files = {}
        self.written_files = []
        self.commands = {}  # Словарь {путь_файла: комманда}

    def __del__(self):
        for file in self.rewrite_files:
            del (file)

    @property
    def base_info(self):
        try:
            return self._base_info
        except AttributeError:
            self._base_info = {'name': self.base_name, 'date': self.base_date, 'source': self.base_source,
                               'type': self.base_type}
            return self._base_info

    def finish(self):
        for file in self.rewrite_files.values():
            file.close()
            self.commands[file.full_path] = file.command
            self.written_files.append(file)
        self.rewrite_files = {}

    def start_new_file(self, full_path, delimiter):
        """ Закрывает все текущие rewrite файлы и сохраняет их в готовые, 
        записывает команды и начинает новый файл """
        self.finish()
        self.current_file = full_path
        self.current_delimiter = delimiter

    def write(self, data: dict):
        """ Записывает информацию из словаря в соответствующий rewrite файл """
        # Проверка текущего файла и делимитра
        if not self.current_file or not self.current_delimiter:
            raise ChildProcessError("You have to start_new_file before calling write method")

        if "hash" in data and not data["hash"]:
            del data["hash"]
            del data["algorithm"]
        algorithm = data.get('algorithm')
        if 'algorithm' in data:
            del data['algorithm']

        # Создание уникального ключа исходя из колонок и алгоритма
        file_id = list(data.keys())
        file_id = tuple(set(file_id + [algorithm, ])) if algorithm else tuple(set(file_id))

        # Если нет файла rewirte с нужными колонками - создаём WriteFile
        if file_id not in self.rewrite_files.keys():
            self.rewrite_files[file_id] = WriterFile(
                initial_name=os.path.basename(self.current_file),
                path=os.path.dirname(self.current_file),
                cols=[k for k in data.keys() if k != 'algorithm'],
                delimiter=self.current_delimiter,
                algorithm=algorithm,
                base_info=self.base_info
            )
        # Записываем data в нужный файл
        self.rewrite_files[file_id].write(data)

    @property
    def iterate_commands(self):
        for file_path, command in self.commands.items():
            yield (file_path, command)


if __name__ == "__main__":
    writer = Writer('db', 'Base Name', 'leaked base', '2020-20-20')
    writer.start_new_file('D:\\dev\\info_armor\\Parser_3.0\\tests\\test_validation.py', ';')
    writer.write({'usermail': 'a@m.ru', 'tel': '888888'})
    writer.write({'tel': '777777', 'usermail': 'b@m.ru', })
    writer.write({'usermail': 'c@m.ru', 'hash': '123cawec'}, algorithm='MD5')
    writer.write({'usermail': 'd@m.ru', 'hash': '$2$5sdg23rF23rfq2ef'}, algorithm='base64')
    writer.start_new_file('D:\\dev\\info_armor\\Parser_3.0\\store.py', ',')
    writer.write({'tel': '777777', 'hash': '1111111111111', })
    writer.write({'usermail': 'c@m.ru', 'hash': '222222222222'})
    writer.write({'usermail': 'c@m.ru', 'hash': '333333333333'}, algorithm='MD5')
    writer.finish()
    for com in writer.all_commands:
        print(f'\n\n\n{com[0]}\n{com[1]}')
