import pytest
from unittest.mock import MagicMock, patch

from pyx3270.emulator import ExecutableApp, X3270


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
    # Usamos patch.object para mockar métodos da classe base abstrata se necessário
    with patch.object(
        ExecutableApp, '_spawn_app', return_value=None
    ), patch.object(
        ExecutableApp, '_get_executable_app_args', return_value=['dummy_args']
    ):
        app = ExecutableApp(shell=False, model='2')
        # Mockar métodos de leitura/escrita diretamente na instância mockada pelo popen
        app.subprocess = mock_subprocess_popen.return_value
        app.subprocess.stdout.readline.return_value = b'ok\n'
        yield app


@pytest.fixture
def x3270_emulator_instance(mock_executable_app_instance):
    """Fixture para uma instância de X3270 com app mockado."""
    # Mock _create_app para evitar a criação real do app na inicialização do X3270
    with patch.object(
        X3270, '_create_app', return_value=None
    ) as mock_create_app:
        emulator = X3270(visible=False, model='3')
        # Atribui manualmente o app mockado (já que _create_app está mockado)
        emulator.app = mock_executable_app_instance
        # Mocka o método principal de execução de comandos
        emulator._exec_command = MagicMock()
        yield emulator


@pytest.fixture
def x3270_cmd_instance(x3270_emulator_instance):
    """Fixture para uma instância de X3270Cmd associada a um X3270 mockado."""
    # X3270Cmd é frequentemente instanciado dentro de X3270, mas podemos criar um
    # diretamente para teste, passando o emulador mockado.
    # No entanto, a classe X3270Cmd herda de X3270, então a fixture anterior já serve.
    # Apenas garantimos que o _exec_command está mockado.
    x3270_emulator_instance._exec_command.reset_mock()  # Reseta o mock para cada teste
    return x3270_emulator_instance  # Retorna a instância do emulador que também é o Cmd
