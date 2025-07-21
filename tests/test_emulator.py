import os
import socket
import subprocess
from itertools import count
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

from pyx3270.emulator import (
    X3270,
    AbstractEmulator,
    AbstractEmulatorCmd,
    AbstractExecutableApp,
    Command,
    CommandError,
    ExecutableApp,
    S3270App,
    Status,
    Wc3270App,
    Ws3270App,
    X3270App,
    X3270Cmd,
)


# Testes de herança existentes
def test_x3270_implements_abstract():
    assert issubclass(X3270, AbstractEmulator)
    assert issubclass(X3270Cmd, AbstractEmulatorCmd)


def test_executable_app_implements_abstract():
    assert issubclass(ExecutableApp, AbstractExecutableApp)


def test_app_implements_executable_app():
    assert issubclass(Wc3270App, ExecutableApp)
    assert issubclass(Ws3270App, ExecutableApp)
    assert issubclass(X3270App, ExecutableApp)
    assert issubclass(S3270App, ExecutableApp)


@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_os_name')
def test_executable_app_init_spawn(mock_subprocess_popen, monkeypatch):
    """Testa se ExecutableApp.__init__ chama _spawn_app corretamente."""
    # Simula OS Posix (Linux/macOS)
    monkeypatch.setattr(os, 'name', 'posix')
    ExecutableApp(shell=False, model='2')
    mock_subprocess_popen.assert_called_once()
    args, kwargs = mock_subprocess_popen.call_args
    assert args[0] == ['-xrm', '"*model: 2"', '-localcp', 'utf8', '-utf8']
    assert kwargs['shell'] is False
    assert kwargs['start_new_session'] is True
    assert 'creationflags' not in kwargs


@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_os_name')
def test_executable_app_init_spawn_windows(mock_subprocess_popen, monkeypatch):
    """Testa se ExecutableApp.__init__ usa creationflags no Windows."""
    # Simula OS Windows
    monkeypatch.setattr(os, 'name', 'nt')
    # Precisa mockar a classe base para evitar erro de path no windows
    monkeypatch.setattr(ExecutableApp, 'args', ['dummy_command'])
    ExecutableApp(shell=True, model='3')
    mock_subprocess_popen.assert_called_once()
    _, kwargs = mock_subprocess_popen.call_args
    assert kwargs['shell'] is True
    assert kwargs['creationflags'] == subprocess.CREATE_NO_WINDOW
    assert 'start_new_session' not in kwargs


@pytest.mark.usefixtures('mock_subprocess_popen')
def test_executable_app_get_args():
    """Testa a geração de argumentos para diferentes modelos."""

    # Mocka a classe base para definir 'args'
    class MockApp(ExecutableApp):
        args = ['base_arg']

    args_model2 = MockApp(model='2').args
    assert args_model2 == [
        'base_arg',
        '-xrm',
        '"*model: 2"',
        '-localcp',
        'utf8',
        '-utf8',
    ]

    args_model5 = MockApp(model='5').args
    assert args_model5 == [
        'base_arg',
        '-xrm',
        '"*model: 5"',
        '-localcp',
        'utf8',
        '-utf8',
    ]


@pytest.mark.usefixtures('mock_subprocess_popen')
def test_executable_app_close(mock_subprocess_popen):
    """Testa o fechamento do processo."""
    app = ExecutableApp(model='2')
    mock_process = mock_subprocess_popen.return_value
    mock_process.poll.return_value = None  # Processo ainda rodando
    mock_process.returncode = None

    return_code = app.close()

    mock_process.terminate.assert_called_once()
    # Testa se poll foi chamado para obter o returncode após terminate
    mock_process.poll.assert_called()
    assert return_code == 0  # Default quando poll retorna None após terminate


@pytest.mark.usefixtures('mock_subprocess_popen')
def test_executable_app_close_already_terminated(mock_subprocess_popen):
    """Testa o fechamento quando o processo já terminou."""
    app = ExecutableApp(model='2')
    mock_process = mock_subprocess_popen.return_value
    mock_process.poll.return_value = 1  # Processo já terminou com código 1
    mock_process.returncode = 1

    return_code = app.close()

    mock_process.terminate.assert_not_called()  # Não deve chamar terminate
    assert return_code == 1


