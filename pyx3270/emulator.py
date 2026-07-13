import errno
import logging.config
import math
import os
import re
import socket
import subprocess
import sys
from contextlib import closing
from functools import cache
from importlib.resources import files
from logging import getLogger
from time import sleep, time
from typing import Literal

from pyx3270.exceptions import (
    CommandError,
    FieldTruncateError,
    KeyboardStateError,
    NotConnectedException,
    TerminatedError,
)
from pyx3270.iemulator import (
    AbstractCommand,
    AbstractEmulator,
    AbstractEmulatorCmd,
    AbstractExecutableApp,
)
from pyx3270.logging_config import LOGGING_CONFIG
from pyx3270.x3270_commands import x3270_command

logger = getLogger(__name__)


def get_binary_path(*parts):
    # Se estiver rodando como executável PyInstaller
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'pyx3270', 'bin', *parts)

    # Se estiver rodando como pacote instalado normalmente
    try:
        bin_dir = files('pyx3270').joinpath('bin')
        return str(bin_dir.joinpath(*parts))
    except Exception as e:
        raise FileNotFoundError(f'Não foi possível localizar o binário: {e}')


BINARY_FOLDER = get_binary_path()
MODEL_TYPE = Literal['2', '3', '4', '5']
MODEL_DIMENSIONS = {
    '2': {
        'rows': 24,
        'columns': 80,
    },
    '3': {
        'rows': 32,
        'columns': 80,
    },
    '4': {
        'rows': 43,
        'columns': 80,
    },
    '5': {
        'rows': 27,
        'columns': 132,
    },
}


class ExecutableApp(AbstractExecutableApp):
    args = list()

    def __init__(self, shell: bool = False, model: MODEL_TYPE = '2') -> None:
        logger.debug(
            'Inicializando ExecutableApp (shell=%s, model=%s)', shell, model
        )
        self.shell = shell
        self.subprocess = None
        self.args = self._get_executable_app_args(model)
        self._spawn_app()

    def _spawn_app(self, args=None) -> None:
        logger.debug('Iniciando processo do aplicativo')
        kwargs = {
            'shell': self.shell,
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }

        if args:
            self.args = args

        if os.name == 'nt':
            logger.debug(
                'Detectado sistema Windows, configurando flags específicos'
            )
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        else:
            logger.debug(
                'Detectado sistema não-Windows, configurando nova sessão'
            )
            kwargs['start_new_session'] = True

        try:
            logger.debug('Executando comando: %s', self.args)
            self.subprocess = subprocess.Popen(self.args, **kwargs)
            logger.debug('Processo iniciado com PID: %s', self.subprocess.pid)
        except Exception as e:
            logger.error('Erro ao iniciar processo: %s', e)
            raise

    def _get_executable_app_args(self, model: MODEL_TYPE) -> list:
        logger.debug('Obtendo argumentos para modelo: %s', model)
        args = self.__class__.args + [
            '-xrm',
            f'*model:{model}',
            '-utf8',
        ]
        logger.debug('Argumentos completos: %s', args)
        return args

    def connect(*args) -> bool:
        logger.debug('Método connect chamado com args: %s', args)
        return False

    def close(self):
        logger.info('Fechando aplicativo')
        if self.subprocess and self.subprocess.poll() is None:
            logger.debug('Terminando processo em execução')
            self.subprocess.terminate()
        return_code = self.subprocess.returncode or self.subprocess.poll()
        return_code = return_code if return_code is not None else 0
        logger.info(
            'Aplicativo fechado com código de retorno: %s', return_code
        )
        return return_code

    def write(self, data: str):
        logger.debug('Escrevendo dados para o processo: %s', data)
        try:
            self.subprocess.stdin.write(data)
            self.subprocess.stdin.flush()
            logger.debug('Dados escritos com sucesso')
        except Exception as e:
            logger.error('Erro ao escrever dados: %s', e)
            raise

    def readline(self, timeout=5) -> bytes:
        try:
            logger.debug('Aguardando dados no buffer do processo')
            line = self.subprocess.stdout.readline()
            logger.debug('Linha lida: %s', line)
            return line
        except Exception as e:
            logger.error('Erro ao ler linha: %s', e)
            raise


