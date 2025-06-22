from logging.handlers import TimedRotatingFileHandler
import os
import pathlib
import re
import select
import socket
import sys
import logging
import queue
import threading

command_queue = queue.Queue()

sys.path.append(str(pathlib.Path(__file__).parent))

import pyx3270.tn3270 as tn3270
from pyx3270.emulator import X3270, BINARY_FOLDER

os.makedirs('./logs', exist_ok=True)
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)

# Evita duplicação de handlers
if not logger.handlers:
    handler = TimedRotatingFileHandler(
        filename='./logs/server.log',
        when='midnight',  # Roda diariamente
        interval=1,  # Intervalo de 1 dia
        backupCount=7,  # Mantém arquivos dos últimos 7 dias
        encoding='utf-8',  # Mantém acentos
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

# Se quiser evitar que os logs sejam propagados para o logger raiz
logger.propagate = False


def ensure_dir(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)


def is_screen_tn3270(data):
    min_file_len = 100
    return len(data) > min_file_len and b'\x11' in data


def load_screens_basic(record_dir):
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


def load_screens(record_dir):
    """Carrega arquivos .bin mantendo a ordem dentro de cada subdiretório."""
    ensure_dir(record_dir)  # Garante que o diretório existe
    screens = {}
    try:
        if not any(f.endswith('.bin') for f in os.listdir(record_dir)):
            screens = load_screens_basic(BINARY_FOLDER)

        for root, _, files in os.walk(
            record_dir
        ):  # Percorre todas as subpastas
            sorted_files = sorted(
                files
            )  # Ordena os arquivos de cada pasta separadamente
            for f in sorted_files:
                if f.endswith('.bin'):
                    file_path = os.path.join(root, f)
                    with open(file_path, 'rb') as fd:
                        data = fd.read()
                        # Garante que termina com tn3270.IAC TN_EOR
                        if not data.endswith(tn3270.IAC + tn3270.TN_EOR):
                            data += tn3270.IAC + tn3270.TN_EOR
                        screens[str(f).upper().replace('.BIN', '')] = data
    except Exception as ex:
        logger.error(f'Falha ao carregar caminho: {record_dir}')
    return screens


def find_directory(base_dir, search_name):
    """Busca um diretório dentro da pasta base, considerando maiúsculas/minúsculas e busca parcial."""
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


def convert_s(hex_string: str):
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


def record_handler(
    emu: X3270,
    clientsock: socket.socket,
    address: str,
    record_dir=None,
    delay=0.01,
):
    serversock = connect_serversock(clientsock, address)

    if not serversock:
        return

    ensure_dir(record_dir)

    counter = 0

    def record_data(data_block):
        nonlocal counter

        if not is_screen_tn3270(data_block):
            return
        fn = os.path.join(record_dir, f'{counter:03}.bin')
        with open(fn, 'wb') as f:
            f.write(data_block)
        counter += 1

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
                        record_data(full_block)
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

    except (ConnectionResetError, OSError):
        for sock in socks:
            sock.close()


def backend_3270(
    clientsock: socket.socket,
    screens: list[bytes],
    current_screen: int,
    emulator: bool,
) -> int | None:
    aid = None

    while aid not in tn3270.AIDS:
        try:
            aid = clientsock.recv(1)
            if not aid:
                raise Exception('Terminal fechado.')
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


def listen_for_commands():
    while True:
        command = input('Digite um comando: ')
        command_queue.put(command)


def replay_handler(
    clientsock: socket.socket,
    screens: dict,
    emulator: bool,
    base_directory: str,
):
    screens_list = list(screens.values())
    current_screen = 0
    clear = False
    command_thread = threading.Thread(target=listen_for_commands, daemon=True)
    command_thread.start()

    try:
        peer_name = clientsock.getpeername()
        logger.info(f'Iniciando replay para {peer_name}')
        clientsock.sendall(b'\xff\xfd\x18\xff\xfb\x18')

        while True:
            if not clear:
                try:
                    buf = screens_list[current_screen]
                    clientsock.sendall(buf)
                except IndexError:
                    current_screen = len(screens_list) - 1
                    buf = screens_list[current_screen]
                    clientsock.sendall(buf)

            # Verifica se há comandos na fila
            try:
                command = command_queue.get_nowait()
                command_log = (
                    command
                    if not command.startswith('add ')
                    else ' '.join(command.split()[:2])
                )
                logger.info(f'Comando recebido: {command_log}')
                if command.startswith('set '):
                    screen_name = command.split(' ', 1)[1].upper()
                    screen_index = next(
                        (
                            i
                            for i, screen in enumerate(screens.keys())
                            if screen_name in screen.upper()
                        ),
                        None,
                    )
                    if screen_index is not None:
                        current_screen = screen_index
                        print(f'[+] Mudando para a tela: {screen_name}')
                        continue
                elif command.startswith('add '):
                    screen_name, screen_data = command.split(' ', 2)[1:]
                    screen_name = screen_name.upper()

                    # Converte a string recebida para bytes sem alterar os valores hexadecimais
                    screen_data_bytes = bytes.fromhex(screen_data)

                    final_bytes = (
                        tn3270.START_SCREEN
                        + screen_data_bytes
                        + tn3270.IAC
                        + tn3270.TN_EOR
                    )

                    # Adicionar tela
                    screens[screen_name] = final_bytes
                    screens_list.append(final_bytes)
                elif command.startswith('change directory '):
                    new_dir = find_directory(
                        base_directory, command.split(' ', 2)[2].strip()
                    )
                    if os.path.isdir(new_dir):
                        screens = load_screens_basic(
                            new_dir
                        )  # Recarrega as telas
                        screens_list = list(
                            screens.values()
                        )  # Atualiza a lista de telas
                        current_screen = 0
                        logger.info(
                            f'[+] Mudando para o diretório de telas: {new_dir}'
                        )
                    else:
                        logger.info(f'[!] Diretório inválido: {new_dir}')
                elif command.startswith('next'):
                    current_screen = min(len(screens), current_screen + 1)
                    logger.info(
                        f"[!] Comando 'next' enviado: {current_screen}"
                    )
                    continue
                elif command.startswith('prev'):
                    current_screen = max(0, current_screen - 1)
                    logger.info(
                        f"[!] Comando 'prev' enviado: {current_screen}"
                    )
                    continue
                elif command.startswith('clear'):
                    clear = True
                    clientsock.sendall(tn3270.CLEAR_SCREEN_BUFFER)
                    logger.info(
                        f"[!] Comando 'clear' enviado: {current_screen}"
                    )
                    continue
                elif command.startswith('q'):
                    logger.info("[!] Comando 'quit' enviado.")
                    break
            except queue.Empty:
                pass

            result = backend_3270(
                clientsock, screens_list, current_screen, emulator
            )
            current_screen = result.get('current_screen')
            clear = result.get('clear')

    except Exception as e:
        logger.error(f'[!] Erro fora do esperado: {str(e)}')
    finally:
        clientsock.close()
