import re
from configparser import ConfigParser
from pathlib import Path

from rich.prompt import Prompt


config = ConfigParser()

config.read(Path(__file__).parent / 'config.example.ini')

for section in config:
    for parameter_name, parameter_description in config[section].items():

        # regex: *description* (default value)
        if match := re.match(r'(.+)\s+\((.+)\)\s*$', parameter_description):
            parameter_description = match.group(1)
            default_value = match.group(2)
        else:
            default_value = None
        config[section][parameter_name] = Prompt.ask(f"[bold blue]{parameter_description}[/]", default=default_value)

with open(Path(__file__).parent / 'config.ini', 'w') as f:
    config.write(f)