class Command(AbstractCommand):
    def __init__(self, app: ExecutableApp, cmdstr: bytes | str) -> None:
        logger.debug('Inicializando Command com comando: %s', cmdstr)
        if isinstance(cmdstr, str):
            cmdstr = bytes(cmdstr, 'utf-8', errors='replace')
        self.app = app
        self.cmdstr = cmdstr
        self.status_line = None
        self.data = []

    def execute(self) -> bool:
        logger.debug('Executando comando: %s', self.cmdstr)
        try:
            self.app.write(self.cmdstr + b'\n')

            while True:
                line = self.app.readline()
                if not line.startswith('data:'.encode('utf-8')):
                    self.status_line = line.rstrip()
                    logger.debug('Status line: %s', self.status_line)
                    result = self.app.readline().rstrip()
                    logger.debug('Resultado: %s', result)
                    return self.handle_result(result.decode('utf-8'))

                logger.debug('Dados recebidos: %s', line)
                self.data.append(line[6:].rstrip('\n\r'.encode('utf-8')))

        except Exception as e:
            logger.error(
                'Erro durante execução do comando %s: %s', self.cmdstr, e
            )
            raise

    def handle_result(self, result: str) -> bool:
        logger.debug('Processando resultado: %s', result)
        count = 0
        max_loop = 2
        while count < max_loop:
            try:
                if not result and self.cmdstr == b'Quit':
                    logger.info('Comando Quit executado com sucesso')
                    return True
                elif result.lower() == 'ok':
                    logger.debug('Comando executado com sucesso (OK)')
                    return True
                else:
                    error_msg = f'"erro" esperado, mas recebido: {result}.'
                    logger.info(error_msg)
                    raise ValueError(error_msg)
            except ValueError:
                logger.warning(
                    'Tentativa %s/%s falhou, aguardando 1s',
                    count + 1,
                    max_loop,
                )
                sleep(0.35)
                count += 1

        msg = b'[sem mensagem de erro]'
        if self.data:
            msg = ''.encode('utf-8').join(self.data).rstrip()
        error_msg = msg.decode('utf-8')

        if (
            'keyboard locked' in error_msg.lower()
            or 'canceled' in error_msg.lower()
        ):
            logger.error('Teclado travado detectado: %s', error_msg)
            raise KeyboardStateError(error_msg)

        logger.error('Comando falhou: %s', error_msg)
        raise CommandError(error_msg)


class Status:
    def __init__(self, status_line: str) -> None:
        logger.debug('Inicializando Status com linha: %s', status_line)
        if not status_line:
            status_line = (' ' * 12).encode('utf-8')
            logger.debug('Status line vazia, usando padrão')
        self.status_line = status_line
        parts = status_line.split(' '.encode('utf-8'))

        try:
            self.keyboard = parts[0] or None
            self.screen_format = parts[1] or None
            self.field_protection = parts[2] or None
            self.connection_state = parts[3] or None
            self.emulator_mode = parts[4] or None
            self.model_number = parts[5] or None
            self.row_number = parts[6] or None
            self.col_number = parts[7] or None
            self.cursor_row = parts[8] or None
            self.cursor_col = parts[9] or None
            self.window_id = parts[10] or None
            self.exec_time = parts[11] or None
            logger.debug(
                'Status: connection_state=%s, emulator_mode=%s',
                self.connection_state,
                self.emulator_mode,
            )
        except IndexError as e:
            logger.error(
                'Status não tem items suficientes: %s (status_line=%s)',
                e,
                status_line,
            )

    def __str__(self) -> str:
        return f'Status: {self.status_line}'


