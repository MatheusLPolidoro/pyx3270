import errno
import math
import os
import pathlib
import re
import socket
import subprocess
import sys
from contextlib import closing
from functools import cache
from random import randint
from time import sleep, time
from typing import Literal

sys.path.append(str(pathlib.Path(__file__).parent))

from command_config import command_map
from exceptions import (
    CommandError,
    FieldTruncateError,
    NotConnectedException,
    TerminatedError,
)
from iemulator import (
    AbstractCommand,
    AbstractEmulator,
    AbstractEmulatorCmd,
    AbstractExecutableApp,
)

BINARY_FOLDER = f'{os.path.dirname(__file__)}/binary'
MODEL_TYPE = Literal['2', '3', '4', '5']
MODEL_DIMENSIONS = {
    '2': {
        'rows': 24,
        'columns': 80,
    },
    '3': {
        'rows': 32,
        'columns': 80,
    },
    '4': {
        'rows': 43,
        'columns': 80,
    },
    '5': {
        'rows': 27,
        'columns': 132,
    },
}


def run_timeout(func):
    def inner(
        timeout: int = 3,
        recursive: bool = False,
        instance: type = str,
        *args,
        **kwargs,
    ):
        # Parâmetros de controle
        check_instance = not recursive  # checar tipo se não for recursivo

        end_time = time() + timeout
        result = None

        while time() < end_time:
            try:
                if recursive:
                    result, exit_condition = func(result, *args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                    exit_condition = result

                if isinstance(exit_condition, bool) and exit_condition:
                    break
                if check_instance and isinstance(result, instance):
                    break

            except Exception:
                sleep(randint(0, 3))

        return result

    return inner


class ExecutableApp(AbstractExecutableApp):
    def __init__(self, shell: bool = False, model: MODEL_TYPE = '2') -> None:
        self.shell = shell
        self.subprocess = None
        self.args = self._get_executable_app_args(model)
        self._spawn_app()

    @cache
    def _spawn_app(self) -> None:
        kwargs = {
            'shell': self.shell,
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }

        if os.name == 'nt':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        else:
            kwargs['start_new_session'] = True

        self.subprocess = subprocess.Popen(self.args, **kwargs)

    def _get_executable_app_args(self, model: MODEL_TYPE) -> list:
        return self.__class__.args + [
            '-xrm',
            f'*model: {model}',
            '-localcp',
            'utf8',
            '-utf8',
        ]

    def connect(*args) -> bool:
        return False

    def close(self):
        if self.subprocess.poll() is None:
            self.subprocess.terminate()
        return_code = self.subprocess.returncode or self.subprocess.poll()
        return_code = return_code if return_code is not None else 0
        return return_code

    def write(self, data: str):
        self.subprocess.stdin.write(data)
        self.subprocess.stdin.flush()

    def readline(self):
        return self.subprocess.stdout.readline()


class Command(AbstractCommand):
    def __init__(self, app: ExecutableApp, cmdstr: bytes | str) -> None:
        if isinstance(cmdstr, str):
            cmdstr = bytes(cmdstr, 'utf-8', errors='replace')
        self.app = app
        self.cmdstr = cmdstr
        self.status_line = None
        self.data = []

    def execute(self) -> bool:
        self.app.write(self.cmdstr + b'\n')

        while True:
            line = self.app.readline()
            if not line.startswith('data:'.encode('utf-8')):
                self.status_line = line.rstrip()
                result = self.app.readline().rstrip()
                return self.handle_result(result.decode('utf-8'))

            self.data.append(line[6:].rstrip('\n\r'.encode('utf-8')))

    def handle_result(self, result: str) -> bool:
        count = 0
        max_loop = 5
        while count < max_loop:
            try:
                if not result and self.cmdstr == b'Quit':
                    return True
                elif result.lower() == 'ok':
                    return True
                elif result.lower() != 'error':
                    raise ValueError(
                        f'"erro" esperado, mas recebido: {result}.'
                    )
                break
            except ValueError:
                sleep(1)
                count += 1

        msg = b'[sem mensagem de erro]'
        if self.data:
            msg = ''.encode('utf-8').join(self.data).rstrip()
        raise CommandError(msg.decode('utf-8'))


class Status:
    def __init__(self, status_line: str) -> None:
        if not status_line:
            status_line = (' ' * 12).encode('utf-8')
        self.status_line = status_line
        parts = status_line.split(' '.encode('utf-8'))

        self.keyboard = parts[0] or None
        self.screen_format = parts[1] or None
        self.field_protection = parts[2] or None
        self.connection_state = parts[3] or None
        self.emulator_mode = parts[4] or None
        self.model_number = parts[5] or None
        self.row_number = parts[6] or None
        self.col_number = parts[7] or None
        self.cursor_row = parts[8] or None
        self.cursor_col = parts[9] or None
        self.window_id = parts[10] or None
        self.exec_time = parts[11] or None

    def __str__(self) -> str:
        return f'Status: {self.status_line}'


class Wc3270App(ExecutableApp):
    args = ['-xrm', 'wc3270.unlockDelay: False']

    def __init__(self, model: MODEL_TYPE) -> None:
        self.args = self._get_executable_app_args(model)
        self.shell = True
        self.script_port = Wc3270App._get_free_port()

    @staticmethod
    def _get_free_port() -> str:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('127.0.0.1', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    @cache
    def _make_socket(self) -> None:
        self.socket = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        count = 0
        max_loop = 15
        while count < max_loop:
            try:
                sock.connect(('localhost', self.script_port))
                break
            except socket.error as e:
                if e.errno != errno.ECONNREFUSED:
                    raise NotConnectedException
                sleep(1)
                count += 1

        self.socket_fh = sock.makefile(mode='rwb')

    def connect(self, host: str) -> bool:
        self.args = [
            'start',
            '/wait',
            f'{BINARY_FOLDER}/wc3270',
        ] + self.args
        self.args.extend(['-scriptport', str(self.script_port), host])
        self._spawn_app()
        self._make_socket()
        return True

    def close(self) -> None:
        self.socket.close()

    def write(self, data: str) -> None:
        if self.socket_fh is None:
            raise NotConnectedException
        try:
            self.socket_fh.write(data)
            self.socket_fh.flush()
        except OSError:
            raise NotConnectedException

    def readline(self) -> bytes:
        if self.socket_fh is None:
            raise NotConnectedException
        return self.socket_fh.readline()


class Ws3270App(ExecutableApp):
    args = [f'{BINARY_FOLDER}/ws3270', '-xrm', 'ws3270.unlockDelay: False']


class X3270App(ExecutableApp):
    args = ['x3270', '-xrm', 'x3270.unlockDelay: False', '-script']


class S3270App(ExecutableApp):
    args = ['s3270', '-xrm', 's3270.unlockDelay: False']


class X3270Cmd(AbstractEmulatorCmd):
    def clear_screen(self) -> None:
        count = 0
        max_loop = 6
        while count < max_loop:
            self.clear()
            self.wait(5, 'unlock')
            if not self.get_full_screen(header=True).strip():
                break
            count += 1

    def send_pf(self, value: int) -> None:
        self.PF(value)
        self.wait(5, 'unlock')

    def wait_for_field(self, timeout: int = 30) -> None:
        self.wait(timeout, 'InputField')

    def wait_string_found(
        self,
        ypos: int,
        xpos: int,
        string: str,
        equal: bool = True,
        timeout: int = 3,
    ) -> bool:
        @run_timeout
        def _wait_loop():
            found = self.get_string(ypos, xpos, len(string))
            if equal:
                result = found == string
            else:
                result = found != string
            return result

        return _wait_loop(timeout)

    def string_found(self, ypos: int, xpos: int, string: str) -> bool:
        found = self.get_string(ypos, xpos, len(string))
        return found == string

    def delete_field(self) -> None:
        self.deletefield()

    def move_to(self, ypos: int, xpos: int) -> None:
        self.movecursor1(ypos, xpos)

    def send_string(
        self, tosend: str, ypos: int | None = None, xpos: int | None = None
    ) -> None:
        if xpos is not None and ypos is not None:
            self.move_to(ypos, xpos)
        tosend = re.sub(r"[()\"']", '', tosend)
        self.string(tosend)

    def send_enter(self) -> None:
        self.enter()
        self.wait(5, 'unlock')

    def send_home(self) -> None:
        self.home()
        self.wait(5, 'unlock')

    def get_string(self, ypos: int, xpos: int, length: int) -> str:
        self.check_limits(ypos, xpos)
        if (xpos + length) > (self.model_dimensions['columns'] + 1):
            raise FieldTruncateError
        xpos -= 1
        ypos -= 1
        return self.ascii(ypos, xpos, length)

    def get_string_area(
        self, yposi: int, xposi: int, ypose: int, xpose: int
    ) -> str:
        self.check_limits(yposi, xposi)
        self.check_limits(ypose, xpose)
        yposi -= 1
        xposi -= 1
        ypose -= 1
        ypose -= yposi
        xpose -= xposi
        return self.ascii(yposi, xposi, ypose, xpose)

    def get_full_screen(self, header: bool = True) -> str:
        text = self.ascii()
        if not header:
            start = (self.model_dimensions['columns'] - 1) * 2
            text = text[start:]
        return text

    def save_screen(self, file_path: str, file_name: str):
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        self.printtext('html', 'file', f'{file_path}\\{file_name}.html')

    def check_limits(self, ypos, xpos):
        if ypos > self.model_dimensions['rows']:
            raise FieldTruncateError(
                'Você excedeu o limite do eixo y da tela do mainframe'
            )
        if xpos > self.model_dimensions['columns']:
            raise FieldTruncateError(
                'Você excedeu o limite do eixo x da tela do mainframe'
            )

    def search_string(self, string: str, ignore_case: bool = False) -> bool:
        for ypos in range(1, self.model_dimensions['rows'] + 1):
            line = self.get_string(ypos, 1, self.model_dimensions['columns'])
            if ignore_case:
                string = string.lower()
                line = line.lower()
            if string in line:
                return True
        return False

    def get_string_positions(
        self, string: str, ignore_case=False
    ) -> list[tuple[int]]:
        screen_content = self.get_full_screen(header=True)
        flags = 0 if not ignore_case else re.IGNORECASE
        indices_object = re.finditer(re.escape(string), screen_content, flags)
        indices = [index.start() for index in indices_object]
        return [
            self._get_ypos_and_xpos_from_index(index + 1) for index in indices
        ]

    def _get_ypos_and_xpos_from_index(self, index):
        ypos = math.ceil(index / self.model_dimensions['columns'])
        remainder = index % self.model_dimensions['columns']
        if remainder == 0:
            xpos = self.model_dimensions['columns']
        else:
            xpos = remainder
        return (ypos, xpos)


class X3270(AbstractEmulator, X3270Cmd):
    def __init__(self, visible: bool = False, model: MODEL_TYPE = '2') -> None:
        self.model = model
        self.model_dimensions = MODEL_DIMENSIONS[model]
        self.visible = visible
        self.app: ExecutableApp = self._create_app()
        self.is_terminated = False
        self.host = None
        self.port = None
        self.tls = None

    def __getattr__(self, name):
        # Mapeamento de comandos com parâmetros e descrições
        if name in command_map:
            params, description = command_map[name]

            def command_func(*args, **kwargs):
                if len(args) + len(kwargs) < len(params):
                    raise CommandError(
                        f'Comando {name} espera {len(params)} parâmetro(s).'
                    )

                all_args = ', '.join(
                    list(map(str, args))
                    + [f'{k}={repr(v)}' for k, v in kwargs.items()]
                )
                cmd = self._exec_command(f'{name}({all_args})'.encode('utf8'))
                text = [text.decode('utf8') for text in cmd.data[0:]]
                return ''.join(text)

            params = {p[0:1] for p in params}
            command_func.__doc__ = (
                f'{name}: {description} parâmetros esperados: {params}'
            )

            return command_func
        elif 'send_pf' in name:

            def command_func(value: int | None = None):
                if not value:
                    value = int(name[-1])
                self._exec_command(f'PF({value})')
                self.wait(5, 'unlock')

            return command_func
        else:
            raise CommandError(f'Comando {name} não encontrado.')

    def _create_app(self) -> None:
        if os.name == 'nt':  # windows
            if self.visible:
                return Wc3270App(self.model)
            return Ws3270App(self.model)

        if self.visible:  # linux
            return X3270App(self.model)
        return S3270App(self.model)

    def _exec_command(self, cmdstr: str) -> Command:
        if self.is_terminated:
            raise TerminatedError
        cmd = Command(self.app, cmdstr)
        cmd.execute()
        self.status = Status(cmd.status_line)
        return cmd

    def terminate(self) -> None:
        if not self.is_terminated:
            try:
                self.quit()
            except BrokenPipeError:
                self.ignore()
            except socket.error as e:
                if e.errno != errno.ECONNRESET:
                    raise ConnectionError
        self.app.close()
        self.is_terminated = True

    def is_connected(self) -> bool:
        try:
            self.query('ConnectionState')
            return self.status.connection_state.startswith(b'C(')
        except Exception:
            return False

    def connect_host(self, host: str, port: str, tls: bool = True) -> None:
        self.host = host
        self.port = port
        self.tls = tls
        tls = 'L:Y:' if tls else ''
        strint_conn = f'{tls}{host}:{port}'
        try:
            if not self.app.connect(strint_conn):
                self.connect(strint_conn)
            self.wait(2, '3270mode')
        except CommandError:
            pass

    def reconnect_host(self) -> object:
        try:
            self.reconnect()
            return self
        except CommandError:
            self.terminate()
        except NotConnectedException:
            pass
        finally:
            args = self.host, self.port, self.tls
            new_instance = X3270(self.visible, self.model)
            new_instance.connect_host(*args)
            return new_instance
