import re

validate_http_https_pattern = re.compile(r'^(http|https)://')
validate_repeat_one_character_all_line_pattern = re.compile(r'^\s*(.)(\1)+\s*$')

def validate_http_https(line):
    """
    Проверяет, начинается ли строка с http:// или https://
    """
    return '' if validate_http_https_pattern.search(line) else line


def validate_repeat_one_character_all_line(line):
    return '' if validate_repeat_one_character_all_line_pattern.search(line) else line
