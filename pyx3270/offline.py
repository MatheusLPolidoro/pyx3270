import subprocess
from logging import getLogger
from time import sleep

from pyx3270.iemulator import AbstractEmulator

logger = getLogger(__name__)


class PyX3270Manager:
    def __init__(self, emu: AbstractEmulator, directory='./screens'):
        self.command = [
            'pyx3270',
            'replay',
            '--directory',
            directory,
            '--no-tls',
            '--no-emulator',
        ]
        self.emu = emu
        # Usa subprocess.Popen para iniciar o servidor
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=0,
        )

    def _exec(self, command: str) -> None:
        if self.process.poll() is not None:
            logger.info(
                '[!] O processo inativo, não é possível enviar comandos: %s',
                command,
            )
            return

        logger.info('[+] Enviando comando offline: %s', command)
        try:
            self.process.stdin.write(f'{command}\n')
            self.process.stdin.flush()
            sleep(0.05)
        except Exception as e:
            logger.error('Erro ao enviar comando: %s', e)
            return
        self.emu.pf(1)
        sleep(0.1)
        self.emu.pf(1)
        sleep(0.1)

    def next(self, *args, **kwargs):
        """Define a tela específica e aguarda processamento corretamente."""
        self._exec('next')
        self.emu.wait_unlock()

    def prev(self, *args, **kwargs):
        """Define a tela específica e aguarda processamento corretamente."""
        self._exec('prev')
        self.emu.wait_unlock()

    def clear(self):
        """Define a tela específica e aguarda processamento corretamente."""
        self.emu.pf(12)

    def send_pf(self, val: int):
        if val in {4, 8}:
            self.next()
        elif val in {3, 7}:
            self.prev()

    def set_screen(self, screen: str):
        """Define a tela específica e aguarda processamento corretamente."""
        self._exec(f'set {screen}')
        return True

    def change_directory(self, directory: str):
        """Troca o diretório de carregamento das telas."""
        self._exec(f'change directory {directory}')
        sleep(3)
        self.emu.pf(1)

    def terminate(self):
        """Finaliza corretamente o processo e evita que fique travado."""
        if (
            self.process.poll() is None
        ):  # Verifica se o processo ainda está rodando
            self.emu.terminate()
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def __del__(self):
        """Certifica que o processo será encerrado ao destruir a instância."""
        self.terminate()