class Wc3270App(ExecutableApp):
    args = ['-xrm', '"wc3270.unlockDelay: False"']

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info('Inicializando Wc3270App com modelo: %s', model)
        self.args = self._get_executable_app_args(model)
        self.script_port = Wc3270App._get_free_port()
        logger.debug('Porta de script alocada: %s', self.script_port)
        super().__init__(shell=True, model=model)

    @staticmethod
    def _get_free_port() -> str:
        logger.debug('Obtendo porta livre para comunicação')
        try:
            with closing(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ) as s:
                s.bind(('127.0.0.1', 0))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                port = s.getsockname()[1]
                logger.debug('Porta livre obtida: %s', port)
                return port
        except Exception as e:
            logger.error('Erro ao obter porta livre: %s', e)
            raise

    @cache
    def _make_socket(self) -> None:
        logger.info('Criando socket para porta %s', self.script_port)
        self.socket = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        count = 0
        max_loop = 5
        while count < max_loop:
            try:
                logger.debug(
                    'Tentativa %s/%s port:%s',
                    count + 1,
                    max_loop,
                    self.script_port,
                )
                sock.connect(('localhost', self.script_port))
                logger.info('Conexão de socket estabelecida com sucesso')
                break
            except socket.error as e:
                if e.errno != errno.ECONNREFUSED:
                    logger.error('Erro de conexão não recuperável: %s', e)
                    raise NotConnectedException
                logger.warning(
                    'Conexão recusada, tentando novamente em 1s (%s/%s)',
                    count + 1,
                    max_loop,
                )
                sleep(1)
                count += 1
                if count >= max_loop:
                    logger.error(
                        'Falha ao conectar após %s tentativas', max_loop
                    )

        self.socket_fh = sock.makefile(mode='rwb')
        logger.debug('File handle do socket criado')

    def connect(self, host: str) -> bool:
        logger.info('Conectando ao host: %s', host)
        self.args = [
            'start',
            '/wait',
            '""',
            f'"{get_binary_path("windows", "wc3270")}"',
        ] + self.args
        self.args.extend(['-scriptport', str(self.script_port), host])
        logger.debug('Argumentos completos: %s', self.args)

        try:
            self._spawn_app(' '.join(self.args))
            self._make_socket()
            return True
        except Exception as e:
            logger.error('Erro ao conectar ao host %s: %s', host, e)
            raise

    def close(self) -> None:
        logger.info('Fechando conexão de socket')
        try:
            self.socket.close()
            logger.debug('Socket fechado com sucesso')
        except Exception as e:
            logger.error('Erro ao fechar socket: %s', e)

    def write(self, data: str) -> None:
        logger.debug('Escrevendo dados para socket: %s', data)
        if self.socket_fh is None:
            logger.error('Tentativa de escrita em socket não inicializado')
            raise NotConnectedException
        try:
            self.socket_fh.write(data)
            self.socket_fh.flush()
            logger.debug('Dados escritos com sucesso')
        except OSError as e:
            logger.error('Erro de E/S ao escrever no socket: %s', e)
            raise NotConnectedException

    def readline(self) -> bytes:
        logger.debug('Lendo linha do socket')
        if self.socket_fh is None:
            logger.error('Tentativa de leitura de socket não inicializado')
            raise NotConnectedException
        try:
            line = self.socket_fh.readline()
            logger.debug('Linha lida: %s', line)
            return line
        except Exception as e:
            logger.error('Erro ao ler do socket: %s', e)
            raise NotConnectedException


class Ws3270App(ExecutableApp):
    args = [
        get_binary_path('windows', 'ws3270'),
        '-xrm',
        'ws3270.unlockDelay:False',
    ]

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info('Inicializando Ws3270App com modelo: %s', model)
        super().__init__(shell=False, model=model)


class X3270App(ExecutableApp):
    args = [
        get_binary_path('linux', 'x3270'),
        '-xrm',
        'x3270.unlockDelay:False',
        '-script',
    ]

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info('Inicializando X3270App com modelo: %s', model)
        super().__init__(shell=False, model=model)


class S3270App(ExecutableApp):
    args = [
        get_binary_path('linux', 's3270'),
        '-xrm',
        's3270.unlockDelay:False',
    ]

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info('Inicializando S3270App com modelo: %s', model)
        super().__init__(shell=True, model=model)


# Mapeamento de cor de campo 3270 (SF/SA aa=42) para código de cor
# ANSI SGR (foreground), conforme tabela de atributos do x3270-script(1).
_FIELD_COLOR_ANSI = {
    'f0': None,  # neutral black (mantém a cor padrão do terminal)
    'f1': 34,  # blue
    'f2': 31,  # red
    'f3': 35,  # pink
    'f4': 32,  # green
    'f5': 36,  # turquoise
    'f6': 33,  # yellow
    'f7': 37,  # neutral white
    'f8': 30,  # black
    'f9': 94,  # deep blue
    'fa': 93,  # orange (aproximado, ANSI não tem laranja nativo)
    'fb': 95,  # purple
    'fc': 92,  # pale green
    'fd': 96,  # pale turquoise
    'fe': 90,  # grey
    'ff': 97,  # white
}

