PATTERN_TEL_PASS = r'^[\"\'\s]?[+]?[\d\.\s\(]{2,}[_\-]?\d+[_\-]?[\d\.\)\s]+[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?[^:; ,|\t]{5,50}[\"\'\s]?$'
PATTERN_USERMAIL_USERNAME_PASS = r'^(([\"\'\s]?[\w\d_\.+\-@!#/$*\^]+@[\d\w.\-_]+\.[\w]{2,5})|([^|/\\\[\]\(\):;,@]{3,16}))[\"\'\s]?[:; ,|\t]{1}[\"\'\s]?[^;:,| \t]{3,60}[\"\'\s]?$'
PATTERN_UID_UN_IP_UM_PASS = r'1:Anonymous:::'
ASSERT_NAME = {
    'um': 'usermail',
    'umn': 'user_mail_name',
    'uid': 'user_ID',
    'un': 'username',
    'ufn': 'user_fname',
    'ufln': 'user_fullname',
    'uln': 'user_lname',
    'umdn': 'user_midname',
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
    'ps': 'passport',
    'dob': 'dob'
}

COLUMN_NAME_TRIGGERS = ['username', 'password', 'name', 'userid', 'имя', 'пароль', 'address', 'ipaddress', 'ip_address',
                        'postcode', 'фамилия', 'hash', 'salt', 'tel', 'f_name', 'usermail', 'email']

POSSIBLE_EXCHANGES = {
    'uid': ['id', 'userid', 'ID', 'uid', 'memberid', '№', '#'],
    'un': ['nick', 'nickname', 'ник', 'username', 'linkedinusernam'],
    'um': ['usermail', 'email', 'e-mail', 'useremail', 'emailaddress', 'майл', 'е-мейл', 'е-мэйл', 'e-mailaddress'],
    't': ['tel', 'phone', 'mobile', 'mobilenumber', 'mobilephone', 'telephone', 'phonenumber', 'телефон', 'telefono', 'тел',
          'cellphone',],
    'ufn': ['userfname', 'fname', 'firstname', 'имя' 'pib', 'name'],
    'uln': ['lname', 'userlname', 'lastname', 'фамилия', 'фам', 'familia', 'lastname', 'surname'],
    'ufln': ['fullname', 'full name', 'ФИО', 'фамилияиимя', 'имяифамилия'],
    'umdn': ['midname', 'middlename', 'middle name', 'отчество'],

    'password': ['password', 'passwd'],
    'h': ['passwordhash', 'passhash', 'token'],
    's': ['secret', 'passwordsalt', 'passsalt', 'salt'],

    'ip': ['ipaddress', 'ip'],
    'a': ['address', 'streetaddress', 'адрес', 'address1', 'homeaddress', 'adres', 'address2', 'address3',],
    'c': ['city', 'town', 'city/town', 'город', 'homecity', 'addressaddress'],
    'st': ['регион', 'область', 'обл', 'homestate', 'addressstate', 'state'],
    'cn': ['country', 'страна', 'homecountry', 'addresscountry'],
    'z': ['zipcode', 'postcode', 'addresszip', 'postalcode', 'zip'],
    'dob': ['birthdate', 'birthday', 'dob', 'birthday'],
    'ps': ['passport'],

    'uai': [ 'position',  'organization', 'gender'],
    'uai+company': ['company', 'company_name'],
    'uai+url': ['website', 'url'],
    'uai+twitter_url': ['twitterurl'],
    'uai+facebook_url': ['facebookurl'],
    'uai+linkedin_url': ['linkedinurl'],
    'uai+facebook_id': ['facebookid'],

}
