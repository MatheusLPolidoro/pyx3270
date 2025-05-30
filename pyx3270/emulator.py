import errno
import logging
import math
import os
import pathlib
import re
import socket
import subprocess
import sys
from contextlib import closing
from functools import cache, lru_cache
from time import sleep, time
from typing import Literal
from logging.handlers import TimedRotatingFileHandler

sys.path.append(str(pathlib.Path(__file__).parent))

from command_config import command_map
from exceptions import (
    CommandError,
    FieldTruncateError,
    NotConnectedException,
    TerminatedError,
)
from iemulator import (
    AbstractCommand,
    AbstractEmulator,
    AbstractEmulatorCmd,
    AbstractExecutableApp,
)

logger = logging.getLogger('x3270_emulator')
logger.setLevel(logging.INFO)

# Evita duplicação de handlers
if not logger.handlers:
    handler = TimedRotatingFileHandler(
        filename='x3270_emulator.log',
        when='midnight',  # Roda diariamente
        interval=1,  # Intervalo de 1 dia
        backupCount=7,  # Mantém arquivos dos últimos 7 dias
        encoding='utf-8',  # Mantém acentos
    )

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

# Se quiser evitar que os logs sejam propagados para o logger raiz
logger.propagate = False


BINARY_FOLDER = f'{os.path.dirname(__file__)}/binary'
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
        logger.info(
            f'Inicializando ExecutableApp (shell={shell}, model={model})'
        )
        self.shell = shell
        self.subprocess = None
        self.args = self._get_executable_app_args(model)
        self._spawn_app()

    @lru_cache
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
            logger.debug(f'Executando comando: {self.args}')
            self.subprocess = subprocess.Popen(self.args, **kwargs)
            logger.info(f'Processo iniciado com PID: {self.subprocess.pid}')
        except Exception as e:
            logger.error(f'Erro ao iniciar processo: {e}', exc_info=True)
            raise

    def _get_executable_app_args(self, model: MODEL_TYPE) -> list:
        logger.debug(f'Obtendo argumentos para modelo: {model}')
        args = self.__class__.args + [
            '-xrm',
            f'*model: {model}',
            '-localcp',
            'utf8',
            '-utf8',
        ]
        logger.debug(f'Argumentos completos: {args}')
        return args

    def connect(*args) -> bool:
        logger.debug(f'Método connect chamado com args: {args}')
        return False

    def close(self):
        logger.info('Fechando aplicativo')
        if self.subprocess and self.subprocess.poll() is None:
            logger.debug('Terminando processo em execução')
            self.subprocess.terminate()
        return_code = self.subprocess.returncode or self.subprocess.poll()
        return_code = return_code if return_code is not None else 0
        logger.info(f'Aplicativo fechado com código de retorno: {return_code}')
        return return_code

    def write(self, data: str):
        logger.debug(f'Escrevendo dados para o processo: {data}')
        try:
            self.subprocess.stdin.write(data)
            self.subprocess.stdin.flush()
            logger.debug('Dados escritos com sucesso')
        except Exception as e:
            logger.error(f'Erro ao escrever dados: {e}', exc_info=True)
            raise

    def readline(self):
        logger.debug('Lendo linha da saída do processo')
        try:
            line = self.subprocess.stdout.readline()
            logger.debug(f'Linha lida: {line}')
            return line
        except Exception as e:
            logger.error(f'Erro ao ler linha: {e}', exc_info=True)
            raise


