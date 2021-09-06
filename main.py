from loguru import logger
from rich.prompt import Prompt
from rich.console import Console
from pathlib import Path
import argparse
from dotenv import load_dotenv

dotenv_path = Path('CONFIG.env')
assert dotenv_path.exists()
load_dotenv(dotenv_path)

from engine.engine import Engine


console = Console()
parser = argparse.ArgumentParser(description="Fusion Power Predator Parser")


@logger.catch()
def start_parsing(auto_parse, full_auto):
    engine = Engine(auto_parse, full_auto)
    engine.start()


if __name__ == '__main__':
    parser.add_argument("--auto-parse", dest="auto_parse", action='store_true')
    parser.add_argument("--full-auto", dest="full_auto", action='store_true')

    args = parser.parse_args(["--auto-parse"])
    try:
        start_parsing(auto_parse=args.auto_parse, full_auto=args.full_auto)
    except KeyboardInterrupt:
        console.print('[green]\nВЫХОД...')