@pytest.mark.usefixtures('mock_subprocess_popen')
def test_executable_app_write(mock_subprocess_popen):
    """Testa a escrita no stdin do processo."""
    app = ExecutableApp(model='2')
    mock_stdin = mock_subprocess_popen.return_value.stdin

    app.write(b'test data')

    mock_stdin.write.assert_called_once_with(b'test data')
    mock_stdin.flush.assert_called_once()


@pytest.mark.usefixtures('mock_subprocess_popen')
def test_executable_app_readline(mock_subprocess_popen):
    """Testa a leitura do stdout do processo."""
    app = ExecutableApp(model='2')
    mock_stdout = mock_subprocess_popen.return_value.stdout
    mock_stdout.readline.return_value = b'output line\n'

    line = app.readline()

    mock_stdout.readline.assert_called_once()
    assert line == b'output line\n'


# Testes para Command
@pytest.fixture
def mock_executable_app():
    """Fixture para criar um mock de ExecutableApp."""
    app = MagicMock(spec=ExecutableApp)
    return app


def test_command_init(mock_executable_app):
    """Testa a inicialização de Command com str e bytes."""
    cmd_bytes = Command(mock_executable_app, b'cmd1')
    assert cmd_bytes.cmdstr == b'cmd1'

    cmd_str = Command(mock_executable_app, 'cmd2')
    assert cmd_str.cmdstr == b'cmd2'


def test_command_execute_ok(mock_executable_app):
    """Testa a execução de um comando com resultado 'ok'."""
    mock_executable_app.readline.side_effect = [
        b'status line\n',  # Linha de status
        b'ok\n',  # Resultado
    ]
    cmd = Command(mock_executable_app, 'TestCmd')
    result = cmd.execute()

    mock_executable_app.write.assert_called_once_with(b'TestCmd\n')
    EXPECTED_READLINE_CALLS = 2
    assert mock_executable_app.readline.call_count == EXPECTED_READLINE_CALLS
    assert cmd.status_line == b'status line'
    assert result is True
    assert cmd.data == []


def test_command_execute_ok_with_data(mock_executable_app):
    """Testa a execução com dados antes do status."""
    mock_executable_app.readline.side_effect = [
        b'data: line 1\n',
        b'data: line 2\r\n',
        b'status line 2\n',
        b'ok\n',
    ]
    cmd = Command(mock_executable_app, 'GetData')
    result = cmd.execute()

    mock_executable_app.write.assert_called_once_with(b'GetData\n')
    EXPECTED_READS = 4
    assert mock_executable_app.readline.call_count == EXPECTED_READS
    assert cmd.status_line == b'status line 2'
    assert result is True
    assert cmd.data == [b'line 1', b'line 2']


def test_command_execute_error(mock_executable_app):
    """Testa a execução de um comando com resultado 'error'."""
    mock_executable_app.readline.side_effect = [
        b'status line error\n',
        b'error\n',
        b'data: Error message line 1\n',  # Mensagem de erro vem depois
        b'data: Error message line 2\n',
    ]
    cmd = Command(mock_executable_app, 'ErrorCmd')

    with pytest.raises(CommandError, match='[sem mensagem de erro]'):
        cmd.execute()

    mock_executable_app.write.assert_called_once_with(b'ErrorCmd\n')
    mock_executable_app.readline.reset_mock()
    mock_executable_app.readline.side_effect = [
        b'data: Error message line 1\n',
        b'data: Error message line 2\n',
        b'status line error\n',
        b'error\n',
    ]
    cmd = Command(mock_executable_app, 'ErrorCmdDataFirst')
    with pytest.raises(
        CommandError, match='Error message line 1Error message line 2'
    ):
        cmd.execute()
    assert cmd.data == [b'Error message line 1', b'Error message line 2']


def test_command_execute_quit(mock_executable_app):
    """Testa a execução do comando 'Quit'."""
    mock_executable_app.readline.side_effect = [
        b'status line quit\n',
        b'\n',  # Resultado vazio para Quit
    ]
    cmd = Command(mock_executable_app, 'Quit')
    result = cmd.execute()
    assert result is True


