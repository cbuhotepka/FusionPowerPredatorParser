import inspect
import unittest
from pprint import pprint
from unittest import skip

from json_parser.json_parser import ConvertorJSON


class ConvertorJSONTest(unittest.TestCase):
    """Тест JSON конвертора"""

    def setUp(self) -> None:
        self.conv = ConvertorJSON('test_file.json')

    def test_read_json_file(self):
        """тест: данные из файла прочитаны"""
        self.conv._read_json_file()
        self.assertIs(type(self.conv.json_data), dict)


    def test_get_data_for_string_from_dict(self):
        """тест: генерируется список tuple из данных JSON"""
        self.conv.json_data = {"empty_key": "empty_string", "payload": {
            "key_string": "string",
            "key_list": ['list_string_1', 'list_string_2', 'list_string_3'],
            "key_dict": {
                "sub_key_string": "sub_string",
                "sub_key_list": ['sub_list_string_1', 'sub_list_string_2'],
                "sub_key_dict": {"sub_sub_key": "sub_sub_string"}
                }
            }
        }
        self.conv.sequence_keys = ["payload"]
        good_result = [
            {"key_string": "string"},
             {"key_list_1": 'list_string_1',
             "key_list_2": 'list_string_2',
             "key_list_3": 'list_string_3'},
             {"sub_key_string": "sub_string",
            "sub_key_list_1": 'sub_list_string_1',
            "sub_key_list_2": 'sub_list_string_2',
            "sub_sub_key": "sub_sub_string"}
        ]
        received_result = [item for item in self.conv._get_data_for_string_from_dict()]
        pprint(received_result)
        self.assertEqual(good_result, received_result)

    def test_get_data_for_string_from_list(self):
        """тест генерации данных при корневом списке в JSON"""
        self.conv.json_data = [
            {"key_1": "string_1", "key_2": ["string_2_1", "string_2_2"],  "key_3": {"sub_key": "sub_string"}},
            {"key_1": "string_1", "key_2": ["string_2_1", "string_2_2"],  "key_3": {"sub_key": "sub_string"}},
        ]

        good_result = [
            {
            "key_1": "string_1",
            "key_2_1": "string_2_1",
            "key_2_2": "string_2_2",
            "sub_key": "sub_string"
        }, {
            "key_1": "string_1",
            "key_2_1": "string_2_1",
            "key_2_2": "string_2_2",
            "sub_key": "sub_string"
        },
        ]
        received_result = [item for item in self.conv._get_data_for_string_from_dict()]
        pprint(received_result)
        self.assertEqual(good_result, received_result)

    def test_get_dict_data(self):
        """тест: получение списка tuple из dict"""
        data = {"key_1": "string_1", "key_2": "string_2"}
        good_result = {"key_1": "string_1", "key_2": "string_2"}
        received_result = self.conv._get_dict_data(data)
        self.assertEqual(received_result, good_result)

        data = {"key_1": "string_1", "key_2": ["string_2_1", "string_2_2"],  "key_3": {"sub_key": "sub_string"}}
        good_result = {
            "key_1": "string_1",
            "key_2_1": "string_2_1",
            "key_2_2": "string_2_2",
            "sub_key": "sub_string"
        }
        received_result = self.conv._get_dict_data(data)
        self.assertEqual(received_result, good_result)

    def test_get_list_data(self):
        """тест: генерирубтся tuple из списка"""
        data = [{"key_1": "string_1"}, {"key_2": "string_2"}, {"key_3": "string_3"}]
        good_result = {'key_1': 'string_1', 'key_2': 'string_2', 'key_3': 'string_3'}
        received_result = self.conv._get_list_data(key='key', ls=data)
        self.assertEqual(good_result, received_result)

        data = ["string_1", "string_2", "string_3"]
        good_result = {'key_1': 'string_1', 'key_2': 'string_2', 'key_3': 'string_3'}
        received_result = self.conv._get_list_data(key='key', ls=data)
        self.assertEqual(good_result, received_result)

    def test_search_key_in_dict(self):
        """тест: поиск ключа в структуре"""
        json_data = {
            'key_1': 'string_1',
            'key_2': 'string_1',
            'key_3': {
                'sub_key_1': 'sub_string_1',
                'sub_key_2': {
                    'find_key': {
                        'good_key_1': 'string_1',
                        'good_key_2': 'string_1',
                        'good_key_3': 'string_1',
                    }
                }
            }
        }
        good_result = ['find_key', 'sub_key_2', 'key_3']
        self.conv._search_key_in_dict('find_key', json_data)
        result = self.conv.sequence_keys
        self.assertEqual(result, good_result)


if __name__ == '__main__':
    unittest.main()