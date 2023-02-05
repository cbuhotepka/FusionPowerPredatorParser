import os
from ..config import config

USER = config['CLICKHOUSE']['username']
PASSWORD = config['CLICKHOUSE']['password']
FIXPY = config['FIXPY']['file_name']
PARSING_DISK = config['PARSER']['local_drive']
SOURCE_DISK = config['PARSER']['remote_drive']

BASE_TYPES = ['db', 'combo']

ALLOW_EXTENSIONS = ['.txt', '.csv', '', '.tsv', '.zip', '.rar', '.json']

BANNED_SYMBOL = ['Ð', 'œ', '\x9d', 'ž', '\x90', '˜', '—', '°', '±', 'Ñ', 'ƒ', '³', '¾',
                 '\x81', '‡', 'µ', 'º', '¡', 'Â', 'š', '²', 'ˆ', '¿', '§', '•', '¥', '¯', '®', '›',
                 '¦', 'ð', 'Ÿ', '¹', 'â', '‹', 'Œ', '·']

ERROR_EXTENSIONS = ['.sql', '.xml', '.xlsx', '.xls', '.doc', '.docx', '.htm', '.html', '.jpg', '.pdf', '.mdb']
