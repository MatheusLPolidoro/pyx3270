import multiprocessing
import os
import queue
import re
import select
import socket
import sys
import threading
from dataclasses import dataclass
from logging import getLogger

import rich

from pyx3270 import state, tn3270
from pyx3270.emulator import BINARY_FOLDER, X3270
from pyx3270.exceptions import NotConnectedException

logger = getLogger(__name__)
server_stop = threading.Event()
command_queue = multiprocessing.Queue()


@dataclass
class ReplayState:
    screens: dict
    screens_list: list
    current_screen: int
    clear: bool


def ensure_dir(path: str | None) -> None:
    if path and not os.path.isdir(path):
        logger.info(f'[+] Criando diretório: {path}')
        os.makedirs(path)


def is_screen_tn3270(data: bytes) -> bool:
    min_file_len = 100
    return len(data) > min_file_len and b'\x11' in data


def load_screens_basic(record_dir: str) -> dict:
    """Carrega todos os arquivos .bin do diretório e subdiretórios."""
    ensure_dir(record_dir)  # Garante que o diretório existe
    screens = {}

    for root, _, files in os.walk(record_dir):  # Percorre pastas e subpastas
        for f in sorted(files):
            if f.endswith('.bin'):
                file_path = os.path.join(root, f)
                with open(file_path, 'rb') as fd:
                    data = fd.read()
                    # Garante que termina com tn3270.IAC TN_EOR
                    if not data.endswith(tn3270.IAC + tn3270.TN_EOR):
                        data += tn3270.IAC + tn3270.TN_EOR
                    screens[str(f).upper().replace('.BIN', '')] = data

    return screens


def load_screens(record_dir: str) -> dict:
    """Carrega arquivos .bin mantendo a ordem dentro de cada subdiretório."""
    ensure_dir(record_dir)  # Garante que o diretório existe

    screens = {}

    try:
        has_bin = any(f.endswith('.bin') for f in os.listdir(record_dir))
        if not has_bin:
            return load_screens_basic(BINARY_FOLDER)

        for root, _, files in os.walk(record_dir):
            for f in sorted(files):
                if not f.endswith('.bin'):
                    continue

                file_path = os.path.join(root, f)
                with open(file_path, 'rb') as fd:
                    data = fd.read()

                # Garante que termina com tn3270.IAC + TN_EOR
                if not data.endswith(tn3270.IAC + tn3270.TN_EOR):
                    data += tn3270.IAC + tn3270.TN_EOR

                key = f.upper().replace('.BIN', '')
                screens[key] = data

    except Exception:
        logger.error(f'Falha ao carregar caminho: {record_dir}')

    return screens


def find_directory(base_dir: str, search_name: str) -> str | None:
    """
    Busca um diretório dentro da pasta base, considerando
    maiúsculas/minúsculas e busca parcial.
    """
    search_name = (
        search_name.lower()
    )  # Normaliza para comparação case-insensitive

    for dir_name in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, dir_name)):
            if (
                search_name in dir_name.lower()
            ):  # Compara de forma insensível a maiúsculas/minúsculas
                return os.path.join(base_dir, dir_name)

    return None  # Retorna None se não encontrar um diretório correspondente


def convert_s(hex_string: str) -> str:
    pattern = r'SF\((.*?)\)'

    def replace_match(match):
        parameters = match.group(1).split(',')
        converted_values = [
            f'1D{param.split("=")[1]}' for param in parameters if '=' in param
        ]
        return ''.join(converted_values)

    converted_string = re.sub(pattern, replace_match, hex_string)
    converted_string = converted_string.replace(' ', '')
    return converted_string


def connect_serversock(
    clientsock: socket.socket, address: str
) -> socket.socket:
    host, *port = address.split(':', 2)
    port = int(*port) if port else 3270
    try:
        serversock = socket.create_connection((host, port), timeout=5)
    except Exception as e:
        logger.error(f'[!] Proxy -> MF Falha de conexão: {e}')
        clientsock.close()
        return
    return serversock


def record_data(data_block, record_dir: str, counter: int) -> int:
    if not is_screen_tn3270(data_block):
        logger.warning('[!] Dados recebidos não são uma tela TN3270.')
        return 0
    fn = os.path.join(record_dir, f'{counter:03}.bin')
    with open(fn, 'wb') as f:
        logger.info(f'[+] Gravação de tela: {fn}')
        f.write(data_block)
    return 1


