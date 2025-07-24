import os
import socket
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import pytest

from pyx3270 import server, tn3270
from pyx3270.emulator import X3270
from pyx3270.server import ReplayState, process_command

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

    screens = server.load_screens_basic(str(record_dir))
    mock_ensure_dir.assert_called_once_with(str(record_dir))
    assert screens == dict()


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

    screens = server.load_screens_basic(str(record_dir))
    screens_list = list(screens.values())

    mock_ensure_dir.assert_called_once_with(str(record_dir))
    EXPECTED_FILES = {'000', '001', '002'}
    assert set(screens.keys()) == EXPECTED_FILES
    assert len(screens_list) == len(EXPECTED_FILES)
    # Verifica a ordem e o conteúdo (com EOR adicionado se necessário)
    assert screens_list[0] == b'screen0_data' + tn3270.IAC + tn3270.TN_EOR
    assert screens_list[1] == b'screen1_data' + tn3270.IAC + tn3270.TN_EOR
    assert screens_list[2] == b'screen2_data' + tn3270.IAC + tn3270.TN_EOR


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
    screens = {'s0': b's0', 's1': b's1', 's2': b's2', 's3': b's3'}

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
    mock_clientsock.recv.side_effect = [b'']
    with pytest.raises(ConnectionResetError, match='Terminal fechado.'):
        server.backend_3270(mock_clientsock, screens, 2, emulator=True)


@patch('socket.socket')
def test_backend_3270_timeout(mock_socket_constructor):
    """Testa backend_3270 com timeout no recv."""
    EXPECTED_CALLS = 3
    mock_clientsock = MagicMock(spec=_real_socket_class)
    mock_clientsock.recv.side_effect = [
        socket.timeout,
        tn3270.ENTER,
        b'K\xe9\xff',
    ]
    screens = {'s0': b's0', 's1': b's1'}

    result = server.backend_3270(mock_clientsock, screens, 0, emulator=False)
    assert result == {'current_screen': 0, 'clear': False}
    assert mock_clientsock.recv.call_count == EXPECTED_CALLS


@patch('pyx3270.server.backend_3270')
def test_replay_handler(mock_backend, monkeypatch):
    """Testa o fluxo básico de replay_handler."""
    mock_clientsock = MagicMock(spec=_real_socket_class)
    screens = {
        'screen0': b'screen0',
        'screen1': b'screen1',
        'screen2': b'screen2',
    }
    screens_list = list(screens.values())
    # Simula a sequência de interações retornada por backend_3270
    mock_backend.side_effect = [
        {'current_screen': 0, 'clear': False},  # Inicial
        {'current_screen': 1, 'clear': False},  # Após interação 1
        {'current_screen': 1, 'clear': True},  # Após interação 2 (Clear)
        {'current_screen': 2, 'clear': False},  # Após interação 3
        Exception('Simulate loop break'),  # Para sair do loop
    ]

    server.replay_handler(
        mock_clientsock, screens, emulator=True, base_directory='./screens'
    )

    # Verifica chamadas
    mock_clientsock.sendall.assert_has_calls([
        call(b'\xff\xfd\x18\xff\xfb\x18'),  # handshake inicial
        call(screens_list[0]),  # inicial
        call(screens_list[0]),  # chamada extra repetida
        call(screens_list[1]),
        call(screens_list[2]),
    ])
    EXPECTED_CALLS = 5
    assert mock_backend.call_count == EXPECTED_CALLS  # Chamado até a exceção
    mock_clientsock.close.assert_called_once()  # Garante que fechou no finally


