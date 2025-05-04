import socket
import sys
import threading

import typer
from emulator import BINARY_FOLDER, X3270
from pynput import keyboard
from server import load_screens, record_handler, replay_handler

app = typer.Typer()


def start_sock(port: int) -> socket.socket:
    tnsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tnsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tnsock.bind(('', port))
    tnsock.listen(5)
    return tnsock


def start_new_amulator(th: threading.Thread, emu: X3270) -> None:
    th.join()
    print('[?] Digite "ESC" para sair ou "ENTER" para continuar: ')
    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                sys.exit(0)
            elif event.key == keyboard.Key.enter:
                break
    print('[+] Escutando localhost...')
    emu.reconnect_host()


@app.command()
def replay(
    directory: str = typer.Option(default='./screens'),
    port: int = typer.Option(default=3270),
    tsl: bool = typer.Option(default=False),
    model: str = typer.Option(default='2'),
    emulator: bool = typer.Option(default=False),
):
    screens = load_screens(BINARY_FOLDER) + load_screens(directory)

    print(f'[+] REPLAY do caminho: {directory}')
    tnsock = start_sock(port)

    print(f'[+] Escutando localhost, porta {port}')
    if emulator:
        emu = X3270(visible=True, model=model)
        emu.connect_host('localhost', port, tsl)

    while True:
        clientsock, addr = tnsock.accept()
        print(f'[+] Replay de conexões de {addr}')

        th = threading.Thread(
            target=replay_handler, args=(clientsock, screens)
        )
        th.start()

        if emulator:
            start_new_amulator(th, emu)


@app.command()
def record(
    address: str = typer.Option(),
    directory: str = typer.Option(default='./screens'),
    tsl: bool = typer.Option(default=False),
    model: str = typer.Option(default='2'),
    emulator: bool = typer.Option(default=False),
):
    host, *port = address.split(':', 2)
    port = int(*port) if port else 3270

    print(f'[+] RECORD na porta {port}')
    tnsock = start_sock(port)

    print(f'[+] Escutando localhost, porta {port}')
    if emulator:
        emu = X3270(visible=True, model=model)
        emu.connect_host('localhost', port, tsl)

    while True:
        clientsock, addr = tnsock.accept()
        print('[+] Conexão recebida de:', addr)

        th = threading.Thread(
            target=record_handler, args=(clientsock, host, port, directory)
        )
        th.start()

        if emulator:
            start_new_amulator(th, emu)


if __name__ == '__main__':
    app()