# Mapeamento de destaque de campo (SF/SA aa=41) para código SGR.
_FIELD_HIGHLIGHT_ANSI = {
    'f1': 5,  # blink
    'f2': 7,  # reverse
    'f4': 4,  # underscore
    'f8': 1,  # intensify (tratado como negrito)
}

_MASK_CHAR = '*'
_MASK_SKIP_CHARS = frozenset((' ', '\x00'))
_SF_TOKEN_RE = re.compile(r'^(SF|SA)\((.*)\)$')
_GE_TOKEN_RE = re.compile(r'^GE\((.*)\)$')

# Subcampo de 2 bits (posições 0x08 e 0x04) do atributo básico 3270 (c0)
# que indica o tipo de exibição do campo.
_BASIC_DISPLAY_BITS_MASK = 0x0C
_BASIC_INTENSIFIED_BITS = 0x08
_BASIC_NON_DISPLAY_BITS = 0x0C


class _FieldStyle:
    """Estado de estilo do campo 3270 (cor/destaque) durante o dump de tela."""

    __slots__ = ('fg', 'highlight', 'bold', 'hidden')

    def __init__(self) -> None:
        self.fg = None
        self.highlight = None
        self.bold = False
        self.hidden = False

    def reset(self) -> None:
        self.fg = None
        self.highlight = None
        self.bold = False
        self.hidden = False

    def apply(self, attrs: dict) -> None:
        basic = attrs.get('c0')
        if basic is not None:
            display_bits = int(basic, 16) & _BASIC_DISPLAY_BITS_MASK
            self.bold = self.bold or display_bits == _BASIC_INTENSIFIED_BITS
            self.hidden = (
                self.hidden or display_bits == _BASIC_NON_DISPLAY_BITS
            )

        highlight = attrs.get('41')
        if highlight in _FIELD_HIGHLIGHT_ANSI:
            code = _FIELD_HIGHLIGHT_ANSI[highlight]
            if code == 1:
                self.bold = True
            else:
                self.highlight = code

        color = attrs.get('42')
        if color in _FIELD_COLOR_ANSI:
            self.fg = _FIELD_COLOR_ANSI[color]

    def sgr(self) -> str | None:
        codes = []
        if self.bold:
            codes.append('1')
        if self.highlight:
            codes.append(str(self.highlight))
        if self.fg is not None:
            codes.append(str(self.fg))
        return f'\x1b[{";".join(codes)}m' if codes else None


def _parse_attr_pairs(spec: str) -> dict:
    attrs = {}
    for pair in spec.split(','):
        if '=' not in pair:
            continue
        key, value = pair.split('=', 1)
        attrs[key.strip().lower()] = value.strip().lower()
    return attrs


def _render_screen_row(row: str, style: _FieldStyle, mask_hidden: bool) -> str:
    rendered = []
    last_sgr = None

    def emit(char: str) -> None:
        nonlocal last_sgr
        sgr = style.sgr()
        if sgr != last_sgr:
            rendered.append(sgr if sgr is not None else '\x1b[0m')
            last_sgr = sgr
        rendered.append(char)

    for token in row.split():
        match = _SF_TOKEN_RE.match(token)
        if match:
            kind, spec = match.groups()
            attrs = _parse_attr_pairs(spec)
            if kind == 'SF':
                style.reset()
                style.apply(attrs)
                emit(' ')
            else:  # SA: atributo estendido, não ocupa posição na tela
                style.apply(attrs)
            continue

        if token == '-':
            continue  # segunda posição de caractere DBCS, sem conteúdo próprio

        ge_match = _GE_TOKEN_RE.match(token)
        hex_token = ge_match.group(1) if ge_match else token

        try:
            char = bytes.fromhex(hex_token).decode('utf-8', errors='replace')
        except ValueError:
            char = hex_token

        if style.hidden and mask_hidden:
            char = ''.join(
                c if c in _MASK_SKIP_CHARS else _MASK_CHAR for c in char
            )

        emit(char)

    if last_sgr is not None:
        rendered.append('\x1b[0m')

    return ''.join(rendered)


