import shlex
import os
import subprocess
import socket
from contextlib import closing


def get_env(env):
    process_env = os.environ.copy()
    for key, value in env:
        process_env[key] = value
    return process_env


def execute(cmd, env=None):
    if env is None:
        env = []
    print('######', cmd, '######')
    popen = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, universal_newlines=True, env=get_env(env))
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def execute_sync(cmd, env=None, no_pipe=False, timeout=None, check_returncode=False):
    if env is None:
        env = []
    print('######', cmd, '######')
    if no_pipe:
        child = subprocess.Popen(
            shlex.split(cmd),
            env=get_env(env),
        )
    else:
        child = subprocess.Popen(
            shlex.split(cmd),
            env=get_env(env),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    result = child.communicate(timeout=timeout)
    result = tuple(map(lambda x: x.decode('utf-8').strip() if x else "", result))
    if check_returncode and child.returncode != 0:
        raise subprocess.CalledProcessError(child.returncode, cmd)
    print('*****', result, '*****')

    return result


def read_file(path):
    with open(path) as file_:
        return file_.read()


def write_file(path, text):
    f = open(path, 'w')
    f.write(text)
    f.close()


def create_directory(path, owner='postgres'):
    execute_sync(f'mkdir -p {path}')
    execute_sync(f'chown -R {owner}:{owner} {path}')


def restart_service(service, reload_systemctl=False):
    if reload_systemctl:
        execute_sync('systemctl daemon-reload')
    execute_sync(f'service {service} restart')


def stop_service(service):
    execute_sync(f'service {service} stop')


def get_service_status(service):
    return execute_sync(f'systemctl status {service} --no-pager')


def chown(path, owner):
    execute_sync(f'chown -R {owner}:{owner} {path}')


def get_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def touch_file(path, owner='postgres'):
    execute_sync(f'touch {path}')
    execute_sync(f'chown -R {owner}:{owner} {path}')


def remove_file(path):
    execute_sync(f'rm -f {path}')


def to_number(number):
    if type(number) == str:
        try:
            return int(number)
        except ValueError:
            return float(number)
    return number


def removesuffix(string: str, suffix: str, /) -> str:
    if string.endswith(suffix):
        return string[:-len(suffix)]
    else:
        return string[:]
