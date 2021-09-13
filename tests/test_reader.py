import unittest
from reader.reader import Reader, validate_repeat_one_character_all_line, validate_http_https, filter_end_symbol


class ReaderTest(unittest.TestCase):
    def setUp(self):
        self.good_line_all = 'value_username:mail@mail.ru:alter_mail@mail.ru:"P@swwo:rd":+77788899955:+75558886633'

        self.bad_line_repeat_one_character_all_line = 'vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'
        self.good_line_no_repeat_one_character_all_line = 'vvvvvvvvvvvvvvvvvvvvvvvv:vvvvvvvvvvvvvvvvvvvvvvvvv'

        self.bad_line_http_https = 'https://github.com/cbuhotepka/FusionPowerPredatorParser/tree/main/tests'
        self.good_line_http_https = 'my_username:my_passWorD:"https://github.com/cbuhotepka/FusionPowerPredatorParser/tree/main/tests"'

        self.bad_line_end_symbol = 'my_username:my_passWorD\n'
        self.good_line_without_end_symbol = 'my_username:my_passWorD'

    def test_filter_end_symbol(self):
        good_result = self.good_line_without_end_symbol
        result = filter_end_symbol(self.bad_line_end_symbol)
        self.assertEqual(result, good_result, 'Не корректно фильтруется символ окончания.')

    def test_validate_repeat_one_character_all_line(self):
        result = validate_repeat_one_character_all_line(self.bad_line_repeat_one_character_all_line)
        self.assertEqual('', result, 'Не корректно валидируется строка из одного повторяющегося символа.')

        good_result = self.good_line_no_repeat_one_character_all_line
        result = validate_repeat_one_character_all_line(good_result)
        self.assertEqual(good_result, result, 'Не корректно валидируется строка из одного повторяющегося символа.')

    def test_validate_http_https(self):
        result_1 = validate_http_https(self.bad_line_http_https)
        self.assertEqual('', result_1, 'Не корректно вадидируется строка-ссылка.')

        result_2 = validate_http_https(self.good_line_http_https)
        self.assertEqual(self.good_line_http_https, result_2, 'Не корректно вадидируется строка-ссылка.')



if __name__ == '__main__':
    unittest.main()