# Testes para Status
def test_status_init():
    """Testa a inicialização e parsing da Status line."""
    status_line = b'U F U C(hostname) I N 3279-4 080 043 020 010 0x1234 0.123'
    status = Status(status_line)

    assert status.status_line == status_line
    assert status.keyboard == b'U'
    assert status.screen_format == b'F'
    assert status.field_protection == b'U'
    assert status.connection_state == b'C(hostname)'
    assert status.emulator_mode == b'I'
    assert status.model_number == b'N'
    assert status.row_number == b'3279-4'
    assert status.col_number == b'080'
    assert status.cursor_row == b'043'
    assert status.cursor_col == b'020'
    assert status.window_id == b'010'
    assert status.exec_time == b'0x1234'

    status_line_sparse = b'U F U C(host) I N 3279-4 80 43 20 10 0x1 0.1'
    status_sparse = Status(status_line_sparse)
    assert status_sparse.keyboard == b'U'
    assert status_sparse.connection_state == b'C(host)'
    assert status_sparse.cursor_col == b'20'


def test_status_init_empty():
    """Testa a inicialização com status line vazia."""
    status = Status(b'')
    assert status.status_line == b'            '  # 12 espaços
    assert status.keyboard is None
    assert status.connection_state is None
    # ... outros campos também devem ser None


# Adicionar testes para Wc3270App, X3270Cmd, etc.
# Exemplo básico para Wc3270App (requer mock_socket)
@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_socket')
def test_wc3270app_init(mock_socket):
    """Testa a inicialização de Wc3270App."""
    # Mock _get_free_port para retornar uma porta fixa
    SCRIPT_PORT = 12345
    with patch(
        'pyx3270.emulator.Wc3270App._get_free_port', return_value=SCRIPT_PORT
    ):
        app = Wc3270App(model='3')
        assert app.shell is True
        assert app.script_port == SCRIPT_PORT
        assert '-xrm' in app.args
        assert '"*model: 3"' in app.args


@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_socket')
def test_wc3270app_connect(mock_subprocess_popen, mock_socket):
    """Testa o método connect de Wc3270App."""
    mock_sock_instance = mock_socket.return_value
    SCRIPT_PORT = 12345
    with patch(
        'pyx3270.emulator.Wc3270App._get_free_port', return_value=SCRIPT_PORT
    ):
        app = Wc3270App(model='4')

        result = app.connect('myhost.com')

        assert result is True
        args, kwargs = mock_subprocess_popen.call_args
        assert 'start' in args[0]
        assert '/wait' in args[0]
        assert 'wc3270' in args[0]  # Verifica o binário wc3270
        assert '-scriptport' in args[0]
        assert '12345' in args[0]
        assert 'myhost.com' in args[0]
        assert '*model: 4' in args[0]

        # Verifica se _make_socket foi chamado (indiretamente pela conexão)
        mock_socket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_sock_instance.connect.assert_called_once_with((
            'localhost',
            SCRIPT_PORT,
        ))
        mock_sock_instance.makefile.assert_called_once_with(mode='rwb')


