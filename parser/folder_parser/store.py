import os


USER = os.environ.get('USER_NAME', 'er')
PASSWORD = os.environ.get('USER_PASSWORD', 'qwerty123')
PARSING_DISK = os.environ.get('PARSING_DISK_NAME', 'C')
SOURCE_DISK = os.environ.get('SOURCE_DISK_NAME', 'W')

BASE_TYPES = ['db', 'combo']


ALLOW_EXTENSIONS = ['.txt', '.csv', '', '.tsv', '.zip', '.rar', '.json']

BANNED_SYMBOL = ['Ð', 'œ', '\x9d', 'ž', '\x90', '˜', '—', '°', '±', 'Ñ', 'ƒ', '³', '¾', 
                '\x81', '‡', 'µ', 'º', '¡', 'Â', 'š', '²', 'ˆ', '¿', '§', '•', '¥', '¯', '®', '›', 
                '¦', 'ð', 'Ÿ', '¹', 'â', '‹', 'Œ', '·']

ERROR_EXTENSIONS = ['.sql', '.xml', '.xlsx', '.xls', '.doc', '.docx', '.htm', '.html', '.jpg', '.pdf', '.mdb']