def record_handler(
    clientsock: socket.socket,
    emu: X3270,
    address: str,
    record_dir=None,
    delay=0.01,
) -> None:
    logger.info(f'Iniciando gravação para {clientsock.getpeername()}')
    serversock = connect_serversock(clientsock, address)

    if not serversock:
        logger.error('[!] Falha ao conectar ao servidor.')
        return

    ensure_dir(record_dir)

    counter = 0

    socks = [clientsock, serversock]
    channel = {clientsock: serversock, serversock: clientsock}
    buffers = {clientsock: b'', serversock: b''}
    screens = []

    try:
        while True:
            ready_socks, _, _ = select.select(socks, [], [], delay)
            for s in ready_socks:
                save = True
                data = s.recv(2048)
                if not data:
                    raise ConnectionResetError

                if emu.tls:
                    channel[s].sendall(data)
                    continue

                buffers[s] += data

                if s == serversock and record_dir:
                    while tn3270.IAC + tn3270.TN_EOR in buffers[s]:
                        block, _, rest = buffers[s].partition(
                            tn3270.IAC + tn3270.TN_EOR
                        )
                        full_block = block + tn3270.IAC + tn3270.TN_EOR
                        counter += record_data(full_block, record_dir, counter)
                        buffers[s] = rest
                channel[s].sendall(data)

            if emu.tls:
                buffer = emu.readbuffer('ebcdic')
                if (
                    not buffer.replace(' ', '').replace('0', '')
                    or not save
                    or buffer in screens
                ):
                    continue
                buffer_hex = convert_s(buffer)
                buffer_hex = bytes.fromhex(buffer_hex)
                full_block = (
                    tn3270.START_SCREEN
                    + buffer_hex
                    + tn3270.IAC
                    + tn3270.TN_EOR
                )
                save = False
                screens.append(buffer)
                record_data(full_block)

    except (ConnectionResetError, OSError, NotConnectedException):
        logger.info('[!] Conexão encerrada pelo servidor ou erro de rede.')
        for sock in socks:
            sock.close()
        server_stop.set()


def backend_3270(
    clientsock: socket.socket,
    screens: list[bytes],
    current_screen: int,
    emulator: bool,
) -> dict[str, int | bool]:
    aid = None

    while aid not in tn3270.AIDS:
        try:
            aid = clientsock.recv(1)
            if not aid:
                raise ConnectionResetError('Terminal fechado.')
        except socket.timeout:
            continue

    press = clientsock.recv(1)

    # Verifica se press contém um código esperado
    key_press = press and press not in tn3270.AIDS
    clear = False

    if aid in {tn3270.PF3, tn3270.PF7} and key_press and emulator:
        current_screen = max(0, current_screen - 1)
        logger.info('[!] Comando de retorno recebido.')
    elif (
        aid in {tn3270.PF4, tn3270.PF8, tn3270.ENTER}
        and key_press
        and emulator
    ):
        logger.info('[!] Comando de paginação/confirmação recebido.')
        current_screen = min(len(screens) - 1, current_screen + 1)
    elif aid == tn3270.CLEAR and key_press and emulator:
        logger.info('[!] Comando CLEAR recebido.')
        clientsock.sendall(tn3270.CLEAR_SCREEN_BUFFER)
        clear = True

    return dict(current_screen=current_screen, clear=clear)


def listen_for_commands(command_queue):
    logger.info('[*] Aguardando comandos...')
    sys.stdin = open(0, mode='r', encoding='utf-8')
    try:
        while True:
            command = input('[?] Digite um comando: ').strip().lower()
            if command == 'q':
                rich.print("[*] Comando 'quit' recebido, encerrando...")
                break
            command_queue.put(command)
    except OSError as e:
        logger.warning(f'[*] stdin para comandos fechado: {e}')
    finally:
        logger.warning('[*] Encerrando processo de escuta.')


def handle_set(command: str, screens: dict) -> int | None:
    screen_name = command.split(' ', 1)[1].upper()
    for i, key in enumerate(screens.keys()):
        if screen_name in key:
            rich.print(f'\n[+] Mudando para a tela: {screen_name}\n')
            return i
    return None


