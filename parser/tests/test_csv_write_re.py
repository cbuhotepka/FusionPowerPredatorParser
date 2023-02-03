import unittest
from utils import csv_write_re
import os
from pathlib import Path


# ======================================================================================================================================

class CsvWriteReTestCase(unittest.TestCase):

    def check_file(self, file_name, keys, colsnames, delimiter, skip, delete_file=True):
        result_file_path = csv_write_re(
            path=Path(os.path.join('tests', file_name)), 
            keys=keys,
            colsnames=colsnames,
            delimiter=delimiter,
            skip=skip,
        )
        file_name_split = file_name.split('.')
        right_file_name = os.path.join('tests', file_name_split[0] + '_right.' + file_name_split[1])

        with open(right_file_name, 'r', encoding='utf-8') as output_file:
            with open(result_file_path, 'r', encoding='utf-8') as result_file:
                right_data = output_file.readlines()
                result_data = result_file.readlines()

                result_file.close()
                if delete_file:
                    os.remove(result_file_path)

                for i, result_line in enumerate(result_data):
                    right_line = right_data[i]
                    self.assertEqual(result_line, right_line, f"\n\nAssert при парсинге файла {file_name}, ошибка на линии {i}:\nRESULT: {result_line}RIGHT:  {right_line}")
        
    #  USERMAIL  USERPASS_PLAIN
    def test_file_email_upp(self):
        self.check_file(
            file_name='test_um_upp.csv', 
            keys=((1, 'usermail'), (2, 'userpass_plain')),
            colsnames=['usermail', 'userpass_plain'],
            delimiter=':',
            skip=4,
        )
    
    #  USER_FNAME  USER_LNAME  TEL  ADDRESS  USER_ADDITIONAL_INFO
    def test_file_test_ufn_uln_t_a_uai(self):
        self.check_file(
            file_name='test_ufn_uln_t_a_uai.csv', 
            keys=((1, 'user_fullname'), (2, 'user_lname'), (3, 'user_additional_info'), (4, 'user_additional_info'), (6, 'tel'), (7, 'user_additional_info'), (9, 'user_additional_info'), (12, 'address')),
            colsnames=['user_fullname', 'user_lname', 'tel', 'address', 'uai'],
            delimiter=',',
            skip=1,
        )      
