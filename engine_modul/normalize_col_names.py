import clipboard
from rich.console import Console

from engine_modul.store import POSSIBLE_EXCHANGES, ASSERT_NAME

console = Console()


def change_col_names(colls: list):
    """Search col names in list
    Args:
        colls (list): col names from file
    Returns:
        _result (dict): {1: 'upp', 2: 'um'}
    """
    _result = {}
    _status = []
    _error = []

    for i_col, col in enumerate(colls):
        next = False
        if  col.lower() in ASSERT_NAME.keys() or col.lower() in ASSERT_NAME.values():
            _result[i_col + 1] = col
            _status.append([i_col + 1, col, True])
            continue
        for key, possible_names in POSSIBLE_EXCHANGES.items():
            if col.lower() in possible_names:
                col = key
                colls[i_col] = col
                _result[i_col + 1] = col
                _status.append([i_col+1, col, True])
                next = True
        if next:
            continue
        _status.append([i_col+1, col, False])
        _error.append(f'{i_col + 1}={col}')
    console.print(f'Error column name: {"NONE" if not _error else " ".join(_error)}')
    console.print("COLS: " + ",".join(
        [f"{'[green]' if st else '[red]'}{i}={col}[/]" 
        for i, col, st in sorted(_status, key=lambda x: x[0])]
    ))
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
