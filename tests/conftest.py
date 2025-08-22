import socket
import os
import threading
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pyx3270 import cli, server
from pyx3270.emulator import X3270, ExecutableApp

_real_socket_class = socket.socket


@pytest.fixture(autouse=True)
def no_os_exit(monkeypatch):
    def fake_exit(code=0):
        raise SystemExit(code)  # deixa o pytest lidar normalmente
    monkeypatch.setattr(os, "_exit", fake_exit)


@pytest.fixture
def mock_socket_with_accept():
    """
    Retorna uma tupla (mock_socket, mock_clientsock)
    mock_socket.accept() na primeira chamada retorna (mock_clientsock, addr),
    na segunda chamada levanta KeyboardInterrupt para parar o loop.
    """
    mock_socket = MagicMock()
    mock_clientsock = MagicMock()

    def accept_side_effect():
        yield (mock_clientsock, ('127.0.0.1', 12345))
        while True:
            raise KeyboardInterrupt('encerrar')

    mock_socket.accept.side_effect = accept_side_effect()
    return mock_socket, mock_clientsock


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
        emulator = X3270(
            visible=False,
            model='3',
        )
        # Atribui manualmente o app mockado (já que _create_app está mockado)
        emulator.app = mock_executable_app_instance
        # Mocka o método principal de execução de comandos
        emulator._exec_command = MagicMock()
        yield emulator


@pytest.fixture
def x3270_real_exec_instance(mock_executable_app_instance):
    """Instância de X3270 com app mockado e Command mockado."""
    with patch.object(X3270, '_create_app', return_value=None):
        emulator = X3270(
            visible=False,
            model='3',
        )
        # Atribui manualmente o app mockado (já que _create_app está mockado)
        emulator.app = mock_executable_app_instance

        # Patch de Command no namespace do módulo pyx3270.emulator
        with patch('pyx3270.emulator.Command') as mock_command_class:
            mock_instance = MagicMock()
            mock_instance.execute.return_value = True
            mock_command_class.return_value = mock_instance

            yield emulator


@pytest.fixture
def x3270_cmd_instance(x3270_emulator_instance):
    """Fixture para uma instância de X3270Cmd associada a um X3270 mockado."""
    # Reseta o mock para cada teste
    x3270_emulator_instance._exec_command.reset_mock()
    # Retorna a instância do emulador que também é o Cmd
    return x3270_emulator_instance


@pytest.fixture
def record_dependencies():
    deps = SimpleNamespace(
        x3270=MagicMock(),
        server_thread=MagicMock(),
        address='localhost:3270',
        directory='./screens',
        tls=True,
        model='2',
        rich_print=MagicMock(),
        sys_exit=MagicMock(),
        control_replay=MagicMock(side_effect=KeyboardInterrupt),
    )

    # Patches globais dentro da fixture
    with patch('pyx3270.cli.X3270', return_value=deps.x3270), patch(
        'pyx3270.cli.start_server_thread', return_value=deps.server_thread
    ), patch('pyx3270.cli.control_replay', deps.control_replay), patch(
        'rich.print', deps.rich_print
    ):
        yield deps


@pytest.fixture
def replay_dependencies(tmp_path, monkeypatch):
    # Cria diretório e arquivo de teste para screens
    screens_dir = tmp_path / 'screens'
    screens_dir.mkdir()
    (screens_dir / '001.bin').write_bytes(
        b'\x11' * 200 + server.tn3270.IAC + server.tn3270.TN_EOR
    )

    # Configura valores padrões
    directory = str(screens_dir)
    port = 12345
    model = '2'
    tls = False

    # Mocks
    x3270_mock = type(
        'X3270Mock', (), {'connect_host': lambda self, *a, **kw: None}
    )()

    def control_replay_mock(th):
        # levanta KeyboardInterrupt quando chamado
        raise KeyboardInterrupt

    # Monkeypatch no módulo
    monkeypatch.setattr(cli, 'X3270', lambda *a, **kw: x3270_mock)
    monkeypatch.setattr(cli, 'start_command_process', lambda: None)
    monkeypatch.setattr(cli, 'control_replay', control_replay_mock)

    # Monkeypatch para não abrir socket de verdade
    def fake_start_server_thread(*args, **kwargs):
        thread = threading.Thread(target=lambda: None, daemon=True)
        thread.start()
        return thread

    monkeypatch.setattr(cli, 'start_server_thread', fake_start_server_thread)

    # Monkeypatch do rich.print para capturar chamadas
    printed_messages = []
    monkeypatch.setattr(
        cli.rich, 'print', lambda msg, **kwargs: printed_messages.append(msg)
    )

    # Retorna todos os valores úteis para o teste
    return dict(
        directory=directory,
        port=port,
        model=model,
        tls=tls,
        printed_messages=printed_messages,
        x3270_mock=x3270_mock,
    )
