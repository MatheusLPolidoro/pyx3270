import pytest

from pyx3270.exceptions import (
    BrokenPipeError,
    CommandError,
    FieldTruncateError,
    KeyboardStateError,
    NotConnectedException,
    ReconnectException,
    TerminatedError,
    TimeoutWaitError,
)


def test_broken_pipe_error():
    with pytest.raises(BrokenPipeError, match='Test BrokenPipeError'):
        raise BrokenPipeError('Test BrokenPipeError')


def test_command_error():
    with pytest.raises(CommandError, match='Test CommandError'):
        raise CommandError('Test CommandError')


def test_terminated_error():
    with pytest.raises(TerminatedError, match='Test TerminatedError'):
        raise TerminatedError('Test TerminatedError')


def test_keyboard_state_error():
    with pytest.raises(KeyboardStateError, match='Test KeyboardStateError'):
        raise KeyboardStateError('Test KeyboardStateError')


def test_field_truncate_error():
    with pytest.raises(FieldTruncateError, match='Test FieldTruncateError'):
        raise FieldTruncateError('Test FieldTruncateError')


def test_not_connected_exception():
    with pytest.raises(
        NotConnectedException, match='Test NotConnectedException'
    ):
        raise NotConnectedException('Test NotConnectedException')


def test_reconnect_exception():
    with pytest.raises(ReconnectException, match='Test ReconnectException'):
        raise ReconnectException('Test ReconnectException')


def test_timeout_wait_error():
    with pytest.raises(TimeoutWaitError, match='Test TimeoutWaitError'):
        raise TimeoutWaitError('Test TimeoutWaitError')
