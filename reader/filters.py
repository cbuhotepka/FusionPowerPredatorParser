def filter_end_symbol(line):
    """
    Убирает с обоих сторон строки символы \n и \r
    """
    return line.strip('\n\r')
