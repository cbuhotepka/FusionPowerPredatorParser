import unittest
from validator.validator import Validator
from collections import OrderedDict


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
        self.keys = [(1, 'username'), (2, 'password')]
        self.validator = Validator(keys_and_cols_name=self.keys, num_columns=1, delimiter=':')

    def test_get_fields_valid(self):
        line = 'random_username:dagwetawetwear'
        expected = [OrderedDict([('algorithm', ''), ('username', 'random_username'), ('userpass_plain', 'dagwetawetwear')])]
        result = list(self.validator.get_fields(line))
        self.assertEqual(result, expected, 'Should return result')

    def test_get_fields_hash(self):
        for algorithm, hashed_pass in {
            'MD5': 'f9a85a5de5de7dea9c9e77a6f511515f',
            'HEX': '$HEX[D23E5DD1FE5059F55E33]',
            'SHA-1(Hex)': '1b1e15161e15161e110c171a110b16060a170a16',
        }.items():
            line = f'random_username:{hashed_pass}'
            expected = [
                OrderedDict([('algorithm', algorithm), ('username', 'random_username'), ('hash', hashed_pass)])
            ]
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


if __name__ == '__main__':
    unittest.main()
