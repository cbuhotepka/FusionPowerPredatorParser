from pprint import pprint

from rich.highlighter import RegexHighlighter
from rich.prompt import Prompt, IntPrompt, Confirm

from rich.console import Console
import os

from rich.theme import Theme


class DelimiterHighlighter(RegexHighlighter):
    base_style = "text."
    highlights = [r"(?P<all>.)", r"(?P<delimiter>[,:;|])",
    r"(?P<email>[a-zA-Z0-9_]+([a-zA-Z0-9_.-]+)?[a-zA-Z0-9_]+\@[a-zA-Z0-9]([a-zA-Z0-9._-]+)?\.[a-zA-Z]+)"]


theme = Theme({"text.delimiter": "bold red",
                "text.email": "bold cyan",
                "text.all": "yellow"})
console = Console()
console_for_show = Console(highlighter=DelimiterHighlighter(), theme=theme)


class UserInterface:

    def ask_type_base(self):
        type_base = Prompt.ask('Тип папки', choices=['combo', 'db'])
        return type_base

    def ask_reparse_file(self):
        _answer = Confirm.ask('[green]Перепарсить готовые файлы?', default=False)
        return _answer

    def ask_delimiter(self):
        _delimiter = Prompt.ask('[magenta]Разделитель', choices=[':', ',', ';', r'\t', '|'])
        _delimiter = '\t' if _delimiter == '\\t' else _delimiter
        console.print(f'[magenta]Разделитель[/magenta]: "[red]{_delimiter}[/red]"')
        return _delimiter

    def ask_num_cols(self, num_columns):
        input_num_columns = IntPrompt.ask('Количество столбцов', default=num_columns + 1) - 1
        return input_num_columns

    def ask_skip_lines(self, skip):
        answer = IntPrompt.ask('Пропустить строк', default=skip)
        return answer

    def ask_cols_keys(self, find_keys):
        if find_keys:
            _keys = Prompt.ask(f'[cyan]Колонки {find_keys}')
            if not _keys:
                keys = find_keys
            elif _keys == 'e':
                keys = ''
            else:
                keys = f'{find_keys},{_keys}'
        else:
            keys = Prompt.ask(f'[cyan]Колонки ')
        return keys

    def ask_column_names(self, column_names):
        console.print(f'[magenta]Определены столбцы[/magenta]: "[green]{column_names}[/green]"')
        _answer = Confirm.ask('[magenta]Все правильно?', default=True)
        return _answer

    def ask_mode_handle(self):
        answer = Prompt.ask(f"[green]Если все ОК нажмите Enter",
                            choices=['p', 'l', 'o', 'n', 'd', 'e', 't'],
                            default='start')
        return answer

    def show_delimiter(self, delimiter):
        if delimiter:
            console.print(f'[magenta]Разделитель[/magenta]: "[red]{delimiter}[/red]"')
        else:
            console.print(f'[magenta]Разделитель[/magenta]: [red]Отсутствует![/red]')

    def show_num_columns(self, num_columns):
        console.print(f'[magenta]Количество столбцов[/magenta]: "[green]{num_columns}[/green]"')

    def show_left_dirs(self, left_dirs):
        console.print(f'[cyan]Папок осталось[/cyan]: "[green]{left_dirs}[/green]"')

    def show_left_files(self, left_files):
        console.print(f'[cyan]Файлов осталось[/cyan]: "[green]{left_files}[/green]"')

    def print_dirs_status(self, path, status):
        if status == 'for parsing':
            console.print(f'[blue]{path}[/blue]')
        elif status == 'done':
            console.print(f'[green]{path}[/green]')
        elif status == 'skipped':
            console.print(f'[yellow]{path}[/yellow]')
        elif status == 'error folder':
            console.print(f'[red]{path}[/red]')

    def show_file(self, file):
        """Print 15 line from parsing file
            Args:
                file (Reader()): file for parsing
            """
        console.print(f'[bold magenta]{file.file_path}')
        console.print("[magenta]" + '-' * 200, overflow='crop')
        file.open()
        for i, line in enumerate(file):
            line_to_show = line[:1000] if len(line) > 3000 else line
            try:
                console_for_show.print(line_to_show)
                if i > 15:
                    break
            except:
                continue
        print('\n')

    def print_key_value_JSON(self, json_path: str, limit: int) -> None:
        """Вываод данных JSON на экран"""
        with open(json_path, 'r', encoding='utf-8') as json_file:
            for i, line in enumerate(json_file.readlines()):
                if len(line) > 1000:
                    length = 1000
                else:
                    length = len(line)
                console.print(f'{line[:length]}')
                if i == limit:
                    break
            print()

    def ask_mode_parsing_JSON(self) -> str:
        """Запрос режима парсинга JSON"""
        # p - пропустить файл
        # o - открыть файл
        # k - указать ключ
        # l - корневой список данных
        while True:
            mode = Prompt.ask(f"[green]Выберите режим парсинга JSON",
                                choices=['p', 'o', 'k', 'l'],
                                default='k')
            if mode == 'k':
                answer = Prompt.ask(f'[cyan]Введите ключ: ')
                if answer == "error":
                    continue
            else:
                answer = mode
            return answer
