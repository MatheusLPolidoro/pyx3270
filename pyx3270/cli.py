import os
import socket
import threading
from time import sleep
from typing import Callable

import rich
import typer

from pyx3270 import state
from pyx3270.emulator import X3270
from pyx3270.server import (
    load_screens,
    record_handler,
    replay_handler,
    server_stop,
    start_command_process,
)

app = typer.Typer()


def start_sock(port: int) -> socket.socket:
    tnsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tnsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if os.name == 'posix':
        tnsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    tnsock.bind(('', port))
    tnsock.listen(5)
    return tnsock


def start_server_thread(
    port: int,
    handler: Callable,
    handler_args: tuple | list | None = None,
    label: str = 'Servidor',
) -> threading.Thread:
    def server_loop():
        tnsock = start_sock(port)
        rich.print(f'[+] {label} escutando na porta {port}')
        while True:
            clientsock, addr = tnsock.accept()
            rich.print(f'[+] Cliente conectado: {addr}')

            th = threading.Thread(
                target=handler, args=(clientsock, *handler_args), daemon=True
            )
            th.start()

    th = threading.Thread(target=server_loop, daemon=True)
    th.start()
    return th


def control_replay(th: threading.Thread) -> None:
    # Aguarda encerramento da thread ou falha do servidor
    while th.is_alive():
        if server_stop.is_set():
            rich.print('[x] Conexão encerrada.')
            if state.command_process:
                state.command_process.terminate()
            server_stop.clear()
            break
        sleep(1)

    while True:
        rich.print('[?] Digite "Q" para sair ou "S" para continuar: ', end='')
        op = input().strip().upper()
        if op == 'Q':
            rich.print('[*] Encerrando aplicação...')
            os._exit(0)
        elif op != 'S':
            rich.print('[!] Opção inválida. Continuando...')
        else:
            rich.print('[*] Reiniciando...')
            break
        sleep(1)

    rich.print('[+] Escutando localhost')


@app.command()
def replay(
    directory: str = typer.Option(default='./screens'),
    port: int = typer.Option(default=992),
    tls: bool = typer.Option(default=False),
    model: str = typer.Option(default='2'),
    emulator: bool = typer.Option(default=True),
):
    screens = load_screens(directory)
    rich.print(f'[+] REPLAY do caminho: {directory}')

    try:
        while True:
            server_thread = start_server_thread(
                port,
                replay_handler,
                handler_args=(screens, emulator, directory),
                label='Servidor de replay',
            )

            if emulator:
                emu = X3270(visible=True, model=model, save_log_file=True)
                emu.connect_host('localhost', port, tls, mode_3270=False)
                sleep(2)

            start_command_process()
            control_replay(server_thread)
    except KeyboardInterrupt:
        rich.print('\n[x] Interrompido pelo usuário.')
        state.command_process.terminate()
        os._exit(0)


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

    try:
        while True:
            if emulator:
                emu = X3270(visible=True, model=model, save_log_file=True)
            else:
                emu = None

            server_thread = start_server_thread(
                port=port,
                handler=record_handler,
                handler_args=(emu, address, directory, 0.01),
                label='Servidor de gravação',
            )

            if emulator:
                rich.print('[+] Conectando ao emulador...')
                emu.connect_host('localhost', port, tls, mode_3270=False)

            rich.print(f'[+] Escutando localhost, origem {host=} {port=}')
            control_replay(server_thread)
    except KeyboardInterrupt:
        rich.print('\n[x] Interrompido pelo usuário.')
        os._exit(0)


if __name__ == '__main__':
    app()
