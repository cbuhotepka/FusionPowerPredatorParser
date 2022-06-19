from rich.console import Console
from rich.progress import track
from pathlib import Path
from pydantic import BaseModel

from reader.reader import Reader
from validator.validator import Validator
from writer.writer import Writer


console = Console()


class ParserResponse(BaseModel):
    commands: dict


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
    writer.start_new_file(file_path, delimiter if delimiter != '\t' else ';')

    count_rows_in_file = read_file.get_count_rows()
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

    writer.finish()

    res = ParserResponse(commands=writer.commands)
    return res