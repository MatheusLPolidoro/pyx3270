from abc import ABC, abstractmethod


class AbstractExecutableApp(ABC):
    """Representa uma aplicação responsavel por emular um terminal tn3270."""

    @abstractmethod
    def _spawn_app(self) -> None: ...

    @abstractmethod
    def _get_executable_app_args(self, model: str) -> None: ...

    @classmethod
    @abstractmethod
    def connect(*args) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def write(self, data: str) -> None: ...

    @abstractmethod
    def readline(self) -> bytes: ...


class AbstractCommand(ABC):
    """Representa um comando de script no TerminalClient."""

    @abstractmethod
    def execute(self) -> bool: ...

    @abstractmethod
    def handle_result(self, result: str) -> bool: ...


class AbstractEmulatorCmd(ABC):
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
    def move_to(self, ypos: int, xpos: int): ...

    @abstractmethod
    def send_string(self, tosend: str, ypos: int, xpos: int): ...

    @abstractmethod
    def senf_enter(self): ...

    @abstractmethod
    def send_home(self): ...

    @abstractmethod
    def send_pf(self): ...

    @abstractmethod
    def get_string(self): ...

    @abstractmethod
    def get_string_area(
        self, yposi: int, xposi: int, ypose: int, xpose: int
    ): ...

    @abstractmethod
    def get_full_screen(self, header: bool): ...

    @abstractmethod
    def save_screen(self, file_path: str, file_name: str): ...

    @abstractmethod
    def search_string(self, string, ignore_case=False): ...

    @abstractmethod
    def get_string_positions(self, string, ignore_case=False): ...

    @abstractmethod
    def _get_ypos_and_xpos_from_index(self, index): ...


class AbstractEmulator(ABC):
    """
    Representa um subprocesso do emulador x/s3270,
    fornece uma API para interagir com ele.
    """

    @abstractmethod
    def _create_app(self): ...

    @abstractmethod
    def _exec_command(self, cmdstr: str): ...

    @abstractmethod
    def terminate(self): ...

    @abstractmethod
    def is_connected(self): ...

    @abstractmethod
    def connect_host(self, host: str, port: str, tsl: bool): ...

    @abstractmethod
    def reconnect_host(self): ...
