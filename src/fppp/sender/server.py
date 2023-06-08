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

def read_env(env_file='.env'):
    # TODO: dotenv is not working on server
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            key, value = line.strip().split('=', 1)
            env_vars[key] = value
    return env_vars


if __name__ == '__main__':
    env = read_env()
    print(f"\nRUNNING SERVER: {env.get('HOST')}:{env.get('PORT')}")
    app.run(debug=True, port=env.get('PORT'), host=env.get('HOST'))
