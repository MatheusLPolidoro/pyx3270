import pathlib
import socket
import sys
import threading

import rich
import typer
from pynput import keyboard

sys.path.append(str(pathlib.Path(__file__).parent))

from emulator import BINARY_FOLDER, X3270
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
    rich.print('[?] Digite "ESC" para sair ou "ENTER" para continuar: ')
    with keyboard.Events() as events:
        for event in events:
            if event.key == keyboard.Key.esc:
                sys.exit(0)
            elif event.key == keyboard.Key.enter:
                break
    rich.print('[+] Escutando localhost...')
    emu.reconnect_host()


@app.command()
def replay(
    directory: str = typer.Option(default='./screens'),
    port: int = typer.Option(default=992),
    tls: bool = typer.Option(default=False),
    model: str = typer.Option(default='2'),
    emulator: bool = typer.Option(default=True),
):
    screens = load_screens(BINARY_FOLDER) + load_screens(directory)

    rich.print(f'[+] REPLAY do caminho: {directory}')
    tnsock = start_sock(port)

    rich.print(f'[+] Escutando localhost, porta {port}')
    if emulator:
        emu = X3270(visible=True, model=model)
        emu.connect_host('localhost', port, tls)

    while True:
        clientsock, addr = tnsock.accept()
        rich.print(f'[+] Replay de conexões de {addr}')

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
    tls: bool = typer.Option(default=True),
    model: str = typer.Option(default='2'),
    emulator: bool = typer.Option(default=True),
):
    host, *port = address.split(':', 2)
    port = int(*port) if port else 3270

    rich.print(f'[+] RECORD na porta {port}')
    tnsock = start_sock(port)

    rich.print(f'[+] Escutando localhost, porta {port}')
    if emulator:
        emu = X3270(visible=True, model=model)
        emu.connect_host('localhost', port, tls)

    while True:
        clientsock, addr = tnsock.accept()
        rich.print('[+] Conexão recebida de:', addr)

        th = threading.Thread(
            target=record_handler, args=(emu, clientsock, address, directory)
        )
        th.start()

        if emulator:
            start_new_amulator(th, emu)


if __name__ == '__main__':
    app()
