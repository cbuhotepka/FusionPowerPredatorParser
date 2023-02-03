from pathlib import Path

import pandas as pd
import os
import shutil


def convert_to_csv(file_path: str, output_dir=None, remove_if_exist=False) -> str:
    _output_dir = output_dir or os.path.splitext(file_path)[0] + '__converted_to_csv'
    if remove_if_exist and os.path.exists(_output_dir):
        shutil.rmtree(_output_dir)
    os.makedirs(_output_dir, exist_ok=True)

    xl = pd.ExcelFile(file_path)

    for sheet_name in xl.sheet_names:
        df: pd.DataFrame = xl.parse(sheet_name)
        df.to_csv(Path(_output_dir) / (sheet_name + '.csv'), index=False)

    return _output_dir


def is_excel(f: str):
    return f.endswith('.xls') or f.endswith('.xlsx')
