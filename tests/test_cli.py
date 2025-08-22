import os
import socket
from unittest import mock
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from pyx3270.cli import app, start_sock

runner = CliRunner()


@pytest.mark.parametrize('emulator', [True, False])
def test_replay(monkeypatch, emulator, replay_dependencies):
    deps = replay_dependencies

    args = [
        'replay',
        '--directory',
        deps['directory'],
        '--port',
        str(deps['port']),
        '--model',
        deps['model'],
    ]
    args.append('--emulator' if emulator else '--no-emulator')
    args.append('--tls' if deps['tls'] else '--no-tls')

    runner = CliRunner()
    result = runner.invoke(app, args)

    # Typer encerra o app com SystemExit
    assert result.exit_code != 0

    # Verifica se a mensagem de REPLAY apareceu
    assert any(
        f'[+] REPLAY do caminho: {deps["directory"]}' in m
        for m in deps['printed_messages']
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
        if os.name != 'nt':
            calls = mock_socket_instance.setsockopt.call_args_list
            assert calls[0] == mock.call.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )
            assert calls[1] == mock.call.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEPORT, 1
            )
        else:
            mock_socket_instance.setsockopt.assert_called_once_with(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )

        # Verifica bind chamado com ('', port)
        mock_socket_instance.bind.assert_called_once_with(('', port))

        # Verifica listen chamado com backlog 5
        mock_socket_instance.listen.assert_called_once_with(5)

        # Verifica que a função retornou a instância de socket criada
        assert result == mock_socket_instance


@pytest.mark.parametrize('emulator', [True, False])
def test_record(emulator, record_dependencies):
    deps = record_dependencies

    # Mock do connect_host se emulador estiver ativo
    if emulator:
        deps.x3270.connect_host = MagicMock(return_value=True)

    # Executa o comando via Typer runner
    args = [
        'record',
        '--address',
        deps.address,
        '--directory',
        deps.directory,
        '--model',
        deps.model,
    ]
    if emulator:
        args.append('--emulator')
    else:
        args.append('--no-emulator')
    if deps.tls:
        args.append('--tls')
    else:
        args.append('--no-tls')

    runner.invoke(app, args)

    if emulator:
        deps.x3270.connect_host.assert_called()
    deps.control_replay.assert_called()
