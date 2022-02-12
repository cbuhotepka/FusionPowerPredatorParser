from loguru import logger
from rich.prompt import Prompt
from rich.console import Console
from pathlib import Path
import argparse
from py_dotenv import read_dotenv

dotenv_path = Path('CONFIG.env')
assert dotenv_path.exists()
read_dotenv(dotenv_path)

from engine_modul.engine import Engine


console = Console()
parser = argparse.ArgumentParser(description="Fusion Power Predator Parser")


@logger.catch()
def start_parsing(auto_parse, full_auto, error_mode):
    engine = Engine(auto_parse, full_auto, error_mode)
    engine.start()


if __name__ == '__main__':
    parser.add_argument("--auto-parse", dest="auto_parse", action='store_true')
    parser.add_argument("--full-auto", dest="full_auto", action='store_true')
    parser.add_argument("--error_mode", dest="error_mode", action='store_true')

    args = parser.parse_args()
    try:
        start_parsing(auto_parse=args.auto_parse, full_auto=args.full_auto, error_mode=args.error_mode)
    except KeyboardInterrupt:
        console.print('[green]\nВЫХОД...')