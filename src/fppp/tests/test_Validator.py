import logging
import re
import unittest
from collections import OrderedDict

from validator.hash_identifer import identify_hashes, get_complexity
from validator.validator import Validator


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        self.good_line = 'value_username:mail@mail.ru:alter_mail@mail.ru:"P@swwo:rd":+77788899955:+75558886633'
        self.bad_line = 'value_username:mail@mail:alter_mail@mail.ru:P@swword:+77788ff899hj955:+75558886633'
        self.short_line = 'value_username:mail@mail:P@swword:+77788ff899hj955'
        self.keys = [(1, 'username'), (2, 'usermail'), (3, 'usermail'), (4, 'password'), (5, 'tel'), (6, 'tel')]
        self.validator = Validator(keys_and_cols_name=self.keys, num_columns=5, delimiter=':')
        self.fields = [
            'value_username',
            'mail@mail.ru',
            'alter_mail@mail.ru',
            '"P@swwo:rd"',
            '+77788899955',
            '+75558886633',
            'f9a85a5de5de7dea9c9e77a6f511515f',
            '1b1e15161e15161e110c171a110b16060a170a16',
        ]

    def test_split_line_to_fields(self):
        good_result = [
            'value_username',
            'mail@mail.ru',
            'alter_mail@mail.ru',
            'P@swwo,rd',
            '+77788899955',
            '+75558886633',
        ]
        result = self.validator.split_line_to_fields(self.good_line)
        self.assertEqual(result, good_result, 'не корректно разбивается строка')
        result = self.validator.split_line_to_fields(self.short_line)
        self.assertEqual([], result, 'не корректно разбивается строка')

    def test_handler_keys(self):
        good_result = {'username': [0], 'usermail': [1, 2], 'password': [3], 'tel': [4, 5]}
        result = self.validator.handler_keys()
        self.assertEqual(result, good_result, 'не правильно обработаны ключи')

    def test_delete_blank_of_line(self):
        dirty_string = '"""username""",NULL,"usermail",null,<blank>,usernull'
        good_result = 'username,,"usermail",,,usernull'
        result = self.validator._delete_blank_of_line(dirty_string)
        self.assertEqual(good_result, result, 'не правильно очищена строка')

    def test_get_fields_good_1(self):
        good_result = [
            OrderedDict(
                {
                    'algorithm': '',
                    'username': 'value_username',
                    'usermail': 'mail@mail.ru',
                    'userpass_plain': 'P@swwo,rd',
                    'tel': '+77788899955',
                }
            ),
            OrderedDict(
                {
                    'algorithm': '',
                    'username': 'value_username',
                    'usermail': 'alter_mail@mail.ru',
                    'userpass_plain': 'P@swwo,rd',
                    'tel': '+75558886633',
                }
            ),
        ]
        for i, item in enumerate(self.validator.get_fields(self.good_line)):
            self.assertEqual(good_result[i], item, 'не правильно очищена строка')

    def test_get_fields_good_2(self):
        good_line = 'user_mail@mail.ru:mail@mail.ru:alter_mail@mail.ru:"P@swwo:rd":+77788899955:+75558886633'
        good_result = [
            OrderedDict(
                {'algorithm': '', 'usermail': 'mail@mail.ru', 'userpass_plain': 'P@swwo,rd', 'tel': '+77788899955'}
            ),
            OrderedDict(
                {
                    'algorithm': '',
                    'usermail': 'alter_mail@mail.ru',
                    'userpass_plain': 'P@swwo,rd',
                    'tel': '+75558886633',
                }
            ),
            OrderedDict(
                {'algorithm': '', 'usermail': 'user_mail@mail.ru', 'userpass_plain': 'P@swwo,rd', 'tel': '+75558886633'}
            ),
        ]
        for i, item in enumerate(self.validator.get_fields(good_line)):
            self.assertEqual(good_result[i], item, 'не правильно очищена строка')

    def test_get_fields_bad_1(self):
        bad_line = 'value_username:mail@mail:alter_mail@mail.ru:P@swword:+7g78-8ff899hj955:+75558886633'
        good_result = [
            OrderedDict(
                {'algorithm': '', 'username': 'value_username', 'usermail': '', 'userpass_plain': 'P@swword', 'tel': ''}
            ),
            OrderedDict(
                {
                    'algorithm': '',
                    'username': 'value_username',
                    'usermail': 'alter_mail@mail.ru',
                    'userpass_plain': 'P@swword',
                    'tel': '+75558886633',
                }
            ),
        ]
        for i, item in enumerate(self.validator.get_fields(bad_line)):
            self.assertEqual(good_result[i], item, 'не правильно очищена строка')

    def test_get_fields_bad_2(self):
        bad_line = 'value_username:mail@mail:P@swword:+77788ff899hj955'
        good_result = [{}]
        for i, item in enumerate(self.validator.get_fields(bad_line)):
            self.assertEqual(good_result[i], item, 'не правильно очищена строка')