@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_socket')
def test_wc3270app_connect_fails(
    mock_subprocess_popen, mock_socket, monkeypatch
):
    """Testa falha na conexão do socket em Wc3270App."""
    # Mock sleep
    monkeypatch.setattr('time.sleep', lambda x: None)
    mock_sock_instance = mock_socket.return_value
    # Simula falha persistente na conexão
    mock_sock_instance.connect.side_effect = socket.error(
        socket.errno.ECONNREFUSED, 'Connection refused'
    )
    SCRIPT_PORT = 12345
    with patch(
        'pyx3270.emulator.Wc3270App._get_free_port', return_value=SCRIPT_PORT
    ):
        app = Wc3270App(model='2')
        # Executa connect e verifica que NENHUMA exceção é levantada
        try:
            app.connect('otherhost.com')
        except Exception as e:
            pytest.fail(
                f'Wc3270App.connect levantou uma exceção inesperada: {e}'
            )

        # Verifica se tentou conectar múltiplas vezes (5 vezes no código)
        MAX_CONNECT_ATTEMPTS = 5
        assert mock_sock_instance.connect.call_count == MAX_CONNECT_ATTEMPTS


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_clear_screen_success(x3270_cmd_instance, monkeypatch):
    """Testa clear_screen com sucesso na primeira tentativa."""
    # Mock time.sleep para acelerar
    monkeypatch.setattr('time.sleep', lambda x: None)
    EXPECTED_COMMAND_CALLS = 3
    # Mock _exec_command para simular respostas
    # A função clear_screen chama _exec 3 vezes (Clear, Wait, Ascii)
    # O teste chama clear_screen 2 vezes (antes e depois de setar rows/cols)
    # Portanto, precisamos de pelo menos 6 resultados no side_effect
    mock_result_ok = MagicMock(status_line=b'ok', data=[])
    mock_result_empty_screen = MagicMock(status_line=b'ok', data=[b''])
    x3270_cmd_instance._exec_command.side_effect = [
        mock_result_ok,  # call 1: Clear() 1º chamada a clear_screen
        mock_result_ok,  # call 2: Wait() 1º chamada a clear_screen
        mock_result_empty_screen,  # call 3: Ascii() 1º chamada a clear_screen
        mock_result_ok,  # call 4: Clear() 2º chamada a clear_screen
        mock_result_ok,  # call 5: Wait() 2º chamada a clear_screen
        mock_result_empty_screen,  # call 6: Ascii() 2º chamada a clear_screen
        # Adiciona um extra para segurança, caso algo chame mais uma vez
        mock_result_ok,
    ]

    x3270_cmd_instance.rows = 24
    x3270_cmd_instance.cols = 80
    x3270_cmd_instance.clear_screen()

    # Verifica as chamadas da primeira execução bem-sucedida
    assert (
        x3270_cmd_instance._exec_command.call_count == EXPECTED_COMMAND_CALLS
    )
    calls_first_run = [
        call(b'clear()'),
        call(
            f'wait({x3270_cmd_instance.time_unlock}, unlock)'.encode('utf-8')
        ),
        call(b'ascii()'),
    ]
    x3270_cmd_instance._exec_command.assert_has_calls(
        calls_first_run, any_order=False
    )

    x3270_cmd_instance._exec_command.reset_mock()
    # Reatribui o side_effect pois reset_mock() o remove
    x3270_cmd_instance._exec_command.side_effect = [
        mock_result_ok,
        mock_result_ok,
        mock_result_empty_screen,
        mock_result_ok,
    ]
    x3270_cmd_instance.clear_screen()
    assert (
        x3270_cmd_instance._exec_command.call_count == EXPECTED_COMMAND_CALLS
    )
    x3270_cmd_instance._exec_command.assert_has_calls(
        calls_first_run, any_order=False
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_clear_screen_multiple_attempts(
    x3270_cmd_instance, monkeypatch
):
    """Testa clear_screen que precisa de múltiplas tentativas."""
    monkeypatch.setattr('time.sleep', lambda x: None)
    EXPECTED_CALLS = 9
    x3270_cmd_instance.rows = 24
    x3270_cmd_instance.cols = 80
    # Simula tela não vazia nas primeiras 2 tentativas
    x3270_cmd_instance._exec_command.side_effect = [
        MagicMock(status_line=b'ok', data=[]),  # Clear 1
        MagicMock(status_line=b'ok', data=[]),  # Wait 1
        MagicMock(
            status_line=b'ok', data=[b'some text']
        ),  # Ascii 1 (not empty)
        MagicMock(status_line=b'ok', data=[]),  # Clear 2
        MagicMock(status_line=b'ok', data=[]),  # Wait 2
        MagicMock(
            status_line=b'ok', data=[b'more text']
        ),  # Ascii 2 (not empty)
        MagicMock(status_line=b'ok', data=[]),  # Clear 3
        MagicMock(status_line=b'ok', data=[]),  # Wait 3
        MagicMock(status_line=b'ok', data=[b'']),  # Ascii 3 (empty)
    ]

    x3270_cmd_instance.clear_screen()

    assert x3270_cmd_instance._exec_command.call_count == EXPECTED_CALLS
    # Verifica a última chamada a Ascii
    assert x3270_cmd_instance._exec_command.call_args_list[-1] == call(
        b'ascii()'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_wait_for_field(x3270_cmd_instance):
    """Testa wait_for_field."""
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        status_line=b'ok', data=[]
    )

    x3270_cmd_instance.wait_for_field(timeout=10)

    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'wait(10, InputField)'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_wait_for_field_timeout(x3270_cmd_instance):
    """Testa wait_for_field com timeout (simulado por exceção)."""
    # Simula CommandError que seria levantado por Wait após timeout
    x3270_cmd_instance._exec_command.side_effect = CommandError(
        'Wait timed out'
    )

    # A função wait_for_field não trata exceções, apenas sequencia execução.
    x3270_cmd_instance.wait_for_field(timeout=1)

    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'wait(1, InputField)'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_string_found_true(x3270_cmd_instance):
    """Testa string_found quando a string é encontrada."""
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        data=[b'expected string']
    )

    result = x3270_cmd_instance.string_found(5, 10, 'expected string')

    assert result is True
    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'ascii(4, 9, 15)'
    )  # 15 = len('expected string')


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_string_found_false(x3270_cmd_instance):
    """Testa string_found quando a string não é encontrada."""
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        data=[b'actual string']
    )

    result = x3270_cmd_instance.string_found(1, 1, 'expected')

    assert result is False
    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'ascii(0, 0, 8)'
    )  # 8 = len('expected')


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_string_found_error(x3270_cmd_instance):
    """Testa string_found quando _exec_command falha."""
    x3270_cmd_instance._exec_command.side_effect = CommandError(
        'Failed to get string'
    )

    result = x3270_cmd_instance.string_found(2, 3, 'test')

    assert result is False  # A função retorna False em caso de erro
    x3270_cmd_instance._exec_command.assert_called_once_with(b'ascii(1, 2, 4)')


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_move_to(x3270_cmd_instance):
    """Testa move_to."""
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )

    x3270_cmd_instance.move_to(10, 20)

    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'movecursor1(10, 20)'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_send_pf(x3270_cmd_instance):
    # Mock _exec_command's return
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    EXPECTED_CALLS = 2
    with patch.object(x3270_cmd_instance, '_exec_command') as mock_exec:
        x3270_cmd_instance.send_pf('3')

        calls = mock_exec.call_args_list
        assert len(calls) >= EXPECTED_CALLS

        pf_command = calls[-2][0][0]
        expected_pf = b'PF(3)'
        assert pf_command == expected_pf

        wait_command = calls[-1][0][0]
        expected_wait = (
            f'wait({x3270_cmd_instance.time_unlock}, unlock)'.encode('utf-8')
        )
        assert wait_command == expected_wait


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_send_enter(x3270_cmd_instance):
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    EXPECTED_CALLS = 2

    with patch.object(x3270_cmd_instance, '_exec_command') as mock_exec:
        x3270_cmd_instance.send_enter()

        calls = mock_exec.call_args_list
        assert len(calls) >= EXPECTED_CALLS

        enter_command = calls[-2][0][0]
        expected_enter = b'enter()'
        assert enter_command == expected_enter

        wait_command = calls[-1][0][0]
        expected_wait = (
            f'wait({x3270_cmd_instance.time_unlock}, unlock)'.encode('utf-8')
        )
        assert wait_command == expected_wait


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_send_string(x3270_cmd_instance):
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    EXPECTED_CALLS = 2

    with patch.object(x3270_cmd_instance, '_exec_command') as mock_exec:
        x3270_cmd_instance.send_string('test string')

        calls = mock_exec.call_args_list

        assert len(calls) >= EXPECTED_CALLS

        string_command = calls[-2][0][0]
        expected_string = b'string(test string)'
        assert string_command == expected_string

        wait_command = calls[-1][0][0]
        expected_wait = (
            f'wait({x3270_cmd_instance.time_unlock}, unlock)'.encode('utf-8')
        )
        assert wait_command == expected_wait


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_send_string_truncate(x3270_cmd_instance):
    # Simula erro retornado pelo comando String
    x3270_cmd_instance._exec_command.side_effect = CommandError(
        'Write to protected field'
    )

    # Vamos testar o CommandError que é o que realmente pode acontecer.
    with pytest.raises(CommandError, match='Write to protected field'):
        x3270_cmd_instance.send_string('long string data')

    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'string(long string data)'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_get_string(x3270_cmd_instance):
    """Testa get_string."""
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        data=[b'data from screen']
    )

    result = x3270_cmd_instance.get_string(10, 5, 16)  # length = 16

    assert result == 'data from screen'
    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'ascii(9, 4, 16)'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_get_full_screen(x3270_cmd_instance):
    """Testa get_full_screen."""
    x3270_cmd_instance.rows = 24
    x3270_cmd_instance.cols = 80
    mock_data = [f'line {i}'.encode('utf-8') for i in range(24)]
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=mock_data)

    result = x3270_cmd_instance.get_full_screen()

    expected_result = ''.join([f'line {i}' for i in range(24)])
    assert result == expected_result
    x3270_cmd_instance._exec_command.assert_called_once_with(b'ascii()')


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_save_screen(x3270_cmd_instance):
    """Testa save_screen usando tempfile em vez de tmp_path."""
    x3270_cmd_instance.rows = 24
    x3270_cmd_instance.cols = 80
    screen_rows = [f'Screen Line {i}' for i in range(24)]
    mock_data = b''.join([row.encode('utf-8') for row in screen_rows])
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=mock_data)

    # Usa tempfile para criar um diretório temporário

    # Chama a função a ser testada
    x3270_cmd_instance.save_screen('path_test', 'myscreen')

    # Verifica se Ascii foi chamado corretamente
    x3270_cmd_instance._exec_command.assert_called_once_with(
        'printtext(html, file, path_test\\myscreen.html)'.encode('utf-8')
    )


