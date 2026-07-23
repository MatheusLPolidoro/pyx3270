import os
import socket
import threading
from unittest import mock
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from pyx3270.cli import app, start_server_thread, start_sock

runner = CliRunner()

ADDRESS_PORT = 3270
CUSTOM_LOCAL_PORT = 4000


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


def test_record_without_local_port_defaults_to_address_port():
    """Sem --local-port, o comportamento não muda: a porta local de
    escuta continua sendo a mesma porta informada em --address."""
    x3270_mock = MagicMock()
    x3270_mock.connect_host = MagicMock(return_value=True)

    with mock.patch('pyx3270.cli.X3270', return_value=x3270_mock), mock.patch(
        'pyx3270.cli.start_server_thread',
        return_value=(MagicMock(), ADDRESS_PORT, MagicMock()),
    ) as mock_start_server_thread, mock.patch(
        'pyx3270.cli.control_replay', MagicMock(side_effect=KeyboardInterrupt)
    ), mock.patch('rich.print', MagicMock()):
        runner.invoke(
            app,
            [
                'record',
                '--address',
                'localhost:3270',
                '--directory',
                './screens',
                '--model',
                '2',
                '--emulator',
                '--tls',
            ],
        )

    call_kwargs = mock_start_server_thread.call_args.kwargs
    assert call_kwargs['port'] == ADDRESS_PORT
    # Sem --local-port, o fallback automático de porta fica habilitado --
    # é seguro trocar de porta, já que ela não foi escolhida explicitamente.
    assert call_kwargs['allow_port_fallback'] is True
    x3270_mock.connect_host.assert_called_once_with(
        'localhost', ADDRESS_PORT, True, mode_3270=True
    )


def test_record_local_port_overrides_listen_port():
    """--local-port desacopla a porta local de escuta da porta do host de
    origem (ex.: 992, que exige privilégio no Linux para escutar
    localmente), sem alterar a porta usada para conectar ao host real."""
    x3270_mock = MagicMock()
    x3270_mock.connect_host = MagicMock(return_value=True)

    with mock.patch('pyx3270.cli.X3270', return_value=x3270_mock), mock.patch(
        'pyx3270.cli.start_server_thread',
        return_value=(MagicMock(), CUSTOM_LOCAL_PORT, MagicMock()),
    ) as mock_start_server_thread, mock.patch(
        'pyx3270.cli.control_replay', MagicMock(side_effect=KeyboardInterrupt)
    ), mock.patch('rich.print', MagicMock()):
        runner.invoke(
            app,
            [
                'record',
                '--address',
                'mainframe.example.com:992',
                '--local-port',
                '4000',
                '--directory',
                './screens',
                '--model',
                '2',
                '--emulator',
                '--tls',
            ],
        )

    call_kwargs = mock_start_server_thread.call_args.kwargs
    assert call_kwargs['port'] == CUSTOM_LOCAL_PORT
    # --local-port é uma escolha explícita: se estiver bloqueada, deve
    # falhar com a mensagem clara, não trocar de porta silenciosamente.
    assert call_kwargs['allow_port_fallback'] is False
    x3270_mock.connect_host.assert_called_once_with(
        'localhost', CUSTOM_LOCAL_PORT, True, mode_3270=True
    )


def test_start_server_thread_binds_synchronously_before_returning():
    """O bind/listen (start_sock) deve acontecer antes de
    start_server_thread retornar, e não dentro da thread de aceitação --
    caso contrário, quem chama em seguida (ex.: emu.connect_host) pode
    tentar conectar antes do socket estar escutando."""
    port = 12345
    fake_sock = MagicMock()
    fake_sock.getsockname.return_value = ('0.0.0.0', port)
    with mock.patch(
        'pyx3270.cli.start_sock', return_value=fake_sock
    ) as mock_start_sock, mock.patch(
        'pyx3270.cli.threading.Thread'
    ) as mock_thread_class:
        mock_thread_instance = MagicMock()
        mock_thread_class.return_value = mock_thread_instance

        thread, actual_port, listen_sock = start_server_thread(
            port=port, handler=MagicMock(), handler_args=()
        )

    # A thread nunca executou seu target (start() foi mockado), então o
    # bind só pode ter acontecido no fluxo síncrono de start_server_thread.
    mock_start_sock.assert_called_once_with(port, allow_fallback=False)
    assert thread == mock_thread_instance
    assert actual_port == port
    assert listen_sock == fake_sock