class Command(AbstractCommand):
    def __init__(self, app: ExecutableApp, cmdstr: bytes | str) -> None:
        logger.debug(f'Inicializando Command com comando: {cmdstr}')
        if isinstance(cmdstr, str):
            cmdstr = bytes(cmdstr, 'utf-8', errors='replace')
        self.app = app
        self.cmdstr = cmdstr
        self.status_line = None
        self.data = []

    def execute(self) -> bool:
        logger.info(f'Executando comando: {self.cmdstr}')
        try:
            self.app.write(self.cmdstr + b'\n')

            while True:
                line = self.app.readline()
                if not line.startswith('data:'.encode('utf-8')):
                    self.status_line = line.rstrip()
                    logger.debug(f'Status line: {self.status_line}')
                    result = self.app.readline().rstrip()
                    logger.debug(f'Resultado: {result}')
                    return self.handle_result(result.decode('utf-8'))

                logger.debug(f'Dados recebidos: {line}')
                self.data.append(line[6:].rstrip('\n\r'.encode('utf-8')))

        except Exception as e:
            logger.error(
                f'Erro durante execução do comando: {e}', exc_info=True
            )
            raise

    def handle_result(self, result: str) -> bool:
        logger.debug(f'Processando resultado: {result}')
        count = 0
        max_loop = 5
        while count < max_loop:
            try:
                if not result and self.cmdstr == b'Quit':
                    logger.info('Comando Quit executado com sucesso')
                    return True
                elif result.lower() == 'ok':
                    logger.info('Comando executado com sucesso (OK)')
                    return True
                else:
                    error_msg = f'"erro" esperado, mas recebido: {result}.'
                    logger.warning(error_msg)
                    raise ValueError(error_msg)
            except ValueError:
                logger.warning(
                    f'Tentativa {count + 1}/{max_loop} falhou, aguardando 1s'
                )
                sleep(0.35)
                count += 1

        msg = b'[sem mensagem de erro]'
        if self.data:
            msg = ''.encode('utf-8').join(self.data).rstrip()
        error_msg = msg.decode('utf-8')
        logger.error(f'Comando falhou: {error_msg}')
        raise CommandError(error_msg)


class Status:
    def __init__(self, status_line: str) -> None:
        logger.debug(f'Inicializando Status com linha: {status_line}')
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
                f'Status inicializado: connection_state={self.connection_state}, emulator_mode={self.emulator_mode}'
            )
        except IndexError:
            logger.error(f'Status não tem items suficientes.')

    def __str__(self) -> str:
        return f'Status: {self.status_line}'


class Wc3270App(ExecutableApp):
    args = ['-xrm', 'wc3270.unlockDelay: False']

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando Wc3270App com modelo: {model}')
        self.args = self._get_executable_app_args(model)
        self.shell = True
        self.script_port = Wc3270App._get_free_port()
        logger.debug(f'Porta de script alocada: {self.script_port}')
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
                logger.debug(f'Porta livre obtida: {port}')
                return port
        except Exception as e:
            logger.error(f'Erro ao obter porta livre: {e}', exc_info=True)
            raise

    @cache
    def _make_socket(self) -> None:
        logger.info(f'Criando socket para porta {self.script_port}')
        self.socket = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        count = 0
        max_loop = 5
        while count < max_loop:
            try:
                logger.debug(
                    f'Tentativa {count + 1}/{max_loop} de conexão ao localhost:{self.script_port}'
                )
                sock.connect(('localhost', self.script_port))
                logger.info('Conexão de socket estabelecida com sucesso')
                break
            except socket.error as e:
                if e.errno != errno.ECONNREFUSED:
                    logger.error(
                        f'Erro de conexão não recuperável: {e}', exc_info=True
                    )
                    raise NotConnectedException
                logger.warning(
                    f'Conexão recusada, tentando novamente em 1s (tentativa {count + 1}/{max_loop})'
                )
                sleep(1)
                count += 1
                if count >= max_loop:
                    logger.error(
                        f'Falha ao conectar após {max_loop} tentativas'
                    )

        self.socket_fh = sock.makefile(mode='rwb')
        logger.debug('File handle do socket criado')

    def connect(self, host: str) -> bool:
        logger.info(f'Conectando ao host: {host}')
        self.args = [
            'start',
            '/wait',
            f'{BINARY_FOLDER}/wc3270',
        ] + self.args
        self.args.extend(['-scriptport', str(self.script_port), host])
        logger.debug(f'Argumentos completos: {self.args}')

        try:
            self._spawn_app(tuple(self.args))
            self._make_socket()
            logger.info('Conexão estabelecida com sucesso')
            return True
        except Exception as e:
            logger.error(f'Erro ao conectar: {e}', exc_info=True)
            raise

    def close(self) -> None:
        logger.info('Fechando conexão de socket')
        try:
            self.socket.close()
            logger.debug('Socket fechado com sucesso')
        except Exception as e:
            logger.error(f'Erro ao fechar socket: {e}', exc_info=True)

    def write(self, data: str) -> None:
        logger.debug(f'Escrevendo dados para socket: {data}')
        if self.socket_fh is None:
            logger.error('Tentativa de escrita em socket não inicializado')
            raise NotConnectedException
        try:
            self.socket_fh.write(data)
            self.socket_fh.flush()
            logger.debug('Dados escritos com sucesso')
        except OSError as e:
            logger.error(
                f'Erro de E/S ao escrever no socket: {e}', exc_info=True
            )
            raise NotConnectedException

    def readline(self) -> bytes:
        logger.debug('Lendo linha do socket')
        if self.socket_fh is None:
            logger.error('Tentativa de leitura de socket não inicializado')
            raise NotConnectedException
        try:
            line = self.socket_fh.readline()
            logger.debug(f'Linha lida: {line}')
            return line
        except Exception as e:
            logger.error(f'Erro ao ler do socket: {e}', exc_info=True)
            raise NotConnectedException


