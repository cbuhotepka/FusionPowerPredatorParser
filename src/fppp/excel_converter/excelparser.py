from pathlib import Path

import pandas as pd
import os
import shutil

from rich.prompt import Confirm


class ExcelToCsvFileConverter:

    def __init__(self,
                 file_path: str,
                 output_dir: str = None,
                 ):
        assert os.path.exists(file_path), 'File does not exists (try use absolute path)'
        assert self.is_excel(file_path)
        self._file_path = file_path
        self._xl = pd.ExcelFile(self._file_path)

        self._output_dir = output_dir or os.path.splitext(self._file_path)[0] + '__converted_to_csv'
        self._create_output_dir(self._output_dir)

    @staticmethod
    def is_excel(file_path: str):
        return file_path.endswith('.xls') or file_path.endswith('.xlsx')

    def convert_to_csv(self, rewrite_if_exists: bool = False) -> str:
        self._convert_to_csv(rewrite_if_exists=rewrite_if_exists)

        return self._output_dir

    def _convert_to_csv(self, rewrite_if_exists=False):
        for sheet_name in self._xl.sheet_names:
            output_file_path = Path(self._output_dir) / (sheet_name + '.csv')

            if rewrite_if_exists or self._is_need_write_output_file(output_file_path):
                df: pd.DataFrame = self._xl.parse(sheet_name)
                if not df.empty:
                    print(df)
                    df.to_csv(output_file_path, index=False)

        return self._output_dir

    @staticmethod
    def _create_output_dir(output_dir_path):
        os.makedirs(output_dir_path, exist_ok=True)

    @staticmethod
    def _output_file_exists(_file_path):
        return os.path.exists(_file_path)

    def _is_need_write_output_file(self, file_path):
        return not os.path.exists(file_path) or \
            Confirm.ask(
                f'[yellow]Файл [bold]{file_path}[/] уже существует, перезаписать его?[/]',
                default=False)
