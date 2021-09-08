import clipboard
from rich.console import Console

from store import POSSIBLE_EXCHANGES

console = Console()


def change_col_names(colls: list):
    """Search col names in list
    Args:
        colls (list): col names from file
    Returns:
        _result (dict): {1: 'upp', 2: 'um'}
    """
    _result = {}
    _status = set()
    _error = []

    for i_col, col in enumerate(colls):
        for key, possible_names in POSSIBLE_EXCHANGES.items():
            if col.lower() in possible_names:
                colls[i_col] = key
                _result[i_col + 1] = key
                _status.add(tuple([col, True]))
        if (col, True) not in _status:
            _status.add(tuple([col, False]))
            _error.append(f'{i_col + 1}={col}')
    print(f'Error column name: {" ".join(_error)}')
    print(f'STATUS: {" ".join([f"{item}-{st}" for item, st in _status])}')
    return _result


def find_delimiter(string: str, possible_delimiters: list = [',', ':', ';', '\t', '|']):
    delimiter_numbers = sorted(list((d, string.count(d)) for d in possible_delimiters), key=lambda x: x[1],
                               reverse=True)
    if delimiter_numbers[0][1] != 0:
        return delimiter_numbers[0][0]
    return None


def normalize_col_names(string: str, delimiter: str = None):
    """Convert strin to col names
    Args:
        string (str): string with col names
        delimiter (str, optional): ',', ':', ';', '\t', '|' Defaults to None.
    Returns:
        result (str): 1=un,2=upp,3=h
    """
    if not delimiter:
        delimiter = find_delimiter(string)
        console.print(f'[magenta]Разделитель[/magenta]: "[red]{delimiter}[/red]"')
    if not delimiter:
        return None
    string = string.lower().replace('"', '').replace("'", '').replace(' ', '').replace('_', '').replace('.', '')
    colls_list = change_col_names(string.strip().split(delimiter))

    result = ','.join(f'{i}={column.strip()}' for i, column in colls_list.items())
    if result:
        clipboard.copy(result)
    return result


if __name__ == '__main__':
    while True:
        print('\n' * 2)

        STR = input('Enter STR:')
        print(normalize_col_names(STR))
