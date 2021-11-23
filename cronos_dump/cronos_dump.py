import subprocess


def convert_to_csv(input_dir, output_dir=None) -> str:
    _output_dir = output_dir or input_dir + '__converted_to_csv'
    subprocess.run(f'croconvert --csv "{input_dir}" --outputdir "{_output_dir}"', shell=True)
    return _output_dir


def is_cronos(f: str):
    return f.endswith('.dat') or f.endswith('.tad')