@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_os_name')
def test_ws3270app_init(mock_subprocess_popen):
    """Testa a inicialização de Ws3270App."""
    app = Ws3270App(model='4')
    assert app.shell is False
    mock_subprocess_popen.assert_called_once()
    args, kwargs = mock_subprocess_popen.call_args
    assert 'ws3270' in args[0][0]
    assert '"*model: 4"' in args[0]


@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_os_name')
def test_x3270app_init(mock_subprocess_popen):
    """Testa a inicialização de X3270App."""
    app = X3270App(model='2')
    assert app.shell is False
    mock_subprocess_popen.assert_called_once()
    args, kwargs = mock_subprocess_popen.call_args
    assert 'x3270' in args[0][0]
    assert '"*model: 2"' in args[0]
    assert '-script' in args[0]


@pytest.mark.usefixtures('mock_subprocess_popen', 'mock_os_name')
def test_s3270app_init(mock_subprocess_popen):
    """Testa a inicialização de S3270App."""
    app = S3270App(model='5')
    assert app.shell is False
    mock_subprocess_popen.assert_called_once()
    args, kwargs = mock_subprocess_popen.call_args
    assert 's3270' in args[0][0]
    assert '"*model: 5"' in args[0]


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_wait_string_found_success_first_try(x3270_cmd_instance):
    """Testa wait_string_found encontrando a string de primeira."""

    def always_wrong(*args, **kwargs):
        return 'target string'

    x3270_cmd_instance.get_string = MagicMock(side_effect=always_wrong)

    result = x3270_cmd_instance.wait_string_found(
        1, 1, 'target string', timeout=3
    )

    assert result is True
    x3270_cmd_instance.get_string.assert_called_once_with(
        1, 1, len('target string')
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_wait_string_found_timeout(x3270_cmd_instance, monkeypatch):
    """Testa wait_string_found com timeout."""

    # Simula o tempo avançando lentamente (0.5s por chamada)
    fake_time = (100 + i * 0.5 for i in count())
    monkeypatch.setattr('time.time', lambda: next(fake_time))
    monkeypatch.setattr('time.sleep', lambda x: None)

    x3270_cmd_instance.get_string = MagicMock(return_value='wrong string')

    result = x3270_cmd_instance.wait_string_found(2, 2, 'expected', timeout=2)

    assert result is False
    assert x3270_cmd_instance.get_string.call_count >= 1


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_wait_string_found_not_equal(x3270_cmd_instance, monkeypatch):
    """Testa wait_string_found com equal=False."""

    fake_time = (200 + i * 0.5 for i in count())
    monkeypatch.setattr('time.time', lambda: next(fake_time))
    monkeypatch.setattr('time.sleep', lambda x: None)

    x3270_cmd_instance._exec_command.return_value = MagicMock(
        data=[b'different string']
    )

    result = x3270_cmd_instance.wait_string_found(
        3, 3, 'target', equal=False, timeout=2
    )

    assert (
        result is True
    )  # Deve retornar True porque a string encontrada é diferente
    x3270_cmd_instance._exec_command.assert_called_once_with(b'ascii(2, 2, 6)')


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_delete_field(x3270_cmd_instance):
    """Testa delete_field."""
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    x3270_cmd_instance.delete_field()
    x3270_cmd_instance._exec_command.assert_called_once_with(b'deletefield()')


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_send_home(x3270_cmd_instance):
    x3270_cmd_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    EXPECTED_CALLS = 2

    with patch.object(x3270_cmd_instance, '_exec_command') as mock_exec:
        x3270_cmd_instance.send_home()

        call_list = mock_exec.call_args_list

        assert len(call_list) >= EXPECTED_CALLS

        home_command_args = call_list[-2][0][0]
        wait_command_args = call_list[-1][0][0]

        expected_home_command = b'home()'
        expected_wait_command = (
            f'wait({x3270_cmd_instance.time_unlock}, unlock)'.encode('utf-8')
        )

        assert home_command_args == expected_home_command
        assert wait_command_args == expected_wait_command


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_get_string_area(x3270_cmd_instance):
    """Testa get_string_area."""
    x3270_cmd_instance.rows = 24
    x3270_cmd_instance.cols = 80
    # Simula a resposta do comando Ascii para uma área
    mock_data = [
        b'row1 data',
        b'row2 data',
        b'row3 data',
    ]
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=mock_data)

    result = x3270_cmd_instance.get_string_area(1, 5, 3, 15)  # y1, x1, y2, x2

    expected_result = 'row1 datarow2 datarow3 data'
    assert result == expected_result
    # Verifica o comando Ascii com coordenadas de área
    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'ascii(0, 4, 3, 11)'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_search_string_found(x3270_cmd_instance):
    """Testa search_string quando a string é encontrada."""
    # Simula a resposta do comando Ascii para a tela inteira
    screen_data = [
        b'line 1',
        b'line 2 with target',
        b'line 3',
    ]
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=screen_data)
    x3270_cmd_instance.rows = 3
    x3270_cmd_instance.cols = 20

    result = x3270_cmd_instance.search_string('target')

    assert result is True
    x3270_cmd_instance._exec_command.assert_called_once_with(
        b'ascii(0, 0, 80)'
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_search_string_not_found(x3270_cmd_instance):
    """Testa search_string quando a string não é encontrada."""
    screen_data = [b'line one', b'line two']
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=screen_data)
    x3270_cmd_instance.rows = 2
    x3270_cmd_instance.cols = 10

    result = x3270_cmd_instance.search_string('missing')

    assert result is False


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_search_string_ignore_case(x3270_cmd_instance):
    """Testa search_string com ignore_case=True."""
    screen_data = [b'Some Text HERE']
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=screen_data)
    x3270_cmd_instance.rows = 1
    x3270_cmd_instance.cols = 15

    assert (
        x3270_cmd_instance.search_string('text here', ignore_case=True) is True
    )
    assert (
        x3270_cmd_instance.search_string('TEXT HERE', ignore_case=True) is True
    )
    assert (
        x3270_cmd_instance.search_string('text here', ignore_case=False)
        is False
    )


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_get_string_positions(x3270_cmd_instance):
    """Testa get_string_positions."""
    screen_data = [
        #   01234567890123456789 (cols)
        b'abc target 123'.ljust(80),  # row 0
        b'456 target abc'.ljust(80),  # row 1
        b'target end.'.ljust(80),  # row 2
    ]
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=screen_data)
    x3270_cmd_instance.rows = 3
    x3270_cmd_instance.cols = 20

    positions = x3270_cmd_instance.get_string_positions('target')

    assert positions == [(1, 5), (2, 5), (3, 1)]  # (row, col)
    x3270_cmd_instance._exec_command.assert_called_once_with(b'ascii()')


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_get_string_positions_ignore_case(x3270_cmd_instance):
    """Testa get_string_positions com ignore_case=True."""
    screen_data = [
        b'Find Me'.ljust(80),
        b'find me too'.ljust(80),
    ]  # row 0, row 1
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=screen_data)
    x3270_cmd_instance.rows = 2
    x3270_cmd_instance.cols = 15

    positions = x3270_cmd_instance.get_string_positions(
        'find me', ignore_case=True
    )
    assert positions == [(1, 1), (2, 1)]

    positions_case_sensitive = x3270_cmd_instance.get_string_positions(
        'find me', ignore_case=False
    )
    assert positions_case_sensitive == [(2, 1)]