class X3270Cmd(AbstractEmulatorCmd):  # noqa: PLR0904
    def __init__(self, time_unlock: int = 60) -> None:
        logger.info('Inicializando X3270Cmd com time_unlock: %s', time_unlock)
        self.time_unlock = time_unlock

    def __getattr__(self, name):
        def x3270_builtin_func(*args, **kwargs):
            return x3270_command(self, name, *args, **kwargs)

        return x3270_builtin_func

    def clear_screen(self) -> None:
        logger.info('Limpando tela')
        count = 0
        max_loop = 6
        while count < max_loop:
            logger.debug('Tentativa %s/%s de limpar tela', count + 1, max_loop)
            self.clear()
            self.wait_unlock()
            if not self.get_full_screen(header=True).strip():
                logger.info('Tela limpa com sucesso')
                break
            logger.debug(
                'Tela não foi limpa completamente na tentativa %s', count + 1
            )
            count += 1
        if count >= max_loop:
            logger.warning(
                'Não foi possível limpar a tela completamente'
                ' após %s tentativas',
                max_loop,
            )

    def wait_for_field(self, timeout: int = 30) -> None:
        logger.debug('Aguardando campo de entrada (timeout=%ss)', timeout)
        try:
            self.wait(timeout, 'InputField')
            logger.debug('Campo de entrada carregado.')
        except CommandError as e:
            logger.warning(
                'Timeout atingido: %ss. Campo de entrada não encontrado (%s).',
                timeout,
                e,
            )

    def wait_unlock(self) -> None:
        logger.debug(
            'Aguardando desbloqueio do host (timeout=%ss)', self.time_unlock
        )
        try:
            sleep(0.03)
            self.wait(self.time_unlock, 'unlock')
            logger.debug('Host desbloqueado.')
        except CommandError as e:
            logger.warning(
                'Timeout atingido: %ss. Host não desbloqueado (%s).',
                self.time_unlock,
                e,
            )

    def wait_string_found(
        self,
        ypos: int,
        xpos: int,
        string: str,
        equal: bool = True,
        timeout: int = 5,
    ) -> bool:
        logger.debug(
            'Aguardando string=%s na posição (%s,%s), equal=%s, timeout=%ss',
            string,
            ypos,
            xpos,
            equal,
            timeout,
        )

        end_time = time() + timeout
        result = None

        while time() < end_time:
            try:
                found = self.get_string(ypos, xpos, len(string))
                logger.debug("String encontrada: '%s'", found)
                if equal:
                    result = found == string
                else:
                    result = found != string
                logger.debug('Resultado da comparação: %s', result)
                if result:
                    logger.debug('String localizada.')
                    return result
            except Exception as ex:
                logger.warning(
                    'Falha ao buscar string, tentando novamente: %s', ex
                )
                continue

        logger.warning(
            'Timeout atingido após %ss, resultado final: %s', timeout, result
        )
        return result

    def string_found(self, ypos: int, xpos: int, string: str) -> bool:
        logger.debug(
            'Verificando se string=%s existe na posição (%s,%s)',
            string,
            ypos,
            xpos,
        )
        try:
            found = self.get_string(ypos, xpos, len(string))
            result = found == string
            logger.debug("Resultado: %s (encontrado: '%s')", result, found)
            return result
        except Exception as e:
            logger.error('Erro ao verificar string=%s: %s', string, e)
            return False

    def delete_field(self) -> None:
        logger.debug('Deletando campo atual')
        self.deletefield()
        logger.debug('Campo deletado')

    def move_to(self, ypos: int, xpos: int) -> None:
        logger.debug('Movendo cursor para posição (%s,%s)', ypos, xpos)
        self.movecursor1(ypos, xpos)
        logger.debug('Cursor movido')

    def send_pf(self, value: int) -> None:
        logger.info('Enviando tecla PF%s', value)
        self.pf(value)
        logger.debug('PF%s enviado e tela desbloqueada', value)

    def send_string(
        self,
        tosend: str,
        ypos: int | None = None,
        xpos: int | None = None,
        password: bool = False,
    ) -> None:
        if not tosend:
            logger.debug('tosend não é string, send_string não executado.')
            return
        # Remove caracteres especiais
        original = tosend
        tosend = re.sub(r"[()\"']", '', tosend)

        tosend_str = 'password' if password else tosend

        if original != tosend:
            logger.debug(
                'String modificada para %s (removidos caracteres especiais)',
                tosend_str,
            )

        if xpos is not None and ypos is not None:
            logger.info(
                "Enviando string '%s' para posição ypos=%s xpos=%s",
                tosend_str,
                ypos,
                xpos,
            )
            self.move_to(ypos, xpos)
        else:
            logger.info("Enviando string '%s' na posição atual.", tosend_str)

        self.string(f'"{tosend}"')
        self.wait_unlock()
        logger.debug("String '%s' enviada para o emulador.", tosend_str)

    def send_enter(self, wait_input: bool = False) -> None:
        logger.info('Enviando tecla ENTER')
        self.enter()
        if wait_input:
            self.wait_for_field()
        else:
            self.wait_unlock()
        logger.debug('ENTER enviado e tela desbloqueada')

    def send_home(self) -> None:
        logger.info('Enviando tecla HOME')
        self.home()
        self.wait_unlock()
        logger.debug('HOME enviado e tela desbloqueada')

    def get_string(self, ypos: int, xpos: int, length: int) -> str:
        logger.debug(
            'Obtendo string na posição (%s,%s) com comprimento %s',
            ypos,
            xpos,
            length,
        )
        try:
            self.check_limits(ypos, xpos)
            if (xpos + length) > (self.model_dimensions['columns'] + 1):
                logger.error(
                    'Comprimento excede limite da tela: %s+%s > %s',
                    xpos,
                    length,
                    self.model_dimensions['columns'] + 1,
                )
                raise FieldTruncateError

            xpos -= 1
            ypos -= 1
            result = self.ascii(ypos, xpos, length)
            logger.debug("String obtida: '%s'", result)
            return result
        except Exception as e:
            logger.error('Erro ao obter string: %s', e)
            raise

    def get_string_area(
        self, yposi: int, xposi: int, ypose: int, xpose: int
    ) -> str:
        logger.debug(
            'Obtendo área de texto de (%s,%s) até (%s,%s)',
            yposi,
            xposi,
            ypose,
            xpose,
        )
        try:
            self.check_limits(yposi, xposi)
            self.check_limits(ypose, xpose)
            yposi -= 1
            xposi -= 1
            ypose -= yposi
            xpose -= xposi
            result = self.ascii(yposi, xposi, ypose, xpose)
            logger.debug('Área obtida com %s caracteres', len(result))
            return result
        except Exception as e:
            logger.error('Erro ao obter área de texto: %s', e)
            raise

    def get_full_screen(self, header: bool = True) -> str:
        logger.debug(
            'Obtendo conteúdo completo da tela (com header: %s)', header
        )
        try:
            text = self.ascii()
            if not header:
                start = self.model_dimensions['columns']
                text = text[start:]
                logger.debug('Header removido do conteúdo')
            logger.debug('Conteúdo obtido com %s caracteres', len(text))
            return text
        except Exception as e:
            logger.error('Erro ao obter conteúdo da tela. Detalhe: %s', e)
            raise

    def save_screen(self, file_path: str, file_name: str):
        logger.info('Salvando tela em %s\\%s.html', file_path, file_name)
        try:
            if not os.path.exists(file_path):
                logger.debug('Criando diretório: %s', file_path)
                os.makedirs(file_path)
            self.printtext('html', 'file', f'{file_path}\\{file_name}.html')
            logger.info('Tela salva com sucesso')
        except Exception as e:
            logger.error('Erro ao salvar tela. Detalhe: %s', e)
            raise

    def get_screen_log(self, mask_hidden: bool = True) -> str:
        logger.debug(
            'Gerando dump colorido da tela para log (mask_hidden=%s)',
            mask_hidden,
        )
        try:
            cmd = self._exec_command(b'ReadBuffer(Ascii)', False)
            style = _FieldStyle()
            rows = [
                _render_screen_row(row.decode('utf-8'), style, mask_hidden)
                for row in cmd.data
            ]
            result = '\n'.join(rows)
            logger.debug('Dump de tela gerado com %s linhas', len(rows))
            return result
        except Exception as e:
            logger.error('Erro ao gerar dump colorido da tela: %s', e)
            raise

    def check_limits(self, ypos, xpos):
        logger.debug('Verificando limites para posição (%s,%s)', ypos, xpos)
        if ypos > self.model_dimensions['rows']:
            error_msg = (
                f'Você excedeu o limite do eixo y da tela do mainframe: '
                f'{ypos} > {self.model_dimensions["rows"]}'
            )
            logger.error(error_msg)
            raise FieldTruncateError(error_msg)
        if xpos > self.model_dimensions['columns']:
            error_msg = (
                f'Você excedeu o limite do eixo x da tela do mainframe: '
                f'{xpos} > {self.model_dimensions["columns"]}'
            )
            logger.error(error_msg)
            raise FieldTruncateError(error_msg)
        logger.debug('Posição dentro dos limites')

    def search_string(self, string: str, ignore_case: bool = False) -> bool:
        logger.info(
            "Buscando texto '%s' na tela (ignore_case=%s)", string, ignore_case
        )
        try:
            for ypos in range(1, self.model_dimensions['rows'] + 1):
                line = self.get_string(
                    ypos, 1, self.model_dimensions['columns']
                )
                if ignore_case:
                    string_comp = string.lower()
                    line_comp = line.lower()
                    logger.debug(
                        'Comparando (ignorando case) na linha %s', ypos
                    )
                else:
                    string_comp = string
                    line_comp = line
                    logger.debug(
                        'Comparando (case sensitive) na linha %s', ypos
                    )

                if string_comp in line_comp:
                    logger.info('Texto encontrada na linha %s', ypos)
                    return True

            logger.info('Texto não encontrada em nenhuma linha')
            return False
        except Exception as e:
            logger.error('Erro durante busca de texto: %s', e)
            return False

    def get_string_positions(
        self, string: str, ignore_case=False
    ) -> list[tuple[int]]:
        logger.info(
            "Buscando posições da texto '%s' (ignore_case=%s)",
            string,
            ignore_case,
        )
        try:
            screen_content = self.get_full_screen(header=True)
            flags = 0 if not ignore_case else re.IGNORECASE
            indices_object = re.finditer(
                re.escape(string), screen_content, flags
            )
            indices = [index.start() for index in indices_object]
            logger.debug('Encontradas %s ocorrências', len(indices))

            positions = [
                self._get_ypos_and_xpos_from_index(index + 1)
                for index in indices
            ]
            logger.info('Posições encontradas: %s', positions)
            return positions
        except Exception as e:
            logger.error('Erro ao buscar posições: %s', e)
            return []

    def _get_ypos_and_xpos_from_index(self, index):
        logger.debug('Convertendo índice %s para coordenadas (y,x)', index)
        col_dimentions = self.model_dimensions['columns'] + 1
        ypos = math.ceil(index / col_dimentions)
        remainder = index % col_dimentions
        if remainder == 0:
            xpos = col_dimentions
        else:
            xpos = remainder
        logger.debug('Índice %s convertido para (%s,%s)', index, ypos, xpos)
        return (ypos, xpos)


