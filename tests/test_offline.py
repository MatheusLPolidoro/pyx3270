import gc
import subprocess
import sys
import weakref
from unittest.mock import MagicMock, patch

from pyx3270.offline import PyX3270Manager


@patch('subprocess.Popen')
def test_pyx3270_manager_init_and_terminate(mock_popen, x3270_cmd_instance):
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    mock_process.poll.return_value = None  # Processo em execução

    manager = PyX3270Manager(x3270_cmd_instance)

    mock_popen.assert_called_once_with(
        [
            sys.executable,
            '-m',
            'pyx3270',
            'replay',
            '--directory',
            './screens',
            '--no-tls',
            '--no-emulator',
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    assert manager.process == mock_process

    manager.terminate()
    mock_process.poll.assert_called_once()
    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_called_once_with(timeout=5)


@patch('subprocess.Popen')
@patch('pyx3270.offline.logger')
def test_pyx3270_manager_exec(mock_logger, mock_popen, x3270_cmd_instance):
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    mock_process.poll.return_value = None  # Processo em execução

    manager = PyX3270Manager(x3270_cmd_instance)
    manager.emu = MagicMock()  # Mock atributos de emu

    command = 'test_command'
    manager._exec(command)

    mock_logger.info.assert_called_with(
        f'[+] Enviando comando offline: {command}'
    )
    mock_process.stdin.write.assert_called_once_with(f'{command}\n')
    mock_process.stdin.flush.assert_called_once()
    manager.emu.pf.assert_called_once_with(1)


@patch('subprocess.Popen')
@patch('pyx3270.offline.logger')
def test_pyx3270_manager_exec_inactive_process(
    mock_logger, mock_popen, x3270_cmd_instance
):
    mock_process = MagicMock()
    mock_popen.return_value = mock_process
    mock_process.poll.return_value = 1  # Process is inactive

    manager = PyX3270Manager(x3270_cmd_instance)
    manager.emu = MagicMock()

    command = 'test_command'
    manager._exec(command)

    mock_logger.info.assert_called_with(
        '[!] O processo inativo, não é possível enviar comandos.'
    )
    mock_process.stdin.write.assert_not_called()


def test_pyx3270_manager_next(x3270_cmd_instance):
    manager = PyX3270Manager(x3270_cmd_instance)
    manager._exec = MagicMock()
    manager.next()
    manager._exec.assert_called_once_with('next')


def test_pyx3270_manager_prev(x3270_cmd_instance):
    manager = PyX3270Manager(x3270_cmd_instance)
    manager._exec = MagicMock()
    manager.prev()
    manager._exec.assert_called_once_with('prev')


def test_pyx3270_manager_clear(x3270_cmd_instance):
    manager = PyX3270Manager(x3270_cmd_instance)
    manager._exec = MagicMock()
    manager.clear()
    manager._exec.assert_called_once_with('clear')


def test_pyx3270_manager_send_pf(x3270_cmd_instance):
    manager = PyX3270Manager(x3270_cmd_instance)
    manager.next = MagicMock()
    manager.prev = MagicMock()

    manager.send_pf(4)
    manager.next.assert_called_once()
    manager.next.reset_mock()

    manager.send_pf(8)
    manager.next.assert_called_once()
    manager.next.reset_mock()

    manager.send_pf(3)
    manager.prev.assert_called_once()
    manager.prev.reset_mock()

    manager.send_pf(7)
    manager.prev.assert_called_once()
    manager.prev.reset_mock()

    manager.send_pf(1)
    manager.next.assert_not_called()
    manager.prev.assert_not_called()


def test_pyx3270_manager_set_screen(x3270_cmd_instance):
    manager = PyX3270Manager(x3270_cmd_instance)
    manager._exec = MagicMock()
    screen_name = 'test_screen'
    result = manager.set_screen(screen_name)
    manager._exec.assert_called_once_with(f'set {screen_name}')
    assert result is True


def test_pyx3270_manager_change_directory(x3270_cmd_instance):
    manager = PyX3270Manager(x3270_cmd_instance)
    manager._exec = MagicMock()
    manager.emu = MagicMock()
    directory_name = 'new_directory'
    manager.change_directory(directory_name)
    manager._exec.assert_called_once_with(f'change directory {directory_name}')
    manager.emu.pf.assert_called_once_with(1)


def test_pyX3270_manager_del(x3270_cmd_instance):
    manager = PyX3270Manager(x3270_cmd_instance)
    terminate_mock = MagicMock()
    manager.terminate = terminate_mock

    called_flag = {'called': False}

    def on_finalize():
        called_flag['called'] = terminate_mock.called

    weakref.finalize(manager, on_finalize)

    del manager
    gc.collect()

    assert called_flag['called']


@patch('subprocess.Popen')
def test_terminate_kills_process_on_timeout(mock_popen, x3270_cmd_instance):
    # Mock do processo
    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    # Simula que o processo está rodando
    mock_process.poll.return_value = None

    # Simula o wait lançando TimeoutExpired
    mock_process.wait.side_effect = subprocess.TimeoutExpired(
        cmd='testcmd', timeout=5
    )

    # Instancia o manager
    manager = PyX3270Manager(x3270_cmd_instance)

    # Mock do emu.terminate
    manager.emu = MagicMock()

    # Chama o método terminate
    manager.terminate()

    # Verificações
    mock_process.poll.assert_called_once()
    manager.emu.terminate.assert_called_once()
    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_called_once_with(timeout=5)
    mock_process.kill.assert_called_once()