@pytest.mark.usefixtures('x3270_cmd_instance')
def test_x3270cmd_get_string_positions_not_found(x3270_cmd_instance):
    """Testa get_string_positions quando a string não é encontrada."""
    screen_data = [b'nothing here']
    x3270_cmd_instance._exec_command.return_value = MagicMock(data=screen_data)
    x3270_cmd_instance.rows = 1
    x3270_cmd_instance.cols = 15

    positions = x3270_cmd_instance.get_string_positions('missing')
    assert positions == []


# Testes para a classe X3270 (Emulator)
@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_terminate(x3270_emulator_instance):
    """Testa o método terminate do emulador."""
    mock_app = x3270_emulator_instance.app
    mock_app.close = MagicMock()

    x3270_emulator_instance.terminate()
    # Verifica se o comando Quit foi executado
    x3270_emulator_instance._exec_command.assert_called_once_with(b'quit()')
    # Verifica se o app foi fechado
    mock_app.close.assert_called_once()


@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_is_connected_true(x3270_emulator_instance):
    """Testa is_connected quando conectado."""

    # Impede que query sobrescreva ou acione __getattr__
    x3270_emulator_instance.query = MagicMock()

    # Define o atributo status ANTES de qualquer chamada
    x3270_emulator_instance.status = SimpleNamespace(
        connection_state=b'C(hostname) ...'
    )

    x3270_emulator_instance._exec_command.return_value = MagicMock(
        status_line=b'C(hostname) ...'
    )

    assert x3270_emulator_instance.is_connected() is True


