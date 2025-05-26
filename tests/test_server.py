import pytest
import socket
import os
from unittest.mock import MagicMock, patch, mock_open, call

from pyx3270 import server, tn3270
from pyx3270.emulator import X3270


_real_socket_class = socket.socket


def test_ensure_dir_exists(monkeypatch):
    """Testa ensure_dir quando o diretório já existe."""
    mock_isdir = MagicMock(return_value=True)
    mock_makedirs = MagicMock()
    monkeypatch.setattr(os.path, 'isdir', mock_isdir)
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)

    server.ensure_dir('/path/to/existing_dir')

    mock_isdir.assert_called_once_with('/path/to/existing_dir')
    mock_makedirs.assert_not_called()


def test_ensure_dir_creates(monkeypatch):
    """Testa ensure_dir quando o diretório não existe."""
    mock_isdir = MagicMock(return_value=False)
    mock_makedirs = MagicMock()
    monkeypatch.setattr(os.path, 'isdir', mock_isdir)
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)

    server.ensure_dir('/path/to/new_dir')

    mock_isdir.assert_called_once_with('/path/to/new_dir')
    mock_makedirs.assert_called_once_with('/path/to/new_dir')


def test_ensure_dir_no_path():
    """Testa ensure_dir com path vazio ou None."""
    # Não deve fazer nada nem levantar erro
    server.ensure_dir(None)
    server.ensure_dir('')


def test_is_screen_tn3270():
    """Testa a detecção de telas TN3270."""
    assert (
        server.is_screen_tn3270(b'\x00' * 99 + b'\x11') is False
    )  # Muito curto
    assert (
        server.is_screen_tn3270(b'\x00' * 101) is False
    )  # Sem byte de comando
    assert (
        server.is_screen_tn3270(b'\x00' * 100 + b'\x11') is True
    )  # Tamanho e byte OK
    assert (
        server.is_screen_tn3270(b'\x11' + b'\x00' * 100) is True
    )  # Byte no início


def test_load_screens_empty_dir(tmp_path, monkeypatch):
    """Testa load_screens com diretório vazio."""
    record_dir = tmp_path / 'records'
    record_dir.mkdir()
    mock_ensure_dir = MagicMock()
    monkeypatch.setattr(server, 'ensure_dir', mock_ensure_dir)

    screens = server.load_screens(str(record_dir))

    mock_ensure_dir.assert_called_once_with(str(record_dir))
    assert screens == []


def test_load_screens_with_files(tmp_path, monkeypatch):
    """Testa load_screens com arquivos .bin."""
    record_dir = tmp_path / 'records'
    record_dir.mkdir()
    # Cria arquivos de teste
    (record_dir / '001.bin').write_bytes(
        b'screen1_data' + tn3270.IAC + tn3270.TN_EOR
    )
    (record_dir / '000.bin').write_bytes(b'screen0_data')  # Sem EOR
    (record_dir / 'ignored.txt').write_text('ignore me')
    (record_dir / '002.bin').write_bytes(
        b'screen2_data' + tn3270.IAC + tn3270.TN_EOR
    )

    mock_ensure_dir = MagicMock()
    monkeypatch.setattr(server, 'ensure_dir', mock_ensure_dir)

    screens = server.load_screens(str(record_dir))

    mock_ensure_dir.assert_called_once_with(str(record_dir))
    assert len(screens) == 3
    # Verifica a ordem e o conteúdo (com EOR adicionado se necessário)
    assert screens[0] == b'screen0_data' + tn3270.IAC + tn3270.TN_EOR
    assert screens[1] == b'screen1_data' + tn3270.IAC + tn3270.TN_EOR
    assert screens[2] == b'screen2_data' + tn3270.IAC + tn3270.TN_EOR


def test_convert_s():
    """Testa a conversão de string hexadecimal com SF."""
    assert (
        server.convert_s('11C1C1 SF(C1=01, C2=02) 11C2C2')
        == '11C1C11D011D0211C2C2'
    )
    assert server.convert_s('SF(A=1, B=2, C=3)') == '1D11D21D3'
    assert server.convert_s('No SF here') == 'NoSFhere'
    assert server.convert_s('SF() Empty') == 'Empty'  # SF vazio é removido
    assert (
        server.convert_s('SF(X=10) 1234 SF(Y=20, Z=30)') == '1D1012341D201D30'
    )


@patch('socket.create_connection')
def test_connect_serversock_success(mock_create_conn):
    """Testa connect_serversock com sucesso."""
    mock_client_sock = MagicMock(spec=socket.socket)
    mock_server_sock = MagicMock(spec=socket.socket)
    mock_create_conn.return_value = mock_server_sock

    result_sock = server.connect_serversock(
        mock_client_sock, 'mainframe.com:3270'
    )

    mock_create_conn.assert_called_once_with(
        ('mainframe.com', 3270), timeout=5
    )
    assert result_sock == mock_server_sock
    mock_client_sock.close.assert_not_called()


