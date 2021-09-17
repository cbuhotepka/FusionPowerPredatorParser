import os
import shutil
from rich.prompt import Prompt, Confirm
import requests
from loguru import logger
from tabulate import tabulate
from pathlib import Path
from rich.console import Console
import argparse
import re
import json
from py_dotenv import read_dotenv

dotenv_path = Path('../CONFIG.env')
assert dotenv_path.exists()
read_dotenv(dotenv_path)


parser = argparse.ArgumentParser(description="Sender Flask")
parser.add_argument("--auto-fail", dest="auto_fail", action='store_true')
args = parser.parse_args()

console = Console()

Path(f"C:/Source/combo/fail_send.txt").touch()
Path(f"C:/Source/db/fail_send.txt").touch()

Path(f"C:/Source/combo/send_done.txt").touch()
Path(f"C:/Source/db/send_done.txt").touch()

PD = os.environ['PARSING_DISK_NAME']
SD = os.environ['SOURCE_DISK_NAME']


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


HOST, PORT = '192.168.88.173', os.environ['SERVER_PORT_FIX']


# combo = None
# done_parse = None
# fail_send = None
# done_send = None
# dir = None
# all_command_path = None

def get_cmds(f):
    _data = json.load(f)
    return list(zip(_data.values(), _data.keys()))


@logger.catch()
def client(cmd, path=None):
    url = f'http://{HOST}:{PORT}/'
    data = {'cmd': cmd}
    files = {'file': open(path, 'rb')} if path else None
    r = requests.post(url, data=data, files=files)
    result = json.loads(r.text)
    return result


# def preparation():
# client_path = input('Путь до клиента')


def show_progress(done, left):
    a = int(round(done / (left + done), 2) * 100)
    bar = Colors.OKGREEN + '#' * a + Colors.ENDC + '-' * (100 - a)
    stat = f"Выполнено - {done}\n" \
           f"Осталось - {left}"
    print(f"<{bar}>" + f' {a}%')
    print(Colors.HEADER + stat)


def search_command_files(path_search):
    for root_dir, dirs, files in os.walk(path_search):
        for file in files:
            if re.search(r'^_command_\.txt', file):
                file_path = os.path.join(root_dir, file)
                yield file_path
    return None


def create_command_file():
    all_command_path = os.path.join(str(dir), 'all_command_sender.txt')
    # if os.path.exists(all_command_path):
    #     return
    all_command_sender = open(all_command_path, 'w', encoding='utf-8')
    for line in done_parse:
        line = line.replace('\n', '')
        if line in done_send or line in fail_send or not os.path.exists(line) or len(os.listdir(line)) == 0:
            # пропуск если в готово или фейле)
            continue
        if os.path.exists(os.path.join(line, 'OLD-command.txt')):
            continue
        for file in search_command_files(line):

            command_file = open(file, 'r', encoding='utf-8')

            cmds = get_cmds(command_file)
            command_file.close()
            os.rename(file, os.path.join(os.path.split(file)[0], 'OLD-command.txt'))
            new_data = {}
            for cmd, path in cmds:
                cmd = cmd.replace('\ufeff', '')
                if 'hash' in cmd.split('--colsname')[-1] and args.auto_fail:
                    continue
                if 'hash' in cmd.split('--colsname')[-1]:
                    if '--algorithm' not in cmd:
                        clr = Colors.FAIL
                        print(*open(path, encoding='utf-8').readlines()[:5])
                        print(path)
                        cmd += ' --algorithm ' + f"'{Prompt.ask('Введите тип хеша: ')}'"
                        is_send = None
                    elif "--algorithm 'unknown'" in cmd:
                        print(*open(path, encoding='utf-8').readlines()[:5])
                        print(path)
                        cmd.replace("--algorithm 'unknown'", '--algorithm ' + f"'{Prompt.ask('Введите тип хеша: ')}'")
                        is_send = None
                    else:
                        clr = Colors.WARNING
                cmd = re.sub(r'main.py', 'fix.py', cmd)
                new_data[path] = cmd
                all_command_sender.write(f'{cmd}\n')
                all_command_sender.write(f'{path}\n')
            command_file = open(file, 'w', encoding='utf-8')
            new_json = json.dumps(new_data)
            command_file.write(new_json)
            command_file.close()


