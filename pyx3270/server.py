from datetime import datetime
import os
import select
import socket

import tn3270


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
            # Garante que termina com IAC EOR
            if not data.endswith(tn3270.IAC + tn3270.TN_EOR):
                data += tn3270.IAC + tn3270.TN_EOR
            screens.append(data)
    return screens


def record_handler(clientsock, target, port, record_dir=None, delay=0.01):
    try:
        serversock = socket.create_connection((target, port), timeout=5)
    except Exception as e:
        print(f'[!] Proxy -> MF Falha de conexão: {e}')
        clientsock.close()
        return

    ensure_dir(record_dir)
    counter = 0
    channel = {clientsock: serversock, serversock: clientsock}
    socks = [clientsock, serversock]
    buffers = {clientsock: b'', serversock: b''}

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
                data = s.recv(2048)
                if not data:
                    raise ConnectionResetError

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
    
    if aid == tn3270.PF3:
        current_screen = max(0, current_screen - 1)
    elif aid in {tn3270.PF4, tn3270.ENTER}:
        current_screen = min(len(screens) - 1, current_screen + 1)
    elif aid == tn3270.CLEAR:
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