@patch('socket.create_connection')
def test_connect_serversock_default_port(mock_create_conn):
    """Testa connect_serversock usando a porta padrão."""
    mock_client_sock = MagicMock(spec=socket.socket)
    mock_server_sock = MagicMock(spec=socket.socket)
    mock_create_conn.return_value = mock_server_sock

    result_sock = server.connect_serversock(mock_client_sock, 'onlyhost')

    mock_create_conn.assert_called_once_with(('onlyhost', 3270), timeout=5)
    assert result_sock == mock_server_sock


@patch('socket.create_connection')
def test_connect_serversock_failure(mock_create_conn):
    """Testa connect_serversock com falha na conexão."""
    mock_client_sock = MagicMock(spec=socket.socket)
    mock_create_conn.side_effect = socket.timeout('Connection timed out')

    result_sock = server.connect_serversock(mock_client_sock, 'badhost:1234')

    mock_create_conn.assert_called_once_with(('badhost', 1234), timeout=5)
    assert result_sock is None
    mock_client_sock.close.assert_called_once()


@patch('socket.socket')
def test_backend_3270_navigation(mock_socket_constructor):
    """Testa a navegação básica em backend_3270."""
    mock_clientsock = MagicMock(spec=_real_socket_class)
    # Simula recebimento de AID e dados de tecla pressionada
    mock_clientsock.recv.side_effect = [
        tn3270.ENTER,
        b'K\xe9\xff',  # Enter pressionado
        tn3270.PF3,
        b'K\xe9\xff',  # PF3 pressionado
        tn3270.PF8,
        b'K\xe9\xff',  # PF8 pressionado
        tn3270.CLEAR,
        b'K\xe9\xff',  # Clear pressionado
        tn3270.PF7,
        b'K\xe9\xff',  # PF7 pressionado (emulator=True)
        tn3270.PF4,
        b'K\xe9\xff',  # PF4 pressionado
        b'\x00',  # Simula fechamento do terminal para sair do loop
    ]
    screens = [b's0', b's1', b's2', b's3']

    # Teste 1: ENTER
    result = server.backend_3270(mock_clientsock, screens, 0, emulator=True)
    assert result == {'current_screen': 1, 'clear': False}

    # Teste 2: PF3
    result = server.backend_3270(mock_clientsock, screens, 1, emulator=True)
    assert result == {'current_screen': 0, 'clear': False}

    # Teste 3: PF8
    result = server.backend_3270(mock_clientsock, screens, 0, emulator=True)
    assert result == {'current_screen': 1, 'clear': False}

    # Teste 4: CLEAR
    result = server.backend_3270(mock_clientsock, screens, 1, emulator=True)
    assert result == {'current_screen': 1, 'clear': True}
    mock_clientsock.sendall.assert_called_with(tn3270.CLEAR_SCREEN_BUFFER)

    # Teste 5: PF7 (emulator=True)
    result = server.backend_3270(mock_clientsock, screens, 2, emulator=True)
    assert result == {'current_screen': 1, 'clear': False}

    # Teste 6: PF4
    result = server.backend_3270(mock_clientsock, screens, 1, emulator=True)
    assert result == {'current_screen': 2, 'clear': False}

    # Teste 7: Fechamento do terminal
    with pytest.raises(Exception, match=''):
        server.backend_3270(mock_clientsock, screens, 2, emulator=True)


@patch('socket.socket')
def test_backend_3270_timeout(mock_socket_constructor):
    """Testa backend_3270 com timeout no recv."""
    mock_clientsock = MagicMock(spec=_real_socket_class)
    mock_clientsock.recv.side_effect = [
        socket.timeout,
        tn3270.ENTER,
        b'K\xe9\xff',
    ]
    screens = [b's0', b's1']

    result = server.backend_3270(mock_clientsock, screens, 0, emulator=False)
    assert result == {'current_screen': 1, 'clear': False}
    assert mock_clientsock.recv.call_count == 3  # 1 timeout, 1 AID, 1 keypress


@patch('pyx3270.server.backend_3270')
def test_replay_handler(mock_backend, monkeypatch):
    """Testa o fluxo básico de replay_handler."""
    mock_clientsock = MagicMock(spec=_real_socket_class)
    screens = [b'screen0', b'screen1', b'screen2']
    # Simula a sequência de interações retornada por backend_3270
    mock_backend.side_effect = [
        {'current_screen': 0, 'clear': False},  # Inicial
        {'current_screen': 1, 'clear': False},  # Após interação 1
        {'current_screen': 1, 'clear': True},  # Após interação 2 (Clear)
        {'current_screen': 2, 'clear': False},  # Após interação 3
        Exception('Simulate loop break'),  # Para sair do loop
    ]

    server.replay_handler(mock_clientsock, screens, emulator=True)

    # Verifica chamadas
    mock_clientsock.sendall.assert_has_calls([
        call(b'\xff\xfd\x18\xff\xfb\x18'),  # handshake inicial
        call(screens[0]),  # inicial
        call(screens[0]),  # chamada extra repetida
        call(screens[1]),
        call(screens[2]),
    ])
    assert mock_backend.call_count == 5  # Chamado até a exceção
    mock_clientsock.close.assert_called_once()  # Garante que fechou no finally


