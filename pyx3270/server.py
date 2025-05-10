import os
import pathlib
import re
import select
import socket
import sys

sys.path.append(str(pathlib.Path(__file__).parent))

import tn3270
from emulator import X3270


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
            # Garante que termina com tn3270.IAC EOR
            if not data.endswith(tn3270.IAC + tn3270.EOR):
                data += tn3270.IAC + tn3270.EOR
            screens.append(data)
    return screens


def convert_sf(hex_string: str):
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


def record_handler(
    emu: X3270,
    clientsock: socket.socket,
    address: str,
    record_dir=None,
    delay=0.01,
):
    host, *port = address.split(':', 2)
    port = int(*port) if port else 3270
    try:
        serversock = socket.create_connection((host, port), timeout=5)
    except Exception as e:
        print(f'[!] Proxy -> MF Falha de conexão: {e}')
        clientsock.close()
        return

    ensure_dir(record_dir)
    counter = 0
    channel = {clientsock: serversock, serversock: clientsock}
    socks = [clientsock, serversock]
    screens = list()

    def record_data(data_block):
        nonlocal counter

        if not is_screen_tn3270(data_block):
            return
        fn = os.path.join(record_dir, f'{counter:03}.bin')
        with open(fn, 'wb') as f:
            f.write(data_block)
        counter += 1

    try:
        while True:
            ready_socks, _, _ = select.select(socks, [], [], delay)
            for s in ready_socks:
                save = True
                data = s.recv(2048)
                if not data:
                    raise ConnectionResetError

                channel[s].sendall(data)

            buffer = emu.readbuffer('ebcdic')
            if (
                not buffer.replace(' ', '').replace('0', '')
                or not save
                or buffer in screens
            ):
                continue
            buffer_hex = convert_sf(buffer)
            hex_bytes = bytes.fromhex(buffer_hex)
            full_block = (
                tn3270.START_SCREEN + hex_bytes + tn3270.IAC + tn3270.EOR
            )
            record_data(full_block)
            save = False
            screens.append(buffer)

    except (ConnectionResetError, OSError):
        for sock in socks:
            sock.close()


def backend_3270(
    clientsock: socket.socket, screens: list[bytes], current_screen: int
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
            tn3270.IAC + tn3270.EOR,
            b'K\xe9\xff',
        }
        or b'\xff' in press
    )

    if aid == tn3270.PF3 and key_press:
        current_screen = max(0, current_screen - 1)
    elif aid in {tn3270.PF4, tn3270.ENTER} and key_press:
        current_screen = min(len(screens) - 1, current_screen + 1)
    elif aid == tn3270.CLEAR and key_press:
        clientsock.sendall(tn3270.CLEAR_SCREEN_BUFFER)
        current_screen = None

    return current_screen


def replay_handler(clientsock: socket.socket, screens):
    current_screen = 0
    try:
        clientsock.sendall(b'\xff\xfd\x18\xff\xfb\x18')

        while True:
            if current_screen is not None:
                buf = screens[current_screen]
                clientsock.sendall(buf)
            else:
                current_screen = 0

            current_screen = backend_3270(clientsock, screens, current_screen)

    except Exception as e:
        print(f'[ERRO] {str(e)}')
    finally:
        clientsock.close()
