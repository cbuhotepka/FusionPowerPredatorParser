DELIMITERS = [' ', ',', ':', ';', '|']

BANNED_SYMBOL = ['š', 'ô', '\x9d', '°', 'ћ', 'ќ', '®', '™', '‚', 'ž', '\x81',
                 'µ', '¿', 'â', 'Ў', 'ÿ', '²', '·', '‹', '’', '\x90', '¡', 'І',
                 '¯', 'Ђ', 'њ', 'љ', '³', 'º', '¥', 'є', '¬', '¸', '�', 'Ð', '“',
                 '¹', 'œ', 'Ñ', '˜', '§', '¦', '›', 'ў', 'ˆ', 'Ÿ', 'ð', 'Œ', 'ƒ',
                 'à', '‡', 'Â', '±', '¾', '†', '•', 'ö', 'ü', 'Ó', 'Ð', 'ï']

POSSIBLE_EXCHANGES = {
    'uid': ['id', 'userid', 'ID', 'uid', 'memberid', '№', '#'],
    'un': ['nick', 'nickname', 'ник', 'username'],
    'um': ['usermail', 'email', 'e-mail', 'useremail', 'emailaddress', 'майл', 'е-мейл', 'е-мэйл', 'e-mailaddress'],
    't': ['tel', 'phone', 'mobile', 'mobilephone', 'telephone', 'phonenumber', 'телефон', 'telefono', 'тел'],
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
    'cn': ['страна', 'homecountry', 'addresscountry'],
    'z': ['zipcode', 'postcode', 'addresszip', 'postalcode', 'zip'],
    'psp': ['psprt', 'passport', 'pasport', 'паспорт', 'pasportnumber', 'passportnumber'],
    'dob': ['dateofbirth', 'datebirth', 'birthdate', 'birthday'],

    'uai': ['address2', 'address3', 'company', 'position'],
}

COLUMN_NAME_TRIGGERS = ['username', 'password', 'name', 'userid', 'имя', 'пароль', 'address', 'ipaddress', 'ip_address',
                        'postcode', 'фамилия', 'hash', 'salt', 'tel']

COLS_SHORT = {
    'um': 'usermail',
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
    'psp': 'passport',
    'dob': 'dob',
}
COLS_LONG = dict((v,k) for k,v in COLS_SHORT.items())

ALLOW_EXTENSION = ['.txt', '.csv', '', '.zip', '.rar', '.tsv']