def test_start_server_thread_exits_quietly_when_socket_closed():
    """Quando o socket de escuta é fechado de propósito (ex.: o loop de
    record()/replay() reiniciando e encerrando o listener anterior), a
    thread de aceitação deve sair quietamente -- não pode crashar com um
    OSError não tratado só porque o socket foi fechado por fora. (A
    thread termina nos dois casos, então checamos o excepthook para
    confirmar que o erro foi mesmo tratado, não só ignorado.)"""
    fake_sock = MagicMock()
    fake_sock.getsockname.return_value = ('0.0.0.0', 12345)
    fake_sock.accept.side_effect = OSError('Bad file descriptor')

    excepthook_calls = []
    original_excepthook = threading.excepthook
    threading.excepthook = excepthook_calls.append
    try:
        with mock.patch('pyx3270.cli.start_sock', return_value=fake_sock):
            thread, _actual_port, _listen_sock = start_server_thread(
                port=12345, handler=MagicMock(), handler_args=()
            )
            thread.join(timeout=2)
    finally:
        threading.excepthook = original_excepthook

    assert not thread.is_alive()
    assert excepthook_calls == []


def test_record_closes_previous_listener_before_reconnecting():
    """A cada reinício do loop de record() (usuário digitando 'S'), o
    listener anterior precisa ser fechado antes de abrir um novo --
    senão cada reconexão deixa um socket/thread de escuta órfão,
    escutando a mesma porta indefinidamente."""
    x3270_mock = MagicMock()
    x3270_mock.connect_host = MagicMock(return_value=True)

    first_sock = MagicMock()
    second_sock = MagicMock()

    with mock.patch('pyx3270.cli.X3270', return_value=x3270_mock), mock.patch(
        'pyx3270.cli.start_server_thread',
        side_effect=[
            (MagicMock(), ADDRESS_PORT, first_sock),
            (MagicMock(), ADDRESS_PORT, second_sock),
        ],
    ), mock.patch(
        'pyx3270.cli.control_replay',
        MagicMock(side_effect=[None, KeyboardInterrupt]),
    ), mock.patch('rich.print', MagicMock()):
        runner.invoke(
            app,
            [
                'record',
                '--address',
                'localhost:3270',
                '--directory',
                './screens',
                '--model',
                '2',
                '--emulator',
                '--tls',
            ],
        )

    first_sock.close.assert_called_once()
    second_sock.close.assert_not_called()


def test_start_sock_permission_error_raises_clear_message():
    """Falha de bind por falta de privilégio (comum em portas < 1024 no
    Linux, ex.: 992) deve virar uma mensagem clara, não um traceback cru,
    quando o fallback automático de porta não está habilitado."""
    with mock.patch('socket.socket') as mock_socket_class:
        mock_socket_instance = MagicMock()
        mock_socket_instance.bind.side_effect = PermissionError(
            13, 'Permission denied'
        )
        mock_socket_class.return_value = mock_socket_instance

        with pytest.raises(PermissionError, match='privilégio'):
            start_sock(992)

        mock_socket_instance.close.assert_called_once()
        mock_socket_instance.listen.assert_not_called()


def test_start_sock_falls_back_to_free_port_when_allowed():
    """Com allow_fallback=True, uma porta bloqueada por permissão (ex.:
    992 no Linux sem privilégio) não derruba o processo -- o socket cai
    para uma porta livre escolhida pelo SO (bind com porta 0)."""
    with mock.patch('socket.socket') as mock_socket_class:
        mock_socket_instance = MagicMock()
        mock_socket_instance.bind.side_effect = [
            PermissionError(13, 'Permission denied'),
            None,
        ]
        mock_socket_class.return_value = mock_socket_instance

        result = start_sock(992, allow_fallback=True)

        assert mock_socket_instance.bind.call_args_list == [
            mock.call(('', 992)),
            mock.call(('', 0)),
        ]
        mock_socket_instance.close.assert_not_called()
        mock_socket_instance.listen.assert_called_once_with(5)
        assert result == mock_socket_instance
