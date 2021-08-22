import unittest
from utils import clear_from_avoided_delimiters


# ======================================================================================================================================

class ClenFromDelimitersTestCase(unittest.TestCase):

    def test_valid_comma(self):
        new_list = ['String with spaces', 'Другая:стр;ока']
        self.assertEqual(clear_from_avoided_delimiters(new_list, ','), new_list, "Строки без делимитра ','")

    def test_valid_colon(self):
        new_list = ['String with spaces', 'Другая, стр;ока']
        self.assertEqual(clear_from_avoided_delimiters(new_list, ':'), new_list, "Строки без делимитра ':'")

    def test_change_semicolon(self):
        new_list = ['String with; spaces', 'Другая, стр;ока']
        self.assertEqual(clear_from_avoided_delimiters(new_list, ';'), ['String with: spaces', 'Другая, стр:ока'], "Строки с делимитром ';'")