@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_is_connected_false(x3270_emulator_instance):
    """Testa is_connected quando não conectado."""
    # Simula status de não conectado
    # Impede que query sobrescreva ou acione __getattr__
    x3270_emulator_instance.query = MagicMock()

    # Define o atributo status ANTES de qualquer chamada
    x3270_emulator_instance.status = SimpleNamespace(
        connection_state=b'L F U N ...'
    )

    x3270_emulator_instance._exec_command.return_value = MagicMock(
        status_line=b'L F U N ...'
    )

    assert x3270_emulator_instance.is_connected() is False


@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_connect_host(x3270_emulator_instance):
    """Testa connect_host."""
    x3270_emulator_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    x3270_emulator_instance.connect_host('myhost', '1234', tls=False)
    x3270_emulator_instance._exec_command.assert_called_with(
        b'wait(5, 3270mode)'
    )


@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_connect_host_tls(x3270_emulator_instance):
    """Testa connect_host com TLS."""
    x3270_emulator_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    x3270_emulator_instance.connect_host('securehost', '992', tls=True)
    # Verifica se o prefixo L: foi adicionado para TLS
    x3270_emulator_instance._exec_command.assert_called_with(
        b'wait(5, 3270mode)'
    )


@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_reconnect_host_success(x3270_emulator_instance):
    """Testa reconnect_host com sucesso."""
    x3270_emulator_instance._exec_command.return_value = MagicMock(
        status_line=b'ok'
    )
    x3270_emulator_instance.reconnect_host()
    x3270_emulator_instance._exec_command.assert_called_with(b'reconnect()')


