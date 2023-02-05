from configparser import ConfigParser

from rich.prompt import Prompt, Confirm

from .create_config import create_config
from pathlib import Path

config = ConfigParser()
config_path = Path(__file__).parent / 'config.ini'
if config_path.exists():
    config.read(config_path)
else:
    if Confirm.ask('[blod red]Файл конфигурации не найден, создать?[/]'):
        config = create_config()

__all__ = ['config']
