from enum import Enum


class FileMode(Enum):
    PASS_DIR = "p"
    SKIP_FILE = "l"
    OPEN_FILE = "o"
    OPEN_IN_NOTEPAD = "n"
    DELIMITER = "d"
    ERROR_DIR = "e"
    TRASH_DIR = "t"
    JSON_PARSER = "jp"
    START = "start"

    @classmethod
    def choices(cls):
        return [a.value for a in cls]


PATTERN_TEL_PASS = r'^[\"\'\s]?[+]?[\d\.\s\(]{2,}[_\-]?\d+[_\-]?[\d\.\)\s]+[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?[^:; ,|\t]{5,50}[\"\'\s]?$'
PATTERN_USERMAIL_USERNAME_PASS = r'^(([\"\'\s]?[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5})|([^|/\\\[\]\(\):;,@]{3,16}))[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?[^;:,| \t]{3,60}[\"\'\s]?$'
PATTERN_UID_UN_IP_UM_PASS = r'1:Anonymous:::'
ASSERT_NAME = {
    'um': 'usermail',
    'umn': 'user_mail_name',
    'uid': 'user_ID',
    'un': 'username',
    'ufn': 'user_fullname',
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

COLUMN_NAME_TRIGGERS = ['username', 'password', 'name', 'userid', 'имя', 'пароль', 'address', 'ipaddress', 'ip_address',
                        'postcode', 'фамилия', 'hash', 'salt', 'tel', 'f_name', 'usermail', 'email']

POSSIBLE_EXCHANGES = {
    'uid': ['id', 'userid', 'ID', 'uid', 'memberid', '№', '#'],
    'un': ['nick', 'nickname', 'ник', 'username'],
    'um': ['usermail', 'email', 'e-mail', 'useremail', 'emailaddress', 'майл', 'е-мейл', 'е-мэйл', 'e-mailaddress'],
    't': ['tel', 'phone', 'mobile', 'mobilenumber', 'mobilephone', 'telephone', 'phonenumber', 'телефон', 'telefono', 'тел'],
    'ufn': ['userfname', 'fname', 'firstname', 'имя', 'fullname', 'фамилияиимя', 'имяифамилия', 'фио',
            'фио', 'pib', 'name'] + ['lname', 'userlname', 'lastname', 'фамилия', 'фам', 'familia', 'lastname', 'surname'],
    'password': ['password', 'passwd'],
    'h': ['passwordhash', 'passhash', 'token'],
    's': ['secret', 'passwordsalt', 'passsalt', 'salt'],

    'ip': ['ipaddress', 'ip'],
    'a': ['address', 'address2', 'address3', 'streetaddress', 'адрес', 'адреcс', 'address1', 'homeaddress', 'adres'],
    'c': ['city', 'town', 'city/town', 'город', 'homecity', 'addressaddress'],
    'st': ['регион', 'область', 'обл', 'homestate', 'addressstate', 'state'],
    'cn': ['country', 'страна', 'homecountry', 'addresscountry'],
    'z': ['zipcode', 'postcode', 'addresszip', 'postalcode', 'zip'],
    'psp': ['psprt', 'passport', 'pasport', 'паспорт', 'pasportnumber', 'passportnumber'],
    'dob': ['dateofbirth', 'datebirth', 'birthdate', 'birthday'],
    'uai': ['position', 'gender'],
    'uai+company': ['company', 'company_name',  'organization'],
    'uai+url': ['website'],
}