@patch('pyx3270.server.connect_serversock')
@patch('pyx3270.server.ensure_dir')
@patch('select.select')
@patch('builtins.open', new_callable=mock_open)
@patch('os.path.join')
@patch('pyx3270.server.is_screen_tn3270')
def test_record_handler_basic_flow(
    mock_is_screen,
    mock_join,
    mock_open_func,
    mock_select,
    mock_ensure_dir,
    mock_connect_serversock,
):
    """Testa o fluxo básico de gravação em record_handler (sem TLS)."""
    mock_clientsock = MagicMock(spec=_real_socket_class, fileno=lambda: 3)
    mock_serversock = MagicMock(spec=_real_socket_class, fileno=lambda: 4)
    mock_connect_serversock.return_value = mock_serversock
    mock_emu = MagicMock(spec=X3270)
    mock_emu.tls = False  # Teste sem TLS
    record_dir = '/fake/dir'
    mock_join.side_effect = lambda *args: os.path.normpath('/'.join(args))

    # Dados simulados recebidos
    client_data = b'client_req' + tn3270.IAC + tn3270.TN_EOR
    server_data_screen1 = b'server_resp_screen1' + tn3270.IAC + tn3270.TN_EOR
    server_data_non_screen = b'server_non_screen_data'
    server_data_screen2 = b'server_resp_screen2' + tn3270.IAC + tn3270.TN_EOR

    # Configura select para retornar sockets e simular fim
    mock_select.side_effect = [
        ([mock_clientsock], [], []),  # Cliente envia
        ([mock_serversock], [], []),  # Servidor envia tela 1
        ([mock_serversock], [], []),  # Servidor envia dados não-tela
        ([mock_serversock], [], []),  # Servidor envia tela 2
        ConnectionResetError,  # Simula desconexão para parar o loop
    ]

    # Configura recv dos sockets
    mock_clientsock.recv.return_value = client_data
    mock_serversock.recv.side_effect = [
        server_data_screen1,
        server_data_non_screen,
        server_data_screen2,
    ]

    # Configura is_screen_tn3270
    mock_is_screen.side_effect = (
        lambda data: tn3270.IAC + tn3270.TN_EOR in data
    )

    server.record_handler(mock_emu, mock_clientsock, 'host:port', record_dir)

    # Verificações
    mock_connect_serversock.assert_called_once_with(
        mock_clientsock, 'host:port'
    )
    mock_ensure_dir.assert_called_once_with(record_dir)
    assert mock_select.call_count == 5

    # Verifica envios entre sockets
    mock_serversock.sendall.assert_called_once_with(client_data)
    mock_clientsock.sendall.assert_has_calls([
        call(server_data_screen1),
        call(server_data_non_screen),
        call(server_data_screen2),
    ])

    # Verifica gravação dos arquivos
    assert mock_join.call_count == 2  # Chamado para tela 1 e tela 2
    mock_open_func.assert_has_calls(
        [
            call(os.path.normpath('/fake/dir/000.bin'), 'wb'),
            call(os.path.normpath('/fake/dir/001.bin'), 'wb'),
        ],
        any_order=True,
    )

    # Verifica o conteúdo escrito (mock_open captura escritas)
    handle = mock_open_func()  # mock do arquivo aberto (mesmo para todos)

    # Obtem todas as chamadas ao write (argumentos escritos)
    write_calls = [
        call_args[0][0] for call_args in handle.write.call_args_list
    ]

    assert any(server_data_screen1 in w for w in write_calls), (
        'server_data_screen1 não foi escrito'
    )
    assert any(server_data_screen2 in w for w in write_calls), (
        'server_data_screen2 não foi escrito'
    )

    # Verifica fechamento dos sockets
    mock_clientsock.close.assert_called_once()
    mock_serversock.close.assert_called_once()


@patch('pyx3270.server.connect_serversock')
def test_record_handler_connect_fail(mock_connect_serversock):
    """Testa record_handler quando a conexão inicial falha."""
    mock_clientsock = MagicMock(spec=_real_socket_class)
    mock_connect_serversock.return_value = None  # Simula falha
    mock_emu = MagicMock(spec=X3270)

    server.record_handler(mock_emu, mock_clientsock, 'badhost:port', '/dir')

    mock_connect_serversock.assert_called_once_with(
        mock_clientsock, 'badhost:port'
    )
    # Não deve tentar fechar sockets ou fazer outras operações
    mock_clientsock.close.assert_not_called()  # connect_serversock já fecha o cliente
