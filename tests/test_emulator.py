import pytest

from pyx3270.emulator import (
    X3270,
    X3270Cmd,
    Wc3270App,
    Ws3270App,
    X3270App,
    S3270App,
    ExecutableApp,
    AbstractEmulator,
    AbstractEmulatorCmd,
    AbstractExecutableApp,
)


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
