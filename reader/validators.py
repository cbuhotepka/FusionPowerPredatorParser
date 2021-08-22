import re


def validate_http_https(line):
    """
    Проверяет, начинается ли строка с http:// или https://
    """
    return '' if re.search('^(http|https)://', line) else line


def validate_repeat_one_character_all_line(line):
    re_exp = r'^\s*(.)'
    return '' if re.search(re_exp, line) else line
