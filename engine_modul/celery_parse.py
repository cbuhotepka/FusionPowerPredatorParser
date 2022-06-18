from rich.console import Console
from rich.progress import track
from pathlib import Path

from reader.reader import Reader
from validator.validator import Validator
from engine_modul.file_handler import FileHandler
from writer.writer import Writer


console = Console()

def daemon_parse(
    keys: list, 
    num_columns: int, 
    delimiter: str,
    skip: int,
    file_path: Path,
    writer_data: dict,
):
    validator = Validator(keys, num_columns, delimiter)
    read_file = Reader(file_path)
    writer = Writer(**writer_data)
    file_handler = FileHandler(read_file, read_file.file_path)

    count_rows_in_file = file_handler.get_count_rows()
    console.print(f'[yellow]Строк в файле: {count_rows_in_file}')

    read_file.open(skip=skip)
    for line in track(read_file, description='[bold blue]Парсинг файла...', total=count_rows_in_file):

        for fields_data in validator.get_fields(line):

            # Пропуск записи если в полях меньше 2 не пустых значений
            count_not_empty_values = sum(map(lambda x: bool(x), fields_data.values()))
            if fields_data['algorithm']:
                if count_not_empty_values < 3:
                    continue
            else:
                if count_not_empty_values < 2:
                    continue

            # Запись полей в файл
            writer.write(fields_data)