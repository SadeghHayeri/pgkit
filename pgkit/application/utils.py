import shlex
import os

import subprocess
from time import sleep

def get_env(env):
    process_env = os.environ.copy()
    for key, value in env:
        process_env[key] = value
    return process_env

def execute(cmd, env=[]):
    print('######', cmd, '######')
    popen = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, universal_newlines=True, env=get_env(env))
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def execute_sync(cmd, env=[]):
    print('######', cmd, '######')
    return subprocess.Popen(shlex.split(cmd), env=get_env(env)).communicate()
