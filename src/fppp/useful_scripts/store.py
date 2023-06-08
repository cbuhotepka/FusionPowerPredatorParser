DELIMITERS = [' ', ',', ':', ';', '|']

DELETE_VALUES_LIST = [r'\bNULL\b', r'\bnull\b', '<blank>', '"""']

BANNED_SYMBOL = {'Ў', 'Ў', 'º', '˜', 'š', 'ž', 'њ', '¬', 'ˆ', '¶',
                 '¯', 'œ', '±', 'є', 'љ', '\x9d', '•', '¾', 'ƒ', '·', '§',
                 '‡', '‹', 'µ', 'ô', 'Ð', 'ð', 'Â', '�', '¡', '¿',
                 '³', 'ў', 'Ђ', '\x81', '²',  '¹', '®', 'ѓ', 'Œ',
                 '¥', 'ќ', 'Ó', '›', 'Ў', 'ï', '†', '°', '\x90',
                 '™', 'â', '¦', 'ћ', 'Ђ', 'Ð', '¿', '�', 'Ð'}

POSSIBLE_EXCHANGES = {
    'uid': ['id', 'userid', 'ID', 'uid', 'memberid', '№', '#'],
    'un': ['nick', 'nickname', 'ник', 'username'],
    'um': ['usermail', 'email', 'e-mail', 'useremail', 'emailaddress', 'майл', 'е-мейл', 'е-мэйл', 'e-mailaddress'],
    't': ['tel', 'phone', 'mobile', 'mobilenumber', 'mobilephone', 'telephone', 'phonenumber', 'телефон', 'telefono', 'тел'],
    'ufn': ['userfname', 'fname', 'firstname', 'имя', 'firstname', 'fullname', 'фамилияиимя', 'имяифамилия', 'фио',
            'фио', 'pib'],
    # 'uln': ['lname', 'userlname', 'lastname', 'фамилия', 'фам', 'familia', 'lastname', 'surname'],

    'password': ['password', 'passwd'],
    'h': ['secret', 'passwordhash', 'passhash', 'token'],
    's': ['passwordsalt', 'passsalt', 'salt'],

    'ip': ['ipaddress', 'ip'],
    'a': ['address', 'streetaddress', 'адрес', 'address1', 'homeaddress', 'adres'],
    'c': ['city', 'town', 'city/town', 'город', 'homecity', 'addressaddress'],
    'st': ['регион', 'область', 'обл', 'homestate', 'addressstate', 'state'],
    'cn': ['country', 'страна', 'homecountry', 'addresscountry'],
    'z': ['zipcode', 'postcode', 'addresszip', 'postalcode', 'zip'],

    'uai': ['address2', 'address3', 'company', 'position', 'birthdate', 'birthday', 'organization'],
}

COLUMN_NAME_TRIGGERS = ['username', 'password', 'name', 'userid', 'имя', 'пароль', 'address', 'ipaddress', 'ip_address',
                        'postcode', 'фамилия', 'hash', 'salt', 'tel']

ASSERT_NAME = {
    'um': 'usermail',
    'umn': 'user_mail_name',
    'uid': 'user_ID',
    'un': 'username',
    'ufn': 'user_fullname',
    # 'uln': 'user_lname',
    'upp': 'userpass_plain',
    's': 'salt',
    'h': 'hash',
    't': 'tel',
    'c': 'city',
    'ip': 'ipaddress',
    'cn': 'country',
    'st': 'state',
    'a': 'address',
    'z': 'zip',
    'uai': 'user_additional_info',
    'p': 'password',
}

ALLOW_EXTENSION = ['.txt', '.csv', '', '.zip', '.rar', '.tsv', '.7z', '.gz', '.tar']

PATTERN_TEL_PASS = r'^[\"\'\s]?[+]?[\d\.\s\(]{2,}[_\-]?\d+[_\-]?[\d\.\)\s]+[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?.{5,16}[\"\'\s]?$'
PATTERN_USERMAIL_USERNAME_PASS = r'^(([\"\'\s]?[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5})|([^|/\\\[\]\(\):;,@]{3,16}))[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?[^;:,| \t]{3,60}[\"\'\s]?$'