@logger.catch()
def start():
    # all_command_file = open(dir + '\\all_command_sender.txt', 'r', encoding='utf-8')
    # all_cmds = get_cmds(all_command_file.readlines())
    _resend = Confirm.ask('Перезаливаем готовые?', default='n')

    for line in done_parse:
        line = line.replace('\n', '')
        # line = os.path.split(line)[0]
        # base_dir = os.path.join(*Path(line).parts[:4])
        if line in done_send or line in fail_send or not os.path.exists(line) or len(os.listdir(line)) == 0:
            # пропуск если в готово или фейле)
            continue

        if command_path := [path for path in search_command_files(line)]:
            command_file = open(command_path[0], 'r', encoding='utf-8')
        else:
            continue
        cmds = get_cmds(command_file)

        answer = ''
        is_fatal_error = False
        is_success = False

        done_command_path = os.path.join(line, 'done_command_sender.txt')

        if os.path.exists(done_command_path) and _resend == 'n':
            done_command_file = open(done_command_path, 'r', encoding='utf-8')
            done_command = get_cmds(done_command_file)
        else:
            done_command = []
        done_command_file = open(done_command_path, 'a', encoding='utf-8')

        ready_cmd = [cm[0] for cm in done_command]

        for cmd, path in cmds:
            cmd = re.sub(r'main.py', 'fix.py', cmd)
            cmd = re.sub(r'None', 'fix.py', cmd)
            if cmd in ready_cmd:
                continue
            rem_path = os.path.join('/home/br/files/', os.path.basename(path))
            cmd1 = f'test -f {rem_path}'
            answer = client(cmd1)
            print(answer)
            if answer['returncode'] == 0:
                path = None


            cmd = cmd.replace('\ufeff', '')
            clr = ''
            if 'hash' in cmd.split('--colsname')[-1]:
                if '--algorithm' not in cmd:
                    clr = Colors.FAIL
                else:
                    clr = Colors.WARNING
            print(tabulate([[clr + cmd], [path]]))
            # if clr == Colors.FAIL:
            #   continue
            is_send = Prompt.ask('Отправляем?', choices=['hash', 'command', 'pass'],
                                 default='') if clr == Colors.FAIL else ''
            print(str(path))
            # Prompt.ask('Продолжаем: ')
            if is_send:
                if is_send == 'command':
                    cmd = Prompt.ask('Введите команду: ')
                    is_send = None
                elif is_send == 'hash':
                    print(*open(path, encoding='utf-8').readlines()[:5])
                    cmd += ' --algorithm ' + f"'{Prompt.ask('Введите тип хеша: ')}'"
                    is_send = None
                else:
                    continue
            # subprocess.run(f'python {client_path} --cmd "{cmd}" --path "{path}"')
            # print(cmd)
            with console.status('[bold green]Отправка...', spinner='point', spinner_style="bold blue"):

                answer = client(cmd, path)

            print(answer['stdout'])
            if 'FATAL ERROR. This file cannot be repaired.' in answer['stdout']:
                is_fatal_error = True
                with open(f"{dir}/fail_send_cmd.txt", 'a', encoding='utf-8') as f:
                    f.write(cmd + '\n')
                    f.write(line + '\n')
            elif 'All done!' in answer['stdout']:
                is_success = True
                done_command_file.write(f'{cmd}\n')
                done_command_file.write(f'{path}\n')

        done_command_file.close()
        print(line)
        if args.auto_fail:
            with open(f"{dir}/pass_auto_send.txt", 'a', encoding='utf-8') as f:
                f.write(line + '\n')
            continue
            # user_input = 'fail' if is_fatal_error else None
        else:
            pass
            # user_input = Prompt.ask('Все ок?', choices=['fail'], default='') if is_fatal_error else None
            user_input = None

        if not is_fatal_error and is_success:
            command_file.close()
            line_source = line
            base_source = line.replace(f'{PD}:\\Source', f'{SD}:\\Source')
            # basedir = C:\Source\db\database
            base_dir = os.path.join(*Path(line_source).parts[:4])
            line_imported = line_source.replace(f'{PD}:\\Source', f'{PD}:\\Imported')
            if combo:
                # path_source = C:\Source\combo\database
                path_source = Path(os.path.join(*Path(line_source).parts[:4]))
                # path_imported = C:\Imported\combo
                path_imported = Path(os.path.join(*Path(line_imported).parts[:3]))
                # base_imported = S:\Imported\combo
                base_imported = str(path_imported).replace(f'{PD}:\\', f'{SD}:\\')
            else:
                # path_source = C:\Source\db\database\item
                path_source = Path(os.path.join(*Path(line_source).parts[:5]))
                # path_imported = C:\Imported\db\database
                path_imported = Path(os.path.join(*Path(line_imported).parts[:4]))
                # base_imported = S:\Imported\db\database
                base_imported = str(path_imported).replace(f'{PD}:\\', f'{SD}:\\')

            with open(f'{dir}\\send_done.txt', 'a', encoding='utf-8') as f:
                f.write(line_source + "\n")

            try:
                os.makedirs(path_imported, exist_ok=True)
                os.makedirs(base_imported, exist_ok=True)
                shutil.move(str(path_source), str(path_imported))
                shutil.move(str(base_source), str(base_imported))
                # Чистка пустых папок
                if os.path.exists(base_dir) and not os.listdir(base_dir):
                    shutil.rmtree(base_dir)
                _base_rm = os.path.join(*Path(base_source).parts[:4])
                if os.path.exists(_base_rm) and not os.listdir(_base_rm):
                    shutil.rmtree(_base_rm)
            except Exception as ex:
                print(Colors.WARNING + f'Не получается перместить - {ex}')
                # _answer = Confirm.ask('Продолжаем?', default='y')
                # if _answer == 'n':
                #     exit()

            print('\033[32m ' + 'Перенос завершен')

        else:
            with open(f"{dir}/fail_send.txt", 'a', encoding='utf-8') as f:
                f.write(line + '\n')


if __name__ == '__main__':
    start_path = f'{PD}:\\Source\\'

    list_files = []
    combo = Confirm.ask('Комбо?')
    dir = start_path + 'combo' if combo else start_path + 'db'
    done_parse = open(f'{dir}\\_dirs_complete_.txt', 'r', encoding='utf-8').readlines()
    done_parse = list(filter(lambda x: x != '\n', done_parse))

    fail_send = open(f'{dir}\\fail_send.txt', 'r', encoding='utf-8').readlines()
    fail_send = list(filter(lambda x: x != '\n', fail_send))
    fail_send = list(map(lambda x: x.replace('\n', ''), fail_send))

    done_send_file = open(f'{dir}\\send_done.txt', 'r', encoding='utf-8')
    done_send = list(filter(lambda x: x != '\n', done_send_file.readlines()))
    done_send = list(map(lambda x: x.replace('\n', ''), done_send))
    done_send_file.close()

    # show_progress(complete, left)
    print(Colors.WARNING + f'В ошибках - {len(fail_send)}')
    # preparation()
    create_command_file()
    start()
