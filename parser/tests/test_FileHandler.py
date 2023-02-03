import unittest
from unittest.mock import Mock

from engine_modul.file_handler import FileHandler

class TestFileHAndler(unittest.TestCase):

    def setUp(self):
        self.autoparser = FileHandler(
            "tests/test_um_upp.csv", 
            {"base_type": "db", "base_name": "name", "base_source": "source", "base_date": "0000-00-00"},
        )
        self.autoparser.file_path = Mock()
        self.autoparser.reader = Mock()
        self.autoparser.writer = Mock()

    def test_get_keys_good(self):
        input_keys = '1=um,2=un,3=ipaddress,4=a'
        good_result = [('1', 'usermail'), ('2', 'username'), ('3', 'ipaddress'), ('4', 'address')]
        keys, cols_name = self.autoparser.get_keys(input_keys)
        self.assertEqual(good_result, keys, 'не корректно разбивается строка')

    def test_get_keys(self):
        input_keys = '1um,2=uh,3=ipaddress,4=a'
        self.assertRaises(ValueError, self.autoparser.get_keys, input_keys)