class X3270(AbstractEmulator, X3270Cmd):
    def __init__(
        self,
        visible: bool = False,
        model: MODEL_TYPE = '2',
        save_log_file: bool = False,
        time_unlock: int = 60,
    ) -> None:
        if save_log_file:
            logging.config.dictConfig(LOGGING_CONFIG)
        X3270Cmd.__init__(self, time_unlock=time_unlock)
        logger.info(
            'Inicializando X3270 (visible=%s, model=%s)', visible, model
        )
        self.model = model
        self.model_dimensions = MODEL_DIMENSIONS[model]
        self.visible = visible
        self.app: ExecutableApp = self._create_app()
        self.is_terminated = False
        self.host = None
        self.port = None
        self.tls = None
        self.mode_3270 = None
        self.last_command_time = None
        logger.debug('X3270 inicializado')

    def _create_app(self) -> None:
        logger.info('Criando aplicativo emulador')
        try:
            if os.name == 'nt':  # windows
                if self.visible:
                    logger.debug('Criando Wc3270App (Windows, visível)')
                    return Wc3270App(self.model)
                logger.debug('Criando Ws3270App (Windows, não visível)')
                return Ws3270App(self.model)

            if self.visible:  # linux
                logger.debug('Criando X3270App (Linux, visível)')
                return X3270App(self.model)
            logger.debug('Criando S3270App (Linux, não visível)')
            return S3270App(self.model)

        except Exception as e:
            logger.error('Erro ao criar aplicativo: %s', e)
            raise

    def _exec_command(self, cmdstr: str, run_raise: bool = False) -> Command:
        logger.debug('Executando comando: %s', cmdstr)
        if self.is_terminated:
            error_msg = 'Tentativa de executar comando em emulador terminado'
            logger.error(error_msg)
            raise TerminatedError
        try:
            cmd = Command(self.app, cmdstr)
            cmd.execute()
            self.status = Status(cmd.status_line)
            self.last_command_time = time()
            logger.debug('Comando executado, status: %s', self.status)
            return cmd
        except NotConnectedException:
            logger.error('Emulador não conectado.')
            raise NotConnectedException
        except KeyboardStateError:
            if run_raise:
                raise NotConnectedException
            logger.error('KeyboardStateError ao executar %s', cmdstr)
            raise

    def terminate(self) -> None:
        logger.info('Terminando emulador')
        if not self.is_terminated:
            try:
                logger.debug('Enviando comando quit')
                self.quit()
            except BrokenPipeError:
                logger.warning('BrokenPipeError ao enviar quit, ignorando')
                self.ignore()
            except socket.error as ex:
                if ex.errno != errno.ECONNRESET:
                    logger.error('Erro de socket ao terminar: %s', ex)
                    raise ConnectionError
                logger.warning('Erro de conexão resetada: %s', ex)

        logger.debug('Fechando aplicativo')
        self.app.close()
        self.is_terminated = True
        logger.info('Emulador terminado com sucesso')

    def is_connected(self) -> bool:
        logger.debug('Verificando estado de conexão')
        try:
            # Verifica tempo desde o último comando
            elapsed_max = 600
            if self.last_command_time:
                elapsed = time() - self.last_command_time
                if elapsed > elapsed_max:
                    logger.warning(
                        'Tempo de inatividade excedido: %.2f segundos', elapsed
                    )
                    return False

            self.query('ConnectionState')
            is_connected = self.status.connection_state.startswith(b'C(')
            logger.info('Estado de conexão: %s', is_connected)
            return is_connected
        except Exception as e:
            logger.error('Erro ao verificar conexão: %s', e)
            return False

    def connect_host(
        self,
        host: str,
        port: int | str,
        tls: bool = True,
        mode_3270: bool = True,
    ) -> None:
        logger.info('Conectando ao host: %s:%s (tls=%s)', host, port, tls)
        self.host = host
        self.port = port
        self.tls = tls
        self.mode_3270 = mode_3270
        tls_prefix = 'L:Y:' if tls else ''
        strint_conn = f'{tls_prefix}{host}:{port}'
        logger.debug('String de conexão: %s', strint_conn)

        try:
            if self.app:
                if not self.app.connect(strint_conn):
                    logger.debug(
                        'Método connect do app retornou False, '
                        'tentando método connect direto'
                    )
                    self.connect(strint_conn)
                if mode_3270:
                    logger.debug('Aguardando modo 3270')
                    self.wait(5, '3270mode')
                logger.info('Conexão estabelecida com sucesso')
        except CommandError as e:
            logger.warning('CommandError durante conexão: %s', e)
        except Exception as e:
            logger.error('Erro ao conectar: %s', e)
            raise

    def reconnect_host(self) -> 'X3270':
        logger.info('Tentando reconectar ao host')
        try:
            logger.debug('Executando comando reconnect')
            self.reconnect()
            logger.info('Reconexão bem-sucedida')
            return self
        except Exception as e:
            logger.warning('Erro durante reconexão: %s', e)
            logger.debug('Terminando instância atual')
            self.terminate()
        finally:
            logger.info('Criando nova instância para reconexão')
            args = self.host, self.port, self.tls, self.mode_3270
            logger.debug('Argumentos para nova instância: %s', args)
            new_instance = X3270(self.visible, self.model)
            new_instance.connect_host(*args)
            logger.debug('Nova instância criada com sucesso')
            # Atualiza todos os atributos de self com os do novo objeto
            self.__dict__.update(new_instance.__dict__)

            logger.debug('Atributos de self atualizados com sucesso')
            return self
