import socket
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pyx3270.emulator import X3270, ExecutableApp

_real_socket_class = socket.socket


@pytest.fixture
def record_mocks():
    with ExitStack() as stack:
        # Patches no módulo 'pyx3270.server'
        connect_serversock = stack.enter_context(
            patch('pyx3270.server.connect_serversock')
        )
        ensure_dir = stack.enter_context(patch('pyx3270.server.ensure_dir'))
        is_screen = stack.enter_context(
            patch('pyx3270.server.is_screen_tn3270')
        )

        # Patches fora do server.py
        mock_select = stack.enter_context(patch('select.select'))
        mock_open_func = stack.enter_context(
            patch('builtins.open', new_callable=mock_open)
        )
        mock_join = stack.enter_context(patch('os.path.join'))

        mocks = SimpleNamespace(
            clientsock=MagicMock(spec=_real_socket_class, fileno=lambda: 3),
            serversock=MagicMock(spec=_real_socket_class, fileno=lambda: 4),
            connect_serversock=connect_serversock,
            ensure_dir=ensure_dir,
            is_screen=is_screen,
            select=mock_select,
            open_func=mock_open_func,
            join=mock_join,
        )

        yield mocks


@pytest.fixture
def mock_subprocess_popen(autouse=True):
    """Fixture para mockar subprocess.Popen."""
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.stdin = MagicMock()
        mock_process.stdout = MagicMock()
        mock_process.stderr = MagicMock()
        mock_process.poll.return_value = None
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def mock_socket(autouse=True):
    """Fixture para mockar socket.socket e funções relacionadas."""
    with patch('socket.socket') as mock_socket_constructor:
        mock_sock_instance = MagicMock()
        mock_sock_instance.connect.return_value = None
        mock_sock_instance.makefile.return_value = MagicMock()
        mock_sock_instance.close.return_value = None
        mock_sock_instance.getsockname.return_value = ('127.0.0.1', 54321)
        mock_socket_constructor.return_value = mock_sock_instance
        with patch('socket.getaddrinfo'), patch('socket.gethostname'):
            yield mock_socket_constructor


@pytest.fixture
def mock_os_name(monkeypatch):
    """Fixture para mockar os.name."""
    monkeypatch.setattr('os.name', 'posix')


@pytest.fixture
def mock_executable_app_instance(mock_subprocess_popen):
    """Fixture para uma instância mockada de ExecutableApp."""
    with patch.object(
        ExecutableApp, '_spawn_app', return_value=None
    ), patch.object(
        ExecutableApp, '_get_executable_app_args', return_value=['dummy_args']
    ):
        app = ExecutableApp(shell=False, model='2')
        app.subprocess = mock_subprocess_popen.return_value
        app.subprocess.stdout.readline.return_value = b'ok\n'
        yield app


@pytest.fixture
def x3270_emulator_instance(mock_executable_app_instance):
    """Fixture para uma instância de X3270 com app mockado."""
    with patch.object(X3270, '_create_app', return_value=None):
        emulator = X3270(visible=False, model='3', )
        # Atribui manualmente o app mockado (já que _create_app está mockado)
        emulator.app = mock_executable_app_instance
        # Mocka o método principal de execução de comandos
        emulator._exec_command = MagicMock()
        yield emulator


@pytest.fixture
def x3270_cmd_instance(x3270_emulator_instance):
    """Fixture para uma instância de X3270Cmd associada a um X3270 mockado."""
    # Reseta o mock para cada teste
    x3270_emulator_instance._exec_command.reset_mock()
    # Retorna a instância do emulador que também é o Cmd
    return x3270_emulator_instance
