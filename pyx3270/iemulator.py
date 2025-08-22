from abc import ABC, abstractmethod

from pyx3270.x3270_commands import X3270Commands


class AbstractExecutableApp(ABC):
    """Representa uma aplicação responsavel por emular um terminal tn3270."""

    @classmethod
    @abstractmethod
    def connect(*args) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def write(self, data: str) -> None: ...

    @abstractmethod
    def readline(self) -> bytes: ...

    @abstractmethod
    def _spawn_app(self) -> None: ...

    @abstractmethod
    def _get_executable_app_args(self, model: str) -> None: ...


class AbstractCommand(ABC):
    """Representa um comando de script no TerminalClient."""

    @abstractmethod
    def execute(self) -> bool: ...

    @abstractmethod
    def handle_result(self, result: str) -> bool: ...


class AbstractEmulatorCmd(ABC, X3270Commands):
    @abstractmethod
    def clear_screen(self) -> None: ...

    @abstractmethod
    def wait_for_field(self, timeout: float) -> None: ...

    @abstractmethod
    def wait_string_found(
        self, ypos: int, xpos: int, string: str, equal: bool, timeout: float
    ) -> bool: ...

    @abstractmethod
    def string_found(self, ypos: int, xpos: int, string: str) -> bool: ...

    @abstractmethod
    def delete_field(self) -> None: ...

    @abstractmethod
    def move_to(self, ypos: int, xpos: int) -> None: ...

    @abstractmethod
    def send_pf(self, value: str) -> None: ...

    @abstractmethod
    def send_string(self, tosend: str, ypos: int, xpos: int) -> None: ...

    @abstractmethod
    def send_enter(self, times: int = 1) -> None: ...

    @abstractmethod
    def send_home(self) -> None: ...

    @abstractmethod
    def get_string(self) -> str: ...

    @abstractmethod
    def get_string_area(
        self, yposi: int, xposi: int, ypose: int, xpose: int
    ) -> str: ...

    @abstractmethod
    def get_full_screen(self, header: bool) -> str: ...

    @abstractmethod
    def save_screen(self, file_path: str, file_name: str) -> None: ...

    @abstractmethod
    def search_string(
        self, string: str, ignore_case: bool = False
    ) -> bool: ...

    @abstractmethod
    def get_string_positions(
        self, string: str, ignore_case: bool = False
    ) -> list[tuple[int, int]]: ...

    @abstractmethod
    def _get_ypos_and_xpos_from_index(self, index: int) -> tuple[int, int]: ...


class AbstractEmulator(AbstractEmulatorCmd):
    """
    Representa um subprocesso do emulador x/s3270,
    fornece uma API para interagir com ele.
    """

    @abstractmethod
    def terminate(self) -> None: ...

    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def connect_host(self, host: str, port: str, tls: bool) -> None: ...

    @abstractmethod
    def reconnect_host(self) -> None: ...

    @abstractmethod
    def _create_app(self) -> None: ...

    @abstractmethod
    def _exec_command(self, cmdstr: str) -> str: ...
