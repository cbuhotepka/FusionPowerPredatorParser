from rich.console import Console
from rich.progress import track
from pathlib import Path
from pydantic import BaseModel
from celery import Celery, exceptions, states
import os

from .reader.reader import Reader
from .validator.validator import Validator
from .writer.writer import Writer
from py_dotenv import read_dotenv


console = Console()

BROKER_URL = "redis://127.0.0.1:6379/0"
BACKEND_URL = "redis://127.0.0.1:6379/1"
app = Celery("tasks", broker=BROKER_URL, backend=BACKEND_URL)


class ParserResponse(BaseModel):
    commands: dict


@app.task(bind=True, name="Daemon parse")
def daemon_parse(
    self,
    keys: list, 
    num_columns: int, 
    delimiter: str,
    skip: int,
    file_path: str,
    writer_data: dict,
):
    try:
        file_path = Path(file_path)
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
        return res.dict()
    except Exception as ex:
        self.update_state(states.FAILURE)
        return ex