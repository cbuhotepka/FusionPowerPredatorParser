import unittest
from unittest.mock import Mock

from engine.file_handler import FileHandler

class TestFileHAndler(unittest.TestCase):

    def setUp(self):
        self.autoparser = FileHandler(Mock())

    def test_get_keys_good(self):
        input_keys = '1=um,2=un,3=ipaddress,4=a'
        good_result = [('1', 'usermail'), ('2', 'username'), ('3', 'ipaddress'), ('4', 'address')]
        keys, cols_name = self.autoparser.get_keys(input_keys)
        self.assertEqual(good_result, keys, 'не корректно разбивается строка')

    def test_get_keys(self):
        input_keys = '1um,2=uh,3=ipaddress,4=a'
        self.assertRaises(ValueError, self.autoparser.get_keys, input_keys)