class Ws3270App(ExecutableApp):
    args = [f'{BINARY_FOLDER}/ws3270', '-xrm', 'ws3270.unlockDelay: False']

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando Ws3270App com modelo: {model}')
        super().__init__(shell=False, model=model)


class X3270App(ExecutableApp):
    args = ['x3270', '-xrm', 'x3270.unlockDelay: False', '-script']

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando X3270App com modelo: {model}')
        super().__init__(shell=False, model=model)


class S3270App(ExecutableApp):
    args = ['s3270', '-xrm', 's3270.unlockDelay: False']

    def __init__(self, model: MODEL_TYPE) -> None:
        logger.info(f'Inicializando S3270App com modelo: {model}')
        super().__init__(shell=False, model=model)


class X3270Cmd(AbstractEmulatorCmd):
    def clear_screen(self) -> None:
        logger.info('Limpando tela')
        count = 0
        max_loop = 6
        while count < max_loop:
            logger.debug(f'Tentativa {count + 1}/{max_loop} de limpar tela')
            self.clear()
            self.wait(30, 'unlock')
            if not self.get_full_screen(header=True).strip():
                logger.info('Tela limpa com sucesso')
                break
            logger.warning(
                f'Tela não foi limpa completamente na tentativa {count + 1}'
            )
            count += 1
        if count >= max_loop:
            logger.warning(
                f'Não foi possível limpar a tela completamente após {max_loop} tentativas'
            )

    def wait_for_field(self, timeout: int = 30) -> None:
        logger.info(f'Aguardando campo de entrada (timeout={timeout}s)')
        self.wait(timeout, 'InputField')
        logger.debug('Campo de entrada encontrado ou timeout atingido')

    def wait_string_found(
        self,
        ypos: int,
        xpos: int,
        string: str,
        equal: bool = True,
        timeout: int = 5,
    ) -> bool:
        logger.info(
            f"Aguardando string '{string}' na posição ({ypos},{xpos}), equal={equal}, timeout={timeout}s"
        )

        end_time = time() + timeout
        result = None

        while time() < end_time:
            try:
                found = self.get_string(ypos, xpos, len(string))
                logger.debug(f"String encontrada: '{found}'")
                if equal:
                    result = found == string
                else:
                    result = found != string
                logger.info(f'Resultado da comparação: {result}')
                if result:
                    break
            except Exception as e:
                logger.debug(f'Erro ao buscar string: {e}, tentando novamente')
                continue

        logger.warning(
            f'Timeout atingido após {timeout}s, resultado final: {result}'
        )
        return result

    def string_found(self, ypos: int, xpos: int, string: str) -> bool:
        logger.info(
            f"Verificando se string '{string}' existe na posição ({ypos},{xpos})"
        )
        try:
            found = self.get_string(ypos, xpos, len(string))
            result = found == string
            logger.info(f"Resultado: {result} (encontrado: '{found}')")
            return result
        except Exception as e:
            logger.error(f'Erro ao verificar string: {e}', exc_info=True)
            return False

    def delete_field(self) -> None:
        logger.info('Deletando campo atual')
        self.deletefield()
        logger.debug('Campo deletado')

    def move_to(self, ypos: int, xpos: int) -> None:
        logger.info(f'Movendo cursor para posição ({ypos},{xpos})')
        self.movecursor1(ypos, xpos)
        logger.debug('Cursor movido')

    def send_pf(self, value: int) -> None:
        logger.info(f'Enviando tecla PF{value}')
        self.PF(value)
        self.wait(30, 'unlock')
        logger.debug(f'PF{value} enviado e tela desbloqueada')

    def send_string(
        self, tosend: str, ypos: int | None = None, xpos: int | None = None
    ) -> None:
        if not tosend:
            logger.info(f'tosend não é string.')
            return
        if xpos is not None and ypos is not None:
            logger.info(
                f"Enviando string '{tosend}' para posição ({ypos},{xpos})"
            )
            self.move_to(ypos, xpos)
        else:
            logger.info(f"Enviando string '{tosend}' na posição atual")

        # Remove caracteres especiais
        original = tosend
        tosend = re.sub(r"[()\"']", '', tosend)
        if original != tosend:
            logger.debug(
                f"String modificada para '{tosend}' (removidos caracteres especiais)"
            )

        self.string(tosend)
        self.wait(30, 'unlock')
        logger.debug('String enviada')

    def send_enter(self) -> None:
        logger.info('Enviando tecla ENTER')
        self.enter()
        self.wait(30, 'unlock')
        logger.debug('ENTER enviado e tela desbloqueada')

    def send_home(self) -> None:
        logger.info('Enviando tecla HOME')
        self.home()
        self.wait(30, 'unlock')
        logger.debug('HOME enviado e tela desbloqueada')

    def get_string(self, ypos: int, xpos: int, length: int) -> str:
        logger.debug(
            f'Obtendo string na posição ({ypos},{xpos}) com comprimento {length}'
        )
        try:
            self.check_limits(ypos, xpos)
            if (xpos + length) > (self.model_dimensions['columns'] + 1):
                logger.error(
                    f'Comprimento excede limite da tela: {xpos}+{length} > {self.model_dimensions["columns"] + 1}'
                )
                raise FieldTruncateError

            xpos -= 1
            ypos -= 1
            result = self.ascii(ypos, xpos, length)
            logger.debug(f"String obtida: '{result}'")
            return result
        except Exception as e:
            logger.error(f'Erro ao obter string: {e}', exc_info=True)
            raise

    def get_string_area(
        self, yposi: int, xposi: int, ypose: int, xpose: int
    ) -> str:
        logger.debug(
            f'Obtendo área de texto de ({yposi},{xposi}) até ({ypose},{xpose})'
        )
        try:
            self.check_limits(yposi, xposi)
            self.check_limits(ypose, xpose)
            yposi -= 1
            xposi -= 1
            ypose -= 1
            ypose -= yposi
            xpose -= xposi
            result = self.ascii(yposi, xposi, ypose, xpose)
            logger.debug(f'Área obtida com {len(result)} caracteres')
            return result
        except Exception as e:
            logger.error(f'Erro ao obter área de texto: {e}', exc_info=True)
            raise

    def get_full_screen(self, header: bool = True) -> str:
        logger.debug(
            f'Obtendo conteúdo completo da tela (com header: {header})'
        )
        try:
            text = self.ascii()
            if not header:
                start = (self.model_dimensions['columns'] - 1) * 2
                text = text[start:]
                logger.debug('Header removido do conteúdo')
            logger.debug(f'Conteúdo obtido com {len(text)} caracteres')
            return text
        except Exception as e:
            logger.error(f'Erro ao obter conteúdo da tela: {e}', exc_info=True)
            raise

    def save_screen(self, file_path: str, file_name: str):
        logger.info(f'Salvando tela em {file_path}\\{file_name}.html')
        try:
            if not os.path.exists(file_path):
                logger.debug(f'Criando diretório: {file_path}')
                os.makedirs(file_path)
            self.printtext('html', 'file', f'{file_path}\\{file_name}.html')
            logger.info('Tela salva com sucesso')
        except Exception as e:
            logger.error(f'Erro ao salvar tela: {e}', exc_info=True)
            raise

    def check_limits(self, ypos, xpos):
        logger.debug(f'Verificando limites para posição ({ypos},{xpos})')
        if ypos > self.model_dimensions['rows']:
            error_msg = f'Você excedeu o limite do eixo y da tela do mainframe: {ypos} > {self.model_dimensions["rows"]}'
            logger.error(error_msg)
            raise FieldTruncateError(error_msg)
        if xpos > self.model_dimensions['columns']:
            error_msg = f'Você excedeu o limite do eixo x da tela do mainframe: {xpos} > {self.model_dimensions["columns"]}'
            logger.error(error_msg)
            raise FieldTruncateError(error_msg)
        logger.debug('Posição dentro dos limites')

    def search_string(self, string: str, ignore_case: bool = False) -> bool:
        logger.info(
            f"Buscando string '{string}' na tela (ignore_case={ignore_case})"
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
                        f'Comparando (ignorando case) na linha {ypos}'
                    )
                else:
                    string_comp = string
                    line_comp = line
                    logger.debug(
                        f'Comparando (case sensitive) na linha {ypos}'
                    )

                if string_comp in line_comp:
                    logger.info(f'String encontrada na linha {ypos}')
                    return True

            logger.info('String não encontrada em nenhuma linha')
            return False
        except Exception as e:
            logger.error(f'Erro durante busca de string: {e}', exc_info=True)
            return False

    def get_string_positions(
        self, string: str, ignore_case=False
    ) -> list[tuple[int]]:
        logger.info(
            f"Buscando posições da string '{string}' (ignore_case={ignore_case})"
        )
        try:
            screen_content = self.get_full_screen(header=True)
            flags = 0 if not ignore_case else re.IGNORECASE
            indices_object = re.finditer(
                re.escape(string), screen_content, flags
            )
            indices = [index.start() for index in indices_object]
            logger.debug(f'Encontradas {len(indices)} ocorrências')

            positions = [
                self._get_ypos_and_xpos_from_index(index + 1)
                for index in indices
            ]
            logger.info(f'Posições encontradas: {positions}')
            return positions
        except Exception as e:
            logger.error(f'Erro ao buscar posições: {e}', exc_info=True)
            return []

    def _get_ypos_and_xpos_from_index(self, index):
        logger.debug(f'Convertendo índice {index} para coordenadas (y,x)')
        ypos = math.ceil(index / self.model_dimensions['columns'])
        remainder = index % self.model_dimensions['columns']
        if remainder == 0:
            xpos = self.model_dimensions['columns']
        else:
            xpos = remainder
        logger.debug(f'Índice {index} convertido para ({ypos},{xpos})')
        return (ypos, xpos)


