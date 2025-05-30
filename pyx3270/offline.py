# Navegação e controle do sistema execução OFFLINE
import subprocess
import sys
from .emulator import logger

class PyX3270Manager:
    def __init__(self, directory='./screens'):
        self.command = [
            sys.executable,
            '-m',
            'pyx3270',
            'replay',
            '--directory',
            directory,
            '--no-tls',
            '--no-emulator',
        ]

        # Usa subprocess.Popen para iniciar o servidor
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )


    def _exec(self, command: str) -> None:
        if self.process.poll() is not None:
            logger.info(
                '[!] O processo inativo, não é possível enviar comandos.'
            )
            return

        logger.info(f"[+] Enviando comando offline: {command}")
        self.process.stdin.write(f'{command}\n')
        self.process.stdin.flush()
        self.emu.PF(1)

    def next(self):
        """Define a tela específica e aguarda processamento corretamente."""
        self._exec('next')

    def prev(self):
        """Define a tela específica e aguarda processamento corretamente."""
        self._exec('prev')

    def send_pf(self, val: int):
        if val in (4, 8):
            self.next()
        elif val in (3, 7):
            self.prev()

    def set_screen(self, screen: str):
        """Define a tela específica e aguarda processamento corretamente."""
        self._exec(f'set {screen}')
        return True

    def change_directory(self, directory: str):
        """Troca o diretório de carregamento das telas."""
        self._exec(f'change directory {directory}')
        self.emu.PF(1)

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
