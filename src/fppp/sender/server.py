import os
import socket
from flask import Flask, request
import subprocess
import json

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def reception():
    cmd = request.form.get('cmd', None)
    print(cmd)
    file = request.files.get('file')
    if file:
        files_path = os.path.abspath('../files')
        fp = os.path.join(files_path, file.filename)
        file.save(fp)
        print(fp)
    process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    print(process.stdout)
    print(process.stderr)
    print(process.returncode)
    print(' -< PROCESS FINISHED! >- ')
    result = json.dumps({'stdout': process.stdout, 'returncode': process.returncode, 'stderr': process.stderr})
    return result


if __name__ == '__main__':
    app.run(debug=True, port=9097, host='192.168.50.7')