@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_reconnect_host_failure(x3270_emulator_instance):
    """Testa reconnect_host com falha."""
    x3270_emulator_instance._exec_command.side_effect = CommandError(
        'Reconnect failed'
    )
    with pytest.raises(CommandError, match='Reconnect failed'):
        x3270_emulator_instance._exec_command()
    x3270_emulator_instance.reconnect_host()
    x3270_emulator_instance._exec_command.assert_called_with(b'quit()')


# Teste para _exec_command (embora simples, para cobertura)
@pytest.mark.usefixtures('x3270_emulator_instance')
def test_x3270_exec_command_flow(x3270_emulator_instance):
    """Testa o fluxo básico de _exec_command."""
    # Remove o mock anterior para testar a implementação real (que usa Command)
    del x3270_emulator_instance._exec_command
    EXPECTED_CALLS = 2
    with patch.object(x3270_emulator_instance, 'app', MagicMock()) as mock_app:
        mock_app.readline.side_effect = [
            b'status line for exec\n',
            b'ok\n',
        ]

        cmd_result = x3270_emulator_instance._exec_command(b'testcommand()')

        # Verifica se o app foi usado para escrever e ler
        mock_app.write.assert_called_with(b'testcommand()\n')
        assert mock_app.readline.call_count == EXPECTED_CALLS
    # Verifica o resultado retornado (instância de Command)
    assert isinstance(cmd_result, Command)
    assert cmd_result.status_line == b'status line for exec'
    assert cmd_result.data == []
