PATTERN_TEL_PASS = r'^[\"\'\s]?[+]?[\d\.\s\(]{2,}[_\-]?\d+[_\-]?[\d\.\)\s]+[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?.{5,16}[\"\'\s]?$'
PATTERN_USERMAIL_USERNAME_PASS = r'^(([\"\'\s]?[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5})|([^|/\\\[\]\(\):;,@]{3,16}))[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?[^;:,| \t]{3,60}[\"\'\s]?$'

ASSERT_NAME = {
    'um': 'usermail',
    'umn': 'user_mail_name',
    'uid': 'user_ID',
    'un': 'username',
    'ufn': 'user_fname',
    'uln': 'user_lname',
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