def test_record_handler_basic_flow(record_mocks):
    """Testa o fluxo básico de gravação em record_handler (sem TLS)."""
    mock_clientsock = record_mocks.clientsock
    mock_serversock = record_mocks.serversock
    record_mocks.connect_serversock.return_value = mock_serversock
    mock_emu = MagicMock(spec=X3270)
    mock_emu.tls = False  # Teste sem TLS
    record_dir = '/fake/dir'
    record_mocks.join.side_effect = lambda *args: os.path.normpath(
        '/'.join(args)
    )

    # Dados simulados recebidos
    client_data = b'client_req' + tn3270.IAC + tn3270.TN_EOR
    server_data_screen1 = b'server_resp_screen1' + tn3270.IAC + tn3270.TN_EOR
    server_data_non_screen = b'server_non_screen_data'
    server_data_screen2 = b'server_resp_screen2' + tn3270.IAC + tn3270.TN_EOR

    # Configura select para retornar sockets e simular fim
    record_mocks.select.side_effect = [
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
    record_mocks.is_screen.side_effect = (
        lambda data: tn3270.IAC + tn3270.TN_EOR in data
    )

    server.record_handler(mock_emu, mock_clientsock, 'host:992', record_dir)

    # Verificações
    record_mocks.connect_serversock.assert_called_once_with(
        mock_clientsock, 'host:992'
    )

    record_mocks.ensure_dir.assert_called_once_with(record_dir)
    EXPECTED_CALLS = 5
    assert record_mocks.select.call_count == EXPECTED_CALLS

    # Verifica envios entre sockets
    mock_serversock.sendall.assert_called_once_with(client_data)
    mock_clientsock.sendall.assert_has_calls([
        call(server_data_screen1),
        call(server_data_non_screen),
        call(server_data_screen2),
    ])

    # Verifica gravação dos arquivos
    # Chamado para tela 1 e tela 2
    EXPECTED_CALLS = 2
    assert record_mocks.join.call_count == EXPECTED_CALLS
    record_mocks.open_func.assert_has_calls(
        [
            call(os.path.normpath('/fake/dir/000.bin'), 'wb'),
            call(os.path.normpath('/fake/dir/001.bin'), 'wb'),
        ],
        any_order=True,
    )

    # Verifica o conteúdo escrito (mock_open captura escritas)
    handle = (
        record_mocks.open_func()
    )  # mock do arquivo aberto (mesmo para todos)

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
    mock_clientsock.close.assert_not_called()


def test_load_screens_calls_ensure_dir(monkeypatch, tmp_path):
    record_dir = str(tmp_path)

    mock_ensure_dir = MagicMock()
    monkeypatch.setattr(server, 'ensure_dir', mock_ensure_dir)
    # Forçar que haja arquivos .bin para evitar o fallback
    monkeypatch.setattr(
        server.os, 'listdir', MagicMock(return_value=['file.bin'])
    )
    monkeypatch.setattr(
        server.os,
        'walk',
        MagicMock(return_value=[(record_dir, [], ['file.bin'])]),
    )
    monkeypatch.setattr(
        server, 'tn3270', MagicMock(IAC=b'\xff', TN_EOR=b'\xef')
    )

    open_mock = MagicMock()
    open_mock.return_value.__enter__.return_value.read.return_value = (
        b'data' + server.tn3270.IAC + server.tn3270.TN_EOR
    )
    m = mock_open(read_data=b'data' + server.tn3270.IAC + server.tn3270.TN_EOR)
    monkeypatch.setattr('builtins.open', m)

    server.load_screens(record_dir)

    mock_ensure_dir.assert_called_once_with(record_dir)


def test_load_screens_fallback_to_load_screens_basic(monkeypatch):
    record_dir = '/fake/dir'

    monkeypatch.setattr(server, 'ensure_dir', MagicMock())
    monkeypatch.setattr(
        server.os, 'listdir', MagicMock(return_value=['file.txt', 'other.dat'])
    )
    mock_load_basic = MagicMock(return_value={'basic': 'screens'})
    monkeypatch.setattr(server, 'load_screens_basic', mock_load_basic)

    result = server.load_screens(record_dir)

    mock_load_basic.assert_called_once_with(server.BINARY_FOLDER)
    assert result == {'basic': 'screens'}


def test_load_screens_logs_error_and_returns_empty(monkeypatch):
    record_dir = '/fake/dir'

    # Forçar ensure_dir sem efeitos
    monkeypatch.setattr(server, 'ensure_dir', MagicMock())

    # Forçar que listdir lance exceção para simular erro
    def raise_os_error(_):
        raise OSError('fail')

    monkeypatch.setattr(server.os, 'listdir', raise_os_error)

    mock_logger = MagicMock()
    monkeypatch.setattr(server, 'logger', mock_logger)

    result = server.load_screens(record_dir)

    mock_logger.error.assert_called_once_with(
        f'Falha ao carregar caminho: {record_dir}'
    )
    assert result == {}


def test_find_directory_finds_match():
    base_dir = '/fake/base'
    search_name = 'testdir'

    # Simula listdir retornando vários nomes
    mock_listdir = ['OtherDir', 'TestDir123', 'anotherdir']

    # Simula isdir para retornar True apenas para 'TestDir123' e 'OtherDir'
    def mock_isdir(path):
        return path.endswith('TestDir123') or path.endswith('OtherDir')

    with patch('os.listdir', return_value=mock_listdir), patch(
        'os.path.isdir', side_effect=mock_isdir
    ):
        found = server.find_directory(base_dir, search_name)

    expected_path = os.path.join(base_dir, 'TestDir123')
    assert found == expected_path


def test_find_directory_skips_non_dirs():
    base_dir = '/fake/base'
    search_name = 'nomatch'

    mock_listdir = ['file.txt', 'notadir', 'maybeadir']

    # Só 'maybeadir' é diretório
    def mock_isdir(path):
        return path.endswith('maybeadir')

    with patch('os.listdir', return_value=mock_listdir), patch(
        'os.path.isdir', side_effect=mock_isdir
    ):
        found = server.find_directory(base_dir, search_name)

    # Não encontrou, deve retornar None
    assert found is None


def test_find_directory_returns_none_when_no_match():
    base_dir = '/fake/base'
    search_name = 'absent'

    mock_listdir = ['DirOne', 'DirTwo']

    # Todos são diretórios
    def mock_isdir(path):
        return True

    with patch('os.listdir', return_value=mock_listdir), patch(
        'os.path.isdir', side_effect=mock_isdir
    ):
        found = server.find_directory(base_dir, search_name)

    assert found is None


def test_handle_set_found():
    screens = {
        'SCREEN1': b'data1',
        'SCREEN2': b'data2',
        'OTHER': b'data3',
    }
    command = 'set screen2'

    result = server.handle_set(command, screens)
    assert result == 1  # índice de 'SCREEN2'


def test_handle_set_not_found():
    screens = {
        'SCREEN1': b'data1',
        'SCREEN2': b'data2',
    }
    command = 'set nonexistent'

    result = server.handle_set(command, screens)
    assert result is None


@patch('pyx3270.server.logger')
def test_handle_add_valid(mock_logger):
    screens = {}
    screens_list = []

    # Compose a hex string for simple bytes 'ABC' (hex 41 42 43)
    hex_data = '414243'
    command = f'add newscreen {hex_data}'

    server.handle_add(command, screens, screens_list)

    expected_bytes = (
        tn3270.START_SCREEN
        + bytes.fromhex(hex_data)
        + tn3270.IAC
        + tn3270.TN_EOR
    )

    # Verifica se a tela foi adicionada no dict e na lista
    assert 'NEWSCREEN' in screens
    assert screens['NEWSCREEN'] == expected_bytes
    assert expected_bytes in screens_list

    # Logger warning não deve ser chamado
    mock_logger.warning.assert_not_called()


@patch('pyx3270.server.logger')
def test_handle_add_invalid_format(mock_logger):
    screens = {}
    screens_list = []

    # Comando com formato inválido (falta argumento)
    command = 'add invalidcommand'

    server.handle_add(command, screens, screens_list)

    # Nenhuma tela deve ter sido adicionada
    assert screens == {}
    assert screens_list == []

    # Logger deve ter sido chamado com warning
    mock_logger.warning.assert_called_once_with(
        '[!] Formato inválido ao adicionar tela'
    )


@pytest.mark.parametrize(
    ('command', 'expected_screen', 'expected_clear', 'should_close'),
    [
        ('set TELA', 1, False, False),
        ('add TELA 00ff', 0, False, False),
        ('change directory teste', 0, False, False),
        ('next', 1, False, False),
        ('prev', 0, False, False),
        ('clear', 0, True, False),
        ('q', 0, False, True),
        ('comando_invalido', 0, False, False),
    ],
)
def test_process_command(
    command, expected_screen, expected_clear, should_close
):
    # Setup mocks e estado
    mock_socket = Mock()

    mock_screens = {'TELA_PRINCIPAL': b'tela1', 'OUTRA_TELA': b'tela2'}
    # Dados fictícios para inicialização
    screens = {'TELA': 'conteúdo fictício'}
    screens_list = ['TELA']
    current_screen = 0
    clear = False

    state = ReplayState(screens, screens_list, current_screen, clear)
    state.screens = mock_screens
    state.screens_list = list(mock_screens.values())
    state.current_screen = 0
    state.clear = False

    with patch('pyx3270.server.handle_set', return_value=1) as mock_set, patch(
        'pyx3270.server.handle_add'
    ) as mock_add, patch(
        'pyx3270.server.handle_change_directory',
        return_value=(mock_screens, list(mock_screens.values())),
    ) as mock_change:
        result_state = process_command(command, mock_socket, 'base', state)

        # Checagens
        assert result_state.current_screen == expected_screen
        assert result_state.clear == expected_clear

        if should_close:
            mock_socket.close.assert_called_once()
        else:
            mock_socket.close.assert_not_called()

        if command == 'clear':
            mock_socket.sendall.assert_called_once_with(
                tn3270.CLEAR_SCREEN_BUFFER
            )
        else:
            mock_socket.sendall.assert_not_called()

        if command.startswith('set '):
            mock_set.assert_called_once()
        else:
            mock_set.assert_not_called()

        if command.startswith('add '):
            mock_add.assert_called_once()
        else:
            mock_add.assert_not_called()

        if command.startswith('change directory '):
            mock_change.assert_called_once()
        else:
            mock_change.assert_not_called()
