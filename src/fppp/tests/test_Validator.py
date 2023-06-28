import logging
import re
import unittest
from collections import OrderedDict

from validator.hash_identifer import identify_hashes
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
            '__MTQwMzkwNDIxMQAxNDAzOTA0MjExAEFRQUFBQUJaMEJDcFZUajcwZ0YtTl9ndEh0bS1pSmhwZzVzTzVoTX4',
            '97c2fb24ccae0943f577099ffc0efc37f9a94023123',
            '36de6d686f801213bd5495469fe17d406746b125123',
            '54524ceaf4247e9eda52108787bff9425be8931c123',
        ]:
            line = f'random_username:{password}'
            expected = [OrderedDict([('algorithm', 'unknown'), ('username', 'random_username'), ('hash', password)])]
            result = list(self.validator.get_fields(line))
            self.assertEqual(result, expected, 'Should return hash with algorithm')


class TestValidatorTestUnknownHashes(unittest.TestCase):
    def test_hashed(self):
        data = [
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4777',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4777',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            '__MTgzNjM4NjE3MgAxODM2Mzg2MTcyAEFRQUFBQUJiQmE0MUp0SkxoaTFDejljZjB4d2lhOHdscmVaU3ZTOH4!!!',
            'F9fa89634994165ce41725afd9a1a2f944be35a6!!',
            'Buster9151buster9151qq20016123',
            'Brooke2BC1P14Xa1jLXjVGv123',
            'EnidanW3wl9divvxEG4KgJ123',
            'Brooke2BC1P14Xa1jLXjVGv!',
            'Martini4GDquPLwMnK34fQQ!',
            'Nini1901nalalanneaAa1!!',
            'Eusouumbolinhodearro!!',
            'Harryecjk8YgRbMoJdvG7!',
            'Familiadabosss0119123',
            'Hacker122334122334!!',
            'Cami1305asdt112311!!',
            'Balsaminejetaime123!',
            'Nineinchnails1234123',
            'C44a471bd78cc6c2fea3',
            '5DF6EF0F88FB8DE40D589AFE379E61030B9E851A38676B0135F1DF2CE73E724498F9FBCF19FE02E4E491EDF9929EF70DB39D59D2A420F4BAC651FE441F5CE4BF123',
            '7BF821D0E9B21CDF95B643B041C8E17BDAB7B77988870C1F4C5EA7DA4F7062CAD36313C3BF31388D14ED9FD80D6A9ACD4BD3CBA93F3A10B83C20C931466AADA2!',
            '__MTY1NzM0MDA1MQAxNjU3MzQwMDUxAEFRQUFBQUJjWjhFazlfcEpnREUwTmMwMWdvWF9BM3hmUE11WEktY34123',
            '__MTY2MTAxNjcxNTUAMTY2MTAxNjcxNTUAQVFBQUFBQmQ0OHdMT3lMWjF3UWxCUzNjbmFMYV9jcUJQV2hJSnFRfg',
            '__MTQwMzkwNDIxMQAxNDAzOTA0MjExAEFRQUFBQUJaMEJDcFZUajcwZ0YtTl9ndEh0bS1pSmhwZzVzTzVoTX4!',
            '$HEX[313233343536373839d0bad180d0b8d181d182d0b8d0bdd0b0]123',
            '$HEX[d0aed180d0b8d0b9d090d0bdd0b4d180d0b5d0b5d0b2d0b8d187]',
            'B3f2bed3ace001193b8d8a5eedbf40d5marionelagherghi88!!',
            '0da90ac8dd27b9772aad656b424d903ac00dcb6elarry123',
            'Magnolija6magnolija6041MAGNOLIJA6MAGNOLIJA6041!',
            '0da90ac8dd27b9772aad656b424d903ac00dcb6elarry!',
            '$HEX[d0bfd0b8d0bfd0b5d186d0bfd0b8d0bfd0b5d186]',
            'Ttfsjwpzqwettfsjwpzqwe1TTFSJWPZQWETTFSJWPZQWE1',
            '33207f19aec929e41f7998ae6f6904d51e5d1c4f123',
            'A266868f770322d7fe9169f70f47a29119566bcc123',
            'Ebd1e9d494343934b7214d0e7d5c12d3a3d76560123',
            '9359a4d812173b65a3a0094cd86363e79731a3c2123',
            '58cdf9e8a06772e3bcc1475af399ca2472b3e7d1123',
            '3e8485b005145398518f88e546e71f0bd12fd8ef123',
            'Bc1aab26fcc794a2db49afeeee3d07fa48a25b20123',
            '329ef167fcd2befe9df782ccd8d6ea35b8338fd4123',
            'B6042cf559c6563f34ed143455806fc2cf08e2cb123',
            '2483e25d422f0216d14a70be5aeedcd82192b0a2123',
            'Ea3c985e92da17b26cdd0a7146cdf3eee8a448e1123',
            'Ranielle18_soulmates@yahseanal_20@yahoo.com',
            'A9681e7c4ffa3729bcf4d79abddd50ffdec91a98123',
            'C4c05ffb935feda5e34fabc12699fc04618b2750123',
            'B912079e340ae020c05fa8f33b0be43d7c569cb2123',
            '97c2fb24ccae0943f577099ffc0efc37f9a94023123',
            '719c6b1b5b34e58b557afecfe7f07025627a513d123',
            'D2c1a4cbe88f57cc4dd79e4b665ba560d711badb123',
            '9be5b7ac9650287b23a374fad8f1f093525771c0123',
            '61393182eced953da2bbedbdf1c942da434e2d2c123',
            '65b3dd225fe19c6a9ec4383161ea00fe0f161157123',
            '235885d533d4d4a1fb1fe9afd11280b872c37b7d123',
            '10ec2a6aedc46ea55d828c54685fbcf059358f51123',
            '1c41a0fe2191baf95eedda3dcb8d016f90f25cd3123',
            'D0bc16508d08f2b10d0ce006200e69ddae9b1191123',
            '51e19883264a794d9750c53bd17c30e41548c423123',
            '8f0bd8d5ebd1451f569e047f364811eb88fef1c3123',
            '3ffd1142a5604a5e80ca28b237ca0ac4b59193a0123',
            'A3a61fb8a1abbf851dc37b5850dab776ad6ec47f123',
            '899cfa37a0ed63971251ec69045e2a32935dcc12123',
            'Fd1fbf441c5e45942e741bbaf8c3cfa5215c861f123',
            'Cb29c1898caa2143145215e8c89306b546c4f43a123',
            '363ffc3a6c97b7a6570a8ec93847ab5705260705123',
            '9322c5aeb79dcf14e2f8c2440c8186c9f37392a0123',
            'Fd57303d3de0abb35dbbd5f7b8c0c9fbcd098a2b123',
            '54524ceaf4247e9eda52108787bff9425be8931c123',
            '576f45e190fd3a0ffcf75914d170deb55f10aa11123',
            '8d0399a23842230bcec0bbffe86828bb2549383d123',
            'B448385b8db01a9c56f4abd3daac3e07b454f395123',
            '996257aeff16176d7d5c1ec45ad84012670685cd123',
            '269f71e588a921c4fc8c80e74b544263d76be68e123',
            '48cff6762d11a2141c51eecaea77c8c4399e2555123',
            'F336a620c284c15720ef05e22e378586dcb02fda123',
            'C24f5cff02c08728c9789791a4439cdb2fa10c39123',
            '46abc6c4681d02cefcf0dee198d68aa436ccdc3f123',
            '2659ee2465c48958beda4d5759bae7c7b180164b123',
            '36de6d686f801213bd5495469fe17d406746b125123',
            'B3a601476ce525c5c8dd0983645zatvornytska1123',
            '2325c7ebc63e34b3601f9ab4f87a9c0824b7fcb4123',
            'F6efc6b9c580db48bff44db7f630d650d8fd8b65123',
            '5821eb27d7b71c9078000da31a5a654c97e401b9123',
            '7153ca17ff5a46547eb46f1dcbd03881d4753239123',
            '448d5097e65ffa7f3922a5ef3fa526ac16a8ff7f123',
            '4af27b575d822325be1e9ef7864199f7e4bfa9b8123',
            '842772d52ae9239700a327ffb205b5614b6d1e41123',
            '3cbd219d1c5ce965f070c89dfd337fe24379507e123',
            '860f5f76bcbddf0f5a435df95ae55ec6d958abc4123',
            '4999915a961edfd7686112c2935288e1266eae14123',
            '8cabcc2a483f94b712efd2d9d1a442a782dd3d77123',
            '1aa2cf0d826945fc530394469242a9a912c5aef0123',
            '6a2cb1e13fa0e47f97136a53855471a6597b18cd123',
            '5135e8fcef1d3d841c4618b4282780a67b4232c4123',
            'Febdd1c108fed2bb4c5e5624966ef69244c4db89123',
            'C44907a70e90363fb18f530e59783f501848dab3123',
            '5637912c038bc3e2984fbe28c32567921ad783b7123',
            '03fdf1323c8d4770c90576ce2a1860d476ded8ab123',
            '072abada7f34df5dc3faff49033db7894dfecd5d123',
            '1363d4641c5b52056c9998d640d0757ffed1505a123',
            '4f4c49e8f0f456c74ffaae8b8550cb48cdb0dbeb123',
            '276acb753189f6e95315b2af075883ef3772c4f5123',
            'B628aec1c060b28787da306360b41a3037e9ad4e123',
            '418d940643b1975d62234ee01246ad4b58904184123',
            '599118367756492380a90b9bb3c2d6ae51dfc153123',
            '26f4521528956dab00f42527ae851f3bcbd3719d123',
            '3763846d8562aceef56cece52668734bba05e428123',
            '84d58f9874c99e3f126223097add151109ec9dc4123',
            '694df0259290e20d1fdd2325fd9fa35f1f3b5228123',
            '6427f32ab87db79ec3cf9eb320ae8d2001512010!!',
            'Db3e2b2c80fa739a4e4782ae40944a542e5bd430!!',
            'C9e84eb5da7c8b99fc10b5e15d1355f6a672cefc!!',
            '1a9c53aa2c827ea9d57998b13405976745bf8c12!!',
            '7de720760fdd99354d5e468044a27d9fee4cb2b4!!',
            '84b269511a135522046bc3fbd63ef0918bebd7f1!!',
            '8bb92a4243ccd9a7e8245d6e30b488eefcdb896b!!',
            '1363d4641c5b52056c9998d640d0757ffed1505a!!',
            '0c7605a11995f647c066c5e18695b18e1f8636e1!!',
            'A4d12746c46e57e7deb8af9c39b9020dca4135b7!!',
            'D49172eaab452bba6ac4f182082f42410a7bfdb6!!',
            '347b0f783aede9510c312f22647c5aa05fc9a34f!!',
            'C66d5fd424845ed347f4d709abdc2b0c23c279c5!!',
            '4ce57d235f3d02d7e0071ee41ed5f64b02fefcda!!',
        ]
        hashes, passes = [], []
        for item in data:
            if identify_hashes(item):
                hashes.append(item)
            else:
                passes.append(item)
        print('\n\nHASES:\n' + '\n'.join(hashes))
        print('\n\nPASSES:\n' + '\n'.join(passes))



if __name__ == '__main__':
    unittest.main()
