import argparse
from rich.console import Console

from fppp import start_parsing

console = Console()
parser = argparse.ArgumentParser(description="Fusion Power Predator Parser")

if __name__ == '__main__':
    parser.add_argument("--auto-parse", dest="auto_parse", action='store_true')
    parser.add_argument("--full-auto", dest="full_auto", action='store_true')
    parser.add_argument("--error_mode", dest="error_mode", action='store_true')
    parser.add_argument("-d", dest="daemon", action='store_true')

    args = parser.parse_args()
    try:
        start_parsing(
            auto_parse=args.auto_parse,
            full_auto=args.full_auto,
            error_mode=args.error_mode,
            daemon=args.daemon,
        )
        # start_parsing(auto_parse=False, full_auto=False, error_mode=True)
    except KeyboardInterrupt:
        console.print('[green]\nВЫХОД...')
