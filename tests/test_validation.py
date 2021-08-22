import unittest
from utils import validate_field


class ValidationGeneralTestCase(unittest.TestCase):

    def test_empty_string(self):
        self.assertFalse(validate_field('', 'any'), 'Валидация пустой строки должна возвращать False')


# ======================================================================================================================================

class ValidationMailTestCase(unittest.TestCase):
    
# ============= INVALID EMAIL TESTS ============= 
    def test_mail_invalid_without_at(self):
        self.assertFalse(validate_field('mail123_gmail.com', 'usermail'), "В e-mail должна быть '@'")

    def test_mail_invalid_without_dot(self):
        self.assertFalse(validate_field('mail123@gmailcom', 'usermail'), "В e-mail должна быть '.'")

    def test_mail_invalid_without_at(self):
        self.assertFalse(validate_field('plainaddress', 'usermail'), "Простая строка вместо e-mail")
    
    def test_mail_invalid_wrong_symbols(self):
        self.assertFalse(validate_field('#@%^%#$@#$@#.com', 'usermail'), "Неверные символы в e-mail")
    
    def test_mail_invalid_no_name(self):
        self.assertFalse(validate_field('@example.com', 'usermail'), "Нет имени в e-mail")
    
    def test_mail_invalid_spaces_in_name(self):
        self.assertFalse(validate_field('Joe Smith <email@example.com>', 'usermail'), "Пробелы в e-mail")
    
    def test_mail_invalid_no_at_symbol(self):
        self.assertFalse(validate_field('email.example.com', 'usermail'), "Нет '@' в e-mail")
    
    def test_mail_invalid_double_at_symbol(self):
        self.assertFalse(validate_field('email@example@example.com', 'usermail'), "Две '@' в e-mail")
    
    def test_mail_invalid_starts_with_dot(self):
        self.assertFalse(validate_field('.email@example.com', 'usermail'), "E-mail начинается с '.'")
    
    def test_mail_invalid_dot_before_at_symbol(self):
        self.assertFalse(validate_field('email.@example.com', 'usermail'), "'.' перед '@' в e-mail")
    
    def test_mail_invalid_hieroglyphs(self):
        self.assertFalse(validate_field('あいうえお@example.com', 'usermail'), "Иероглифы в имени в e-mail")
    
    def test_mail_invalid_spaces_after(self):
        self.assertFalse(validate_field('email@example.com (Joe Smith)', 'usermail'), "Пробелы после e-mail")
    
    def test_mail_invalid_withou_dot(self):
        self.assertFalse(validate_field('email@example', 'usermail'), "E-mail без '.'")
    
    def test_mail_invalid_dash_after_at_symbol(self):
        self.assertFalse(validate_field('email@-example.com', 'usermail'), "Знак '-' после '@' в e-mail")
    
    def test_mail_invalid_numbers_in_domain(self):
        self.assertFalse(validate_field('email@111.222.333.44444', 'usermail'), "Цифры в домене e-mail")
    
    # def test_mail_invalid_double_dot(self):
    #     self.assertFalse(validate_field('email..email@example.com', 'usermail'), "2 точки подряд в имени e-mail")
    
    # def test_mail_invalid_double_dot_in_domain(self):
    #     self.assertFalse(validate_field('email@example..com', 'usermail'), "2 точки подряд в домене e-mail")
    
    # def test_mail_invalid_double_dot_in_name(self):
    #     self.assertFalse(validate_field('Abc..123@example.com', 'usermail'), "2 точки подряд в имени e-mail")

    
# ============= VALID EMAIL TESTS ============= 
    def test_mail_valid_simple_email(self):
        self.assertTrue(validate_field('email@example.com', 'usermail'), "Ответ False на valid e-mail: email@example.com")

    def test_mail_valid_dot_in_name(self):
        self.assertTrue(validate_field('firstname.lastname@example.com', 'usermail'), "Ответ False на valid e-mail: firstname.lastname@example.com")

    def test_mail_valid_double_domain(self):
        self.assertTrue(validate_field('email@subdomain.example.com', 'usermail'), "Ответ False на valid e-mail: email@subdomain.example.com")

    def test_mail_valid_plus_in_name(self):
        self.assertTrue(validate_field('firstname+lastname@example.com', 'usermail'), "Ответ False на valid e-mail: firstname+lastname@example.com")

    def test_mail_valid_numbers_in_name(self):
        self.assertTrue(validate_field('1234567890@example.com', 'usermail'), "Ответ False на valid e-mail: 1234567890@example.com")

    def test_mail_valid_dash_in_domain(self):
        self.assertTrue(validate_field('email@example-one.com', 'usermail'), "Ответ False на valid e-mail: email@example-one.com")

    def test_mail_valid_underscore_name_only(self):
        self.assertTrue(validate_field('_______@example.com', 'usermail'), "Ответ False на valid e-mail: _______@example.com")

    def test_mail_valid_four_letter_code(self):
        self.assertTrue(validate_field('email@example.name', 'usermail'), "Ответ False на valid e-mail: email@example.name")

    def test_mail_valid_six_letter_code(self):
        self.assertTrue(validate_field('email@example.museum', 'usermail'), "Ответ False на valid e-mail: email@example.museum")

    def test_mail_valid_double_code(self):
        self.assertTrue(validate_field('email@example.co.jp', 'usermail'), "Ответ False на valid e-mail: email@example.co.jp")

    def test_mail_valid_dash_in_name(self):
        self.assertTrue(validate_field('firstname-lastname@example.com', 'usermail'), "Ответ False на valid e-mail: firstname-lastname@example.com")


# ======================================================================================================================================

class ValidationUsernameTestCase(unittest.TestCase):

# ============= INVALID USERNAME TESTS =============     
    def test_username_invalid_email(self):
        self.assertFalse(validate_field('email@example.com', 'username'), "E-mail в username")

# ============= VALID USERNAME TESTS =============     
    def test_username_valid_cyrillic(self):
        self.assertTrue(validate_field('кириЛлица', 'username'), "Ответ False на кириллицу в username")


# ======================================================================================================================================

class ValidationTelTestCase(unittest.TestCase):

# ============= INVALID TEL TESTS =============     
    def test_tel_invalid_email(self):
        self.assertFalse(validate_field('email@example.com', 'tel'), "E-mail в tel")

# ============= VALID TEL TESTS =============     
    def test_tel_valid_cyrillic(self):
        self.assertTrue(validate_field('+7 (999) 123 45-67', 'tel'), "Ответ False на valid tel: '+7 (999) 123 45-67'")


# ======================================================================================================================================

class ValidationIpaddressTestCase(unittest.TestCase):

# ============= INVALID TEL TESTS =============     
    def test_tel_invalid_email(self):
        self.assertFalse(validate_field('email@example.com', 'ipaddress'), "E-mail в ipaddress")

# ============= VALID TEL TESTS =============     
    def test_tel_valid_cyrillic(self):
        self.assertTrue(validate_field('192.168.88.173', 'ipaddress'), "Ответ False на valid ipaddress: '192.168.88.173'")




if __name__ == '__main__':
    unittest.main()
