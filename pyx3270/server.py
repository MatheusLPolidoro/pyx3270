import os
import pathlib
import re
import select
import socket
import sys
from logging import DEBUG, getLogger

sys.path.append(str(pathlib.Path(__file__).parent))

import tn3270
from emulator import X3270

logger = getLogger()
logger.setLevel(DEBUG)


def ensure_dir(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)


def is_screen_tn3270(data):
    min_file_len = 100
    return len(data) > min_file_len and b'\x11' in data


def load_screens(record_dir):
    ensure_dir(record_dir)
    files = sorted(f for f in os.listdir(record_dir) if f.endswith('.bin'))
    screens = []
    for f in files:
        with open(os.path.join(record_dir, f), 'rb') as fd:
            data = fd.read()
            # Garante que termina com tn3270.IAC TN_EOR
            if not data.endswith(tn3270.IAC + tn3270.TN_EOR):
                data += tn3270.IAC + tn3270.TN_EOR
            screens.append(data)
    return screens


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
    emulator: bool
) -> int | None:
    aid = None
    while aid not in tn3270.AIDS:
        try:
            aid = clientsock.recv(1)
            if not aid:
                raise Exception('Terminal fechado.')
        except socket.timeout:
            continue

    press = clientsock.recv(3)
    key_press = (
        press
        in {
            b'@@' + tn3270.IAC,
            b'@@' + tn3270.WSF,
            tn3270.IAC + tn3270.TN_EOR,
            b'K\xe9\xff',
        }
        or b'\xff' in press
        or b'@@' in press
        or tn3270.SBA in press
    )
    clear = False
    if aid == tn3270.PF3 and key_press and emulator:
        current_screen = max(0, current_screen - 1)
    elif aid in {tn3270.PF4, tn3270.ENTER} and key_press:
        current_screen = min(len(screens) - 1, current_screen + 1)
    elif aid == tn3270.CLEAR and key_press:
        clientsock.sendall(tn3270.CLEAR_SCREEN_BUFFER)
        clear = True

    return dict(current_screen=current_screen, clear=clear)


def replay_handler(clientsock: socket.socket, screens: list, emulator: bool):
    current_screen = 0
    clear = False
    try:
        clientsock.sendall(b'\xff\xfd\x18\xff\xfb\x18')

        while True:
            if not clear:
                buf = screens[current_screen]
                clientsock.sendall(buf)

            result: dict = backend_3270(clientsock, screens, current_screen, emulator)
            current_screen = result.get('current_screen')
            clear = result.get('clear')

    except Exception as e:
        logger.error(f'[!] Erro fora do esperado: {str(e)}')
    finally:
        clientsock.close()
