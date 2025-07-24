import socket
from unittest import mock
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from pyx3270.cli import app, start_sock

runner = CliRunner()


@patch('pyx3270.cli.start_new_amulator')
@patch('pyx3270.cli.load_screens')
@patch('pyx3270.cli.start_sock')
@patch('pyx3270.cli.X3270')
@patch('pyx3270.cli.threading.Thread')
def test_replay_command(
    mock_thread_class,
    mock_x3270_class,
    mock_start_sock,
    mock_load_screens,
    mock_start_new_amulator,
):
    # Mock do load_screens
    mock_load_screens.return_value = ['tela1.bin', 'tela2.bin']

    # Mock do socket retornado por start_sock
    mock_socket = MagicMock()
    mock_clientsock = MagicMock()

    # Cria uma função que simula uma chamada e depois lança KeyboardInterrupt
    def accept_side_effect():
        yield (mock_clientsock, ('127.0.0.1', 12345))
        while True:
            raise KeyboardInterrupt('encerrar')

    mock_socket.accept.side_effect = accept_side_effect()
    mock_start_sock.return_value = mock_socket

    # Mock do X3270
    mock_emu_instance = MagicMock()
    mock_x3270_class.return_value = mock_emu_instance

    mock_thread = MagicMock()
    mock_thread_class.return_value = mock_thread

    # Simula o join como se a thread tivesse terminado
    mock_thread.join.return_value = None

    # Execução do comando
    result = runner.invoke(
        app, ['replay', '--directory=tests/screens', '--port=9999']
    )

    # Asserts
    assert result.exit_code == 0
    mock_load_screens.assert_called_once_with('tests/screens')
    mock_start_sock.assert_called_once_with(9999)
    mock_x3270_class.assert_called_once_with(
        visible=True, model='2', save_log_file=True
    )
    mock_thread.start.assert_called_once()
    mock_start_new_amulator.assert_called_once_with(
        mock_thread, mock_emu_instance
    )


@patch('pyx3270.cli.start_new_amulator')
@patch('pyx3270.cli.start_sock')
@patch('pyx3270.cli.X3270')
@patch('pyx3270.cli.threading.Thread')
def test_record_command(
    mock_thread_class,
    mock_x3270_class,
    mock_start_sock,
    mock_start_new_amulator,
    mock_socket_with_accept,
):
    # Preparar mocks de socket e cliente
    mock_socket, mock_clientsock = mock_socket_with_accept
    mock_start_sock.return_value = mock_socket

    # Mock da instância do X3270
    mock_emu_instance = MagicMock()
    mock_x3270_class.return_value = mock_emu_instance

    # Mock da thread
    mock_thread = MagicMock()
    mock_thread_class.return_value = mock_thread
    mock_thread.join.return_value = None

    # Invoca o comando record com parâmetros
    result = runner.invoke(
        app,
        [
            'record',
            '--address',
            'host.local:1234',
            '--directory',
            'tests/screens',
            '--no-tls',  # desliga o TLS, pois o padrão é True
            '--model',
            '2',
            '--emulator',  # habilita emulator (padrão True, mas forçando aqui)
        ],
    )

    # Validar saída e chamadas
    if result.exit_code == 130:  # noqa: PLR2004
        assert isinstance(result.exception, SystemExit)
    else:
        assert result.exit_code == 0

    mock_start_sock.assert_called_once_with(1234)
    mock_x3270_class.assert_called_once_with(
        visible=True, model='2', save_log_file=True
    )
    mock_emu_instance.connect_host.assert_called_once_with(
        'localhost', 1234, False, mode_3270=False
    )
    mock_thread_class.assert_called_once()
    mock_thread.start.assert_called_once()
    mock_start_new_amulator.assert_called_once_with(
        mock_thread, mock_emu_instance
    )


def test_start_sock():
    with mock.patch('socket.socket') as mock_socket_class:
        mock_socket_instance = mock.MagicMock()
        mock_socket_class.return_value = mock_socket_instance

        port = 12345
        result = start_sock(port)

        # Verifica criação do socket com os parâmetros corretos
        mock_socket_class.assert_called_once_with(
            socket.AF_INET, socket.SOCK_STREAM
        )

        # Verifica setsockopt chamado com os parâmetros certos
        mock_socket_instance.setsockopt.assert_called_once_with(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )

        # Verifica bind chamado com ('', port)
        mock_socket_instance.bind.assert_called_once_with(('', port))

        # Verifica listen chamado com backlog 5
        mock_socket_instance.listen.assert_called_once_with(5)

        # Verifica que a função retornou a instância de socket criada
        assert result == mock_socket_instance