class ValidatorTestAutoParse(unittest.TestCase):
    def setUp(self):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        self.keys = [(1, 'username'), (2, 'password')]
        self.validator = Validator(keys_and_cols_name=self.keys, num_columns=1, delimiter=':')

    def test_get_fields_valid(self):
        line = 'random_username:dagwetawetwear'
        expected = [
            OrderedDict([('algorithm', ''), ('username', 'random_username'), ('userpass_plain', 'dagwetawetwear')])
        ]
        result = list(self.validator.get_fields(line))
        self.assertEqual(result, expected, 'Should return result')

    def test_get_fields_hash(self):
        for algorithm, hashed_pass in {
            'MD5': 'f9a85a5de5de7dea9c9e77a6f511515f',
            'HEX': '$HEX[D23E5DD1FE5059F55E33]',
            'SHA-1(Hex)': '1b1e15161e15161e110c171a110b16060a170a16',
        }.items():
            line = f'random_username:{hashed_pass}'
            expected = [OrderedDict([('algorithm', algorithm), ('username', 'random_username'), ('hash', hashed_pass)])]
            result = list(self.validator.get_fields(line))
            self.assertEqual(result, expected, 'Should return hash with algorithm')

    def test_get_fields_with_domain(self):
        for domain_line in [
            'https://example.com',
            'My Channel:test',
            'My TG:@telegram',
        ]:
            result = list(self.validator.get_fields(domain_line))
            self.assertEqual(result, [], 'Username like "https" should return empty list')

    def test_get_fields_suspicious_upp(self):
        for password in [
            'regular_pass',
            'pass1242aeradg',
            'pass1241231241241245123',
            'aaaaaaaaaa11111111@@@@@@@rrrrrrrrrrrr3333333ttttttt#########',
            'C0mp1e><sh0rt.pA$$w0r_d',
            'L0n9 pa$$w0rd w1th spaces can_n0t 6e ha$h',
            'Lorem Ipsum is simply dummy text of the printing and typesetting industry.',
            'long_test_mail+test@email.test.com',
            'Magnolija6magnolija6041MAGNOLIJA6MAGNOLIJA6041!',
            'Ranielle18_soulmates@yahseanal_20@yahoo.com',
            '$HEX',
            '[Julia_]',
            '[James]Bond',
        ]:
            line = f'random_username:{password}'
            expected = [OrderedDict([('algorithm', ''), ('username', 'random_username'), ('userpass_plain', password)])]
            result = list(self.validator.get_fields(line))
            self.assertEqual(result, expected, 'Should return userpass_plain')

    def test_get_fields_unknown_hashes(self):
        for password in [
            'f9a85a5de5de7dea9or1oc9e77a6f511515f',
            '$ANY[D23E5DD1FE25059P32F55E33]',
            '$ANY{1b1e15161e15161e110c171a110b16060a1}',
            '1b1e15161e15161e110c171a110b16060a170a16wr3r234',
            '329ef167fcd2befe9df782ccd8d6ea35b8338fd4123',
            # '__MTQwMzkwNDIxMQAxNDAzOTA0MjExAEFRQUFBQUJaMEJDcFZUajcwZ0YtTl9ndEh0bS1pSmhwZzVzTzVoTX4',
            # '97c2fb24ccae0943f577099ffc0efc37f9a94023123',
            '36de6d686f801213bd5495469fe17d406746b125123',
            # '54524ceaf4247e9eda52108787bff9425be8931c123',
        ]:
            line = f'random_username:{password}'
            expected = [OrderedDict([('algorithm', 'unknown'), ('username', 'random_username'), ('hash', password)])]
            result = list(self.validator.get_fields(line))
            self.assertEqual(result, expected, 'Should return hash with algorithm')


class TestValidatorTestUnknownHashes(unittest.TestCase):
    def test_hashed(self):
        data = [
            'F46ef81f2464441ba58aeecbf654ee41123',
            '3904d4a9f9434878a57543e95b132242123',
            '4514ab66979eaa47b59589a070b056a7123',
            '940dcaa0b22965338835594b821e8688123',
            '27753ca3edb57063ca5aa0cafa8df308123',
            '1a09a0626bf916aaa381779698a17d41123',
            'Cd81cfd0a3397761fac44ddbe5ec3349123',
            '2cc751c432cbafb011cda9afe1cdf191123',
            '89bf86d84c0f42867756acd8148943b8123',
            'A152e841783914146e4bcd4f39100686123',
            '890887522234230b75d8728b34e2de9f123',
            '72fc9b925a7076abcc7a83262b076670123',
            'neko05alMastershaz@Hotmail.Co.Uk',
            'subwmuui2nxvbqd41+bdkl0pkd8m6u1dwmp71a2s',
            'xv8FJeH136@www.paypal.com/cgi-bi',
            'lobadcela.lobito.Adrián.césar.y.lalo',
            'find_pass=06a169c2ff16d75113d9bf6f3cce42d7',
            'vjelxy$n$eow5qn#ylh*ewsr16b5t*',
            'soleil76dq10Ssoleil76dq10Sa777',
            'w1989asAuD_bOyzfull.gmAiL@yaho',
            'khalistep88p4yt1ttmrxl0hd@gmatriona03@yahoo.com',
            'tottigoalqQaAqQtottigoalqQaAqQ',
            'sleckermasato@dj.so-net.ne.jp1',
            'warcraft11q23kwarcraft1!1q23k7',
            'Sinaddr1v8g9unxthf22fsjfjg5l9yxf5g0jldjg5k92nupfzu6a3jq8lfxs4',
            'Weslee94@aron13_rebamba@yajoe23.4u@gmail.com',
            'Jean-Yves.L.Excellent@ens-lyon',
        ]
        hashes, passes = [], []
        for item in data:
            if identify_hashes(item):
                # print(item, ' - ', get_complexity(item), get_complexity(item) / len(item))
                hashes.append(item)
            else:
                passes.append(item)
        print('\n\nHASHES:\n' + '\n'.join(hashes))
        print('\n\nPASSES:\n' + '\n'.join(passes))


if __name__ == '__main__':
    unittest.main()
