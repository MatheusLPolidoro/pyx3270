import os
import socket
import sys
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


def start_sock(port: int, allow_fallback: bool = False) -> socket.socket:
    tnsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tnsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if os.name == 'posix':
        tnsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    try:
        tnsock.bind(('', port))
    except PermissionError as e:
        if not allow_fallback:
            tnsock.close()
            error_msg = (
                f'Sem permissão para abrir a porta {port}. No Linux, portas '
                "abaixo de 1024 exigem privilégio (ex.: 'sudo setcap "
                "cap_net_bind_service=+ep $(readlink -f $(which python3))', "
                'ou execute como root). Use uma porta >= 1024 se não for '
                'possível conceder esse privilégio.'
            )
            raise PermissionError(error_msg) from e
        rich.print(
            f'[!] Sem permissão para a porta {port}; escolhendo '
            'automaticamente uma porta local livre...'
        )
        tnsock.bind(('', 0))
    tnsock.listen(5)
    return tnsock


def start_server_thread(
    port: int,
    handler: Callable,
    handler_args: tuple | list | None = None,
    label: str = 'Servidor',
    allow_port_fallback: bool = False,
) -> tuple[threading.Thread, int, socket.socket]:
    # bind+listen acontecem aqui, de forma síncrona, para garantir que a
    # porta já esteja escutando antes desta função retornar -- do
    # contrário, um cliente (ex.: emu.connect_host logo em seguida) pode
    # tentar conectar antes da thread de aceitação ter feito o bind.
    tnsock = start_sock(port, allow_fallback=allow_port_fallback)
    actual_port = tnsock.getsockname()[1]
    rich.print(f'[+] {label} escutando na porta {actual_port}')

    def server_loop():
        try:
            while True:
                clientsock, addr = tnsock.accept()
                rich.print(f'[+] Cliente conectado: {addr}')

                th = threading.Thread(
                    target=handler,
                    args=(clientsock, *handler_args),
                    daemon=True,
                )
                th.start()
        except OSError:
            # Socket de escuta fechado de propósito (ex.: o loop de
            # record()/replay() reiniciando e encerrando o listener
            # anterior antes de abrir um novo) -- não é um erro real.
            pass

    th = threading.Thread(target=server_loop, daemon=True)
    th.start()
    # O socket de escuta é devolvido para que o chamador possa fechá-lo
    # explicitamente antes de abrir um novo na próxima iteração do loop
    # -- sem isso, cada reconexão deixa um listener (e uma thread de
    # aceitação) órfão, todos escutando a mesma porta indefinidamente.
    return th, actual_port, tnsock


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
    port: int = typer.Option(default=3270),
    tls: bool = typer.Option(default=False),
    model: str = typer.Option(default='2'),
    emulator: bool = typer.Option(default=True),
):
    screens = load_screens(directory)
    rich.print(f'[+] REPLAY do caminho: {directory}')

    listen_sock = None
    try:
        while True:
            if listen_sock is not None:
                listen_sock.close()
            server_thread, actual_port, listen_sock = start_server_thread(
                port,
                replay_handler,
                handler_args=(screens, emulator, directory),
                label='Servidor de replay',
            )

            if emulator:
                emu = X3270(visible=True, model=model, save_log_file=True)
                emu.connect_host(
                    'localhost', actual_port, tls, mode_3270=False
                )
                sleep(2)

            start_command_process()
            control_replay(server_thread)
    except KeyboardInterrupt:
        rich.print('\n[x] Interrompido pelo usuário.')
        state.command_process.terminate()
        if emulator:
            emu.terminate()
        sys.exit(0)


@app.command()
def record(  # noqa: PLR0913, PLR0917
    address: str = typer.Option(),
    directory: str = typer.Option(default='./screens'),
    tls: bool = typer.Option(default=True),
    model: str = typer.Option(default='2'),
    emulator: bool = typer.Option(default=True),
    local_port: int = typer.Option(
        default=None,
        help=(
            'Porta local em que o proxy de gravação escuta. Por padrão, '
            'usa a mesma porta do host de origem (--address) -- o que '
            'exige privilégio no Linux para portas abaixo de 1024 (ex.: '
            '992). Use esta opção para escutar em uma porta local '
            'diferente, sem privilégio.'
        ),
    ),
):
    host, *port = address.split(':', 2)
    port = int(*port) if port else 3270
    listen_port = local_port if local_port is not None else port

    rich.print(f'[+] RECORD na porta {listen_port}')
    reconnect = False
    listen_sock = None
    try:
        while True:
            if emulator and not reconnect:
                emu = X3270(visible=True, model=model, save_log_file=True)
            elif not reconnect:
                emu = None

            if listen_sock is not None:
                listen_sock.close()
            server_thread, actual_port, listen_sock = start_server_thread(
                port=listen_port,
                handler=record_handler,
                handler_args=(emu, address, directory, 0.01),
                label='Servidor de gravação',
                allow_port_fallback=local_port is None,
            )
            # Mantém a porta resolvida (pode ter mudado por causa do
            # fallback) estável entre reconexões do loop.
            listen_port = actual_port

            if emulator:
                rich.print('[+] Conectando ao emulador...')
                if reconnect:
                    emu.reconnect_host()
                else:
                    # mode_3270=True: espera a negociação 3270 real (via
                    # proxy até o host de origem) completar antes de
                    # devolver o controle -- sem isso, o comando podia
                    # retornar como "conectado" com a tela ainda em
                    # branco, exigindo desconectar/reconectar manualmente
                    # no emulador.
                    emu.connect_host(
                        'localhost', listen_port, tls, mode_3270=True
                    )

            rich.print(
                f'[+] Escutando localhost na porta {listen_port}, '
                f'origem {host=} {port=}'
            )
            control_replay(server_thread)
            reconnect = True
    except KeyboardInterrupt:
        rich.print('\n[x] Interrompido pelo usuário.')
        if emulator:
            emu.terminate()
        sys.exit(0)


if __name__ == '__main__':
    app()