def handle_add(command: str, screens: dict, screens_list: list) -> None:
    try:
        screen_name, screen_data = command.split(' ', 2)[1:]
        screen_name = screen_name.upper()
        screen_bytes = bytes.fromhex(screen_data)
        final_bytes = (
            tn3270.START_SCREEN + screen_bytes + tn3270.IAC + tn3270.TN_EOR
        )
        screens[screen_name] = final_bytes
        screens_list.append(final_bytes)
    except ValueError:
        logger.warning('[!] Formato inválido ao adicionar tela')


def handle_change_directory(
    command: str, base_directory: str
) -> tuple[dict, list]:
    new_dir = find_directory(base_directory, command.split(' ', 2)[2].strip())
    if new_dir and os.path.isdir(new_dir):
        new_screens = load_screens_basic(new_dir)
        logger.info(f'[+] Mudando para o diretório de telas: {new_dir}')
        return new_screens, list(new_screens.values())
    else:
        logger.info(f'[!] Diretório inválido: {new_dir}')
        return dict(), list()


def process_command(
    command: str,
    clientsock: socket.socket,
    base_directory: str,
    state: ReplayState,
) -> ReplayState:
    command_log = (
        command
        if not command.startswith('add ')
        else ' '.join(command.split()[:2])
    )
    logger.info(f'Comando recebido: {command_log}')

    if command.startswith('set '):
        index = handle_set(command, state.screens)
        if index is not None:
            state.current_screen = index

    elif command.startswith('add '):
        handle_add(command, state.screens, state.screens_list)

    elif command.startswith('change directory '):
        state.screens, state.screens_list = handle_change_directory(
            command, base_directory
        )
        state.current_screen = 0

    elif command == 'next':
        state.current_screen = min(
            len(state.screens), state.current_screen + 1
        )
        logger.info(f"[!] Comando 'next' enviado: {state.current_screen}")

    elif command == 'prev':
        state.current_screen = max(0, state.current_screen - 1)
        logger.info(f"[!] Comando 'prev' enviado: {state.current_screen}")

    elif command == 'clear':
        state.clear = True
        clientsock.sendall(tn3270.CLEAR_SCREEN_BUFFER)
        logger.info(f"[!] Comando 'clear' enviado: {state.current_screen}")

    elif command == 'q':
        logger.info("[!] Comando 'quit' enviado.")
        clientsock.close()

    return state


def start_command_process():
    if state.command_process and state.command_process.is_alive():
        logger.warning('[!] Processo de comando já está em execução.')
        return

    if not multiprocessing.get_start_method(allow_none=True):
        if os.name == 'posix':
            multiprocessing.set_start_method('fork')
        else:
            multiprocessing.set_start_method('spawn')

    logger.info('[+] Iniciando processo de comando...')
    state.command_process = multiprocessing.Process(
        target=listen_for_commands, args=(command_queue,)
    )
    state.command_process.start()


def replay_handler(
    clientsock: socket.socket,
    screens: dict,
    emulator: bool,
    base_directory: str,
) -> None:
    state = ReplayState(
        screens=screens,
        screens_list=list(screens.values()),
        current_screen=0,
        clear=False,
    )

    try:
        peer_name = clientsock.getpeername()
        logger.info(f'Iniciando replay para {peer_name}')
        clientsock.sendall(b'\xff\xfd\x18\xff\xfb\x18')

        while True:
            try:
                if not state.clear:
                    clientsock.sendall(
                        state.screens_list[state.current_screen]
                    )
            except IndexError:
                state.current_screen = len(state.screens_list) - 1
                clientsock.sendall(state.screens_list[state.current_screen])

            try:
                command = command_queue.get_nowait()
                state = process_command(
                    command, clientsock, base_directory, state
                )
            except queue.Empty:
                pass

            result = backend_3270(
                clientsock, state.screens_list, state.current_screen, emulator
            )

            state.current_screen = result.get(
                'current_screen', state.current_screen
            )
            state.clear = result.get('clear', state.clear)

    except Exception as e:
        logger.error(f'[!] Erro fora do esperado: {str(e)}')
        server_stop.set()
    finally:
        clientsock.close()
        server_stop.set()