class X3270(AbstractEmulator, X3270Cmd):
    def __init__(self, visible: bool = False, model: MODEL_TYPE = '2') -> None:
        logger.info(f'Inicializando X3270 (visible={visible}, model={model})')
        self.model = model
        self.model_dimensions = MODEL_DIMENSIONS[model]
        self.visible = visible
        self.app: ExecutableApp = self._create_app()
        self.is_terminated = False
        self.host = None
        self.port = None
        self.tls = None
        logger.debug('X3270 inicializado')

    def __getattr__(self, name):
        logger.debug(f'Acessando atributo dinâmico: {name}')
        # Mapeamento de comandos com parâmetros e descrições
        if name in command_map:
            logger.debug(f'Comando encontrado no command_map: {name}')
            params, description = command_map[name]

            def command_func(*args, **kwargs):
                logger.info(
                    f'Executando comando {name} com args={args}, kwargs={kwargs}'
                )
                if len(args) + len(kwargs) < len(params):
                    error_msg = (
                        f'Comando {name} espera {len(params)} parâmetro(s).'
                    )
                    logger.error(error_msg)
                    raise CommandError(error_msg)

                all_args = ', '.join(
                    list(map(str, args))
                    + [f'{k}={repr(v)}' for k, v in kwargs.items()]
                )
                logger.debug(f'Comando formatado: {name}({all_args})')

                try:
                    cmd = self._exec_command(
                        f'{name}({all_args})'.encode('utf8')
                    )
                    try:
                        text = [text.decode('utf8') for text in cmd.data[0:]]
                        result = ''.join(text)
                    except AttributeError:
                        result = [val for val in cmd.data[0:]]

                    logger.debug(
                        f'Comando executado, resultado: {result[:100]}...'
                    )
                    return result
                except Exception as e:
                    logger.error(
                        f'Erro ao executar comando {name}: {e}', exc_info=True
                    )
                    raise

            params = {p[0:1] for p in params}
            command_func.__doc__ = (
                f'{name}: {description} parâmetros esperados: {params}'
            )

            return command_func
        elif 'send_pf' in name:
            logger.debug(f'Comando PF detectado: {name}')

            def command_func(value: int | None = None):
                if not value:
                    value = int(name[-1])
                logger.info(f'Enviando tecla PF{value}')
                self._exec_command(f'PF({value})')
                self.wait(30, 'unlock')
                logger.debug(f'PF{value} enviado e tela desbloqueada')

            return command_func
        else:
            error_msg = f'Comando {name} não encontrado.'
            logger.error(error_msg)
            raise CommandError(error_msg)

    def _create_app(self) -> None:
        logger.info('Criando aplicativo emulador')
        try:
            if os.name == 'nt':  # windows
                if self.visible:
                    logger.info('Criando Wc3270App (Windows, visível)')
                    return Wc3270App(self.model)
                logger.info('Criando Ws3270App (Windows, não visível)')
                return Ws3270App(self.model)

            if self.visible:  # linux
                logger.info('Criando X3270App (Linux, visível)')
                return X3270App(self.model)
            logger.info('Criando S3270App (Linux, não visível)')
            return S3270App(self.model)
        except Exception as e:
            logger.error(f'Erro ao criar aplicativo: {e}', exc_info=True)
            raise

    def _exec_command(self, cmdstr: str) -> Command:
        logger.debug(f'Executando comando: {cmdstr}')
        if self.is_terminated:
            error_msg = 'Tentativa de executar comando em emulador terminado'
            logger.error(error_msg)
            raise TerminatedError
        max_loop = 5
        for exec in range(max_loop):
            try:
                cmd = Command(self.app, cmdstr)
                cmd.execute()
                self.status = Status(cmd.status_line)
                logger.debug(f'Comando executado, status: {self.status}')
                return cmd
            except Exception as e:
                logger.error(f'Erro ao executar comando: {e}', exc_info=True)
                logger.warning(
                    f'Nova tentativa de exec command: {exec}/{max_loop}'
                )
                sleep(exec)
                self.reset()
                self.wait(10, 'unlock')
                self.tab()
        logger.error(
            f'Erro ao executar comando total de tentativas: {max_loop}',
            exc_info=True,
        )
        raise CommandError

    def terminate(self) -> None:
        logger.info('Terminando emulador')
        if not self.is_terminated:
            try:
                logger.debug('Enviando comando quit')
                self.quit()
            except BrokenPipeError:
                logger.warning('BrokenPipeError ao enviar quit, ignorando')
                self.ignore()
            except socket.error as e:
                if e.errno != errno.ECONNRESET:
                    logger.error(
                        f'Erro de socket ao terminar: {e}', exc_info=True
                    )
                    raise ConnectionError
                logger.warning(f'Erro de conexão resetada: {e}')

        logger.debug('Fechando aplicativo')
        self.app.close()
        self.is_terminated = True
        logger.info('Emulador terminado com sucesso')

    def is_connected(self) -> bool:
        logger.debug('Verificando estado de conexão')
        try:
            self.query('ConnectionState')
            is_connected = self.status.connection_state.startswith(b'C(')
            logger.info(f'Estado de conexão: {is_connected}')
            return is_connected
        except Exception as e:
            logger.error(f'Erro ao verificar conexão: {e}', exc_info=True)
            return False

    def connect_host(self, host: str, port: str, tls: bool = True) -> None:
        logger.info(f'Conectando ao host: {host}:{port} (tls={tls})')
        self.host = host
        self.port = port
        self.tls = tls
        tls_prefix = 'L:Y:' if tls else ''
        strint_conn = f'{tls_prefix}{host}:{port}'
        logger.debug(f'String de conexão: {strint_conn}')

        try:
            if self.app:
                if not self.app.connect(strint_conn):
                    logger.debug(
                        'Método connect do app retornou False, '
                        + 'tentando método connect direto'
                    )
                    self.connect(strint_conn)
                logger.debug('Aguardando modo 3270')
                self.wait(5, '3270mode')
                logger.info('Conexão estabelecida com sucesso')
        except CommandError as e:
            logger.warning(f'CommandError durante conexão: {e}')
        except Exception as e:
            logger.error(f'Erro ao conectar: {e}', exc_info=True)
            raise

    def reconnect_host(self) -> 'X3270':
        logger.info('Tentando reconectar ao host')
        try:
            logger.debug('Executando comando reconnect')
            self.reconnect()
            logger.info('Reconexão bem-sucedida')
            return self
        except Exception as e:
            logger.warning(f'Erro durante reconexão: {e}', exc_info=True)
            logger.debug('Terminando instância atual')
            self.terminate()
        finally:
            logger.info('Criando nova instância para reconexão')
            args = self.host, self.port, self.tls
            new_instance = X3270(self.visible, self.model)
            new_instance.connect_host(*args)

            # Atualiza todos os atributos de self com os do novo objeto
            self.__dict__.update(new_instance.__dict__)

            logger.info('Atributos de self atualizados com sucesso')
            return self


if __name__ == '__main__':
    emu = X3270(True)
    emu.connect_host('177.139.188.25', 3270, False)
    pass
