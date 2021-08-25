import unittest
from validator.validator import FieldsGenerator


class FieldsGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.fields = ['value_username', 'mail@mail.ru', 'alter_mail@mail.ru',
                       '"P@swwo:rd"', '+77788899955', '+75558886633',
                       'f9a85a5de5de7dea9c9e77a6f511515f', '1b1e15161e15161e110c171a110b16060a170a16']
        self.cols_name_index = {
                                'username': [0],
                                'usermail': [1, 2],
                                'password': [3],
                                'tel': [4, 5],
                                'hash': [6, 7]
                                }
        self.generator = FieldsGenerator(self.cols_name_index)

    def test_get_fields(self):
        good_result = [{
            'username': 'value_username',
            'usermail': 'mail@mail.ru',
            'password': '"P@swwo:rd"',
            'tel': '+77788899955',
            'hash': 'f9a85a5de5de7dea9c9e77a6f511515f'
        },
        {
            'username': 'value_username',
            'usermail': 'alter_mail@mail.ru',
            'password': '"P@swwo:rd"',
            'tel': '+75558886633',
            'hash': '1b1e15161e15161e110c171a110b16060a170a16'
        }]
        result = self.generator.get_generate_fields(self.fields)
        for i, item in enumerate(result):
            self.assertEqual(good_result[i], item)

    def test_handler_fields(self):
        uids = [123, 124, 125, 126]
        good_result = [123, 126, 126]
        result = self.generator._handler_fields(fields=uids, indexes=[0, 3])
        for i, item in enumerate(result):
            if i == len(good_result):
                break
            self.assertEqual(good_result[i], item)

    def test_create_handler_fields(self):
        good_len = 5
        result = self.generator._create_handler_fields(fields=self.fields)
        self.assertEqual(good_len, len(result))
        result_func0 = result['username']
        for value in result_func0:
            self.assertEqual('value_username', value)
            break

    def test_prepare_input_fields(self):
        fields = ['username-mail@mail.ru', 'mail@mail.ru', 'alter_mail@mail.ru',
                       '"P@swwo:rd"', '+77788899955', '+75558886633',
                       'f9a85a5de5de7dea9c9e77a6f511515f', '1b1e15161e15161e110c171a110b16060a170a16']
        good_result = {
                        'usermail': [1, 2, 0],
                        'password': [3],
                        'tel': [4, 5],
                        'hash': [6, 7]
                        }
        result = self.generator._prepare_input_fields(fields=fields)
        self.assertEqual(good_result, result)


    def test_handler_uai_fields(self):
        fields = ['username-mail@mail.ru', 'mail@mail.ru', 'alter_mail@mail.ru',
                       '"P@swwo:rd"', '+77788899955', '+75558886633',
                       'f9a85a5de5de7dea9c9e77a6f511515f', '1b1e15161e15161e110c171a110b16060a170a16']
        self.generator.columns_name_index = {
                        'username': [0],
                        'usermail': [1, 2],
                        'password': [3],
                        'tel': [4, 5],
                        'user_additional_info': [6, 7]
                        }
        good_result = 'f9a85a5de5de7dea9c9e77a6f511515f|1b1e15161e15161e110c171a110b16060a170a16'
        result = next(self.generator._handler_uai_fields(fields=fields, indexes=[6, 7]))
        self.assertEqual(good_result, result)

if __name__ == '__main__':
    unittest.main()