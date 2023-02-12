import subprocess
import os
import shutil


def convert_to_csv(input_dir, output_dir=None, remove_if_exist=False) -> str:
    _output_dir = output_dir or input_dir + '__converted_to_csv'
    if remove_if_exist and os.path.exists(_output_dir):
        shutil.rmtree(_output_dir)
    print(subprocess.run(f'croconvert --strucrack --dbcrack --csv "{input_dir}" --outputdir "{_output_dir}"', shell=True))
    return _output_dir


def is_cronos(f: str):
    return f.endswith('.dat') or f.endswith('.tad')
