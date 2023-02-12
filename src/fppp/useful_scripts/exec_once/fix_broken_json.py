#   Example
#   '"uid":50350589,"first_name":"Татьяна","last_name":"Тимофеева","sex":1,"nickname":"","screen_name":"id50350589","bdate":"10.2","city":1,"mobile_phone":"нет","home_phone":"нет","site":"нет","status":"","last_seen":{"time":1414357937,"platform":7},"occupation":{"type":"work","name":"МОЭК"},"career":[{"company":"МОЭК","country_id":1,"city_id":1,"from":2001}],"university":247,"university_name":"МГСУ НИУ (МГСУ-МИСИ)","faculty":1019,"faculty_name":"Институт инженерно-экологического строительства и механизации (Водоснабжения и водоотведения, Механизации и автоматизации строительства, Теплогазоснабжения и вентиляции)","graduation":0,"interests":"","activities":"","about":"","relatives":[{"uid":-134490024,"type":"child","name":"Никита"'


import re
from pathlib import Path

from ...reader import Reader

regex = '\"([\w_]+)\":\"?([\w\d\.+-]+)\"?(,|$)'


def execute(file_path: str):
    with Reader(file_path) as readfile, open(file_path + '__.jsonlist', 'w') as writefile:
        for i, row in enumerate(readfile):
            for key, value, _ in re.findall(regex, row):
                writefile.write('{"%s":"%s"}\n' % (key, value))
    return file_path + '__.jsonlist'


def test():
    file_path = Path(__file__).parent / 'test'
    fp = execute(file_path.__str__())