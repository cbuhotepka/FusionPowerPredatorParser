
from codecs import register_error


def cp1250_unknown_bytes(err):
    code = ord(err.object[err.start])
    if 0 <= code <= 255:
        return bytes([code]), err.start + 1
    raise err


def en2(file):
    register_error('cp1250_unknown_bytes', cp1250_unknown_bytes)
    with open(file, 'r', encoding='utf-8') as f:
        print(f.read().encode('cp1250', errors='cp1250_unknown_bytes').decode('utf-8')[1:].encode('koi8_r').decode('cp1251'))



def en(file):
    with open(file, 'rb') as f:
        print(f.read().decode('utf-8').encode('cp1250', errors='replace').decode('utf-8', errors='replace')
              .encode('koi8_r', errors='replace').decode('cp1251'))


if __name__ == '__main__':
    file = 'C:\\Source\\combo\\2021-04-28_520MB_ГИБДД_Санкт-Петербург_2004_2010_1.5_million_records\spb-2004-2010\\spb-2004-2010.txt'
    # en(file)
    en2(file)