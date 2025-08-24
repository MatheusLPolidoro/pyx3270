import functools
from typing import Any


def x3270_builtins_class(cls):
    """Decorador de classe que aplica x3270_builtins a todos os métodos."""
    for name, attr in cls.__dict__.items():
        if callable(attr) and not name.startswith('__'):
            # aplica o wrapper
            setattr(cls, name, _wrap_method(attr))
    return cls


def _wrap_method(method):
    """Wrapper que imprime o nome do método e delega para _target."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        return x3270_command(self, method.__name__, *args, **kwargs)

    return wrapper


def x3270_command(em, func, *args, **kwargs):
    all_args = ', '.join(
        list(map(str, args)) + [f'{k}={repr(v)}' for k, v in kwargs.items()]
    )

    if 'send_pf' in func or func == 'pf':
        em._exec_command(f'PF({all_args})'.encode('utf8'))
        em.wait(em.time_unlock, 'unlock')

    try:
        cmd = em._exec_command(f'{func}({all_args})'.encode('utf8'))
        try:
            text = [text.decode('utf8') for text in cmd.data[0:]]
            result = ''.join(text)
        except AttributeError:
            result = [val for val in cmd.data[0:]]

        return result
    except Exception:
        raise


@x3270_builtins_class
class X3270Commands:
    def abort(self) -> Any: ...  # Aborta scripts e macros pendentes.
    def ansitext(self) -> Any: ...  # Exibe texto NVT pendente.
    def ascii(self, *args: Any) -> Any: ...  # Conteúdo da tela em ASCII.
    def ascii1(
        self, row: int, col: int
    ) -> Any: ...  # Bytes da tela em ASCII da posição (1-origem).
    def asciifield(self) -> Any: ...  # Conteúdo do campo atual em ASCII.
    def attn(self) -> Any: ...  # Envia a sequência ATTN do 3270.
    def backspace(
        self,
    ) -> Any: ...  # Move o cursor uma posição para a esquerda.
    def backtab(self) -> Any: ...  # Move o cursor para o campo anterior.
    def bell(self) -> Any: ...  # Toca o sino do terminal.
    def circumnot(self) -> Any: ...  # Envia ~ em NVT ou ¬ em 3270.
    def clear(self) -> Any: ...  # Limpa a tela do terminal 3270.
    def close(self) -> Any: ...  # Alias para Disconnect, fecha a conexão.
    def closescript(self) -> Any: ...  # Encerra o script em execução.
    def compose(
        self,
    ) -> Any: ...  # Interpreta as próximas duas teclas conforme o mapa.
    def connect(self, host: str) -> Any: ...  # Conecta ao host.
    def cursorselect(
        self,
    ) -> Any: ...  # Seleciona local do cursor como caneta luminosa.
    def delete(self) -> Any: ...  # Apaga caractere na posição do cursor.
    def deletefield(self) -> Any: ...  # Apaga o conteúdo do campo atual.
    def deleteword(self) -> Any: ...  # Apaga a palavra anterior ao cursor.
    def disconnect(self) -> Any: ...  # Fecha conexão com o host.
    def down(self) -> Any: ...  # Move o cursor para a linha de baixo.
    def dup(self) -> Any: ...  # Envia tecla DUP do 3270.
    def ebcdic(self) -> Any: ...  # Conteúdo da tela em EBCDIC.
    def ebcdicfield(self) -> Any: ...  # Conteúdo do campo atual em EBCDIC.
    def enter(self) -> Any: ...  # Envia o comando ENTER.
    def erase(self) -> Any: ...  # Backspace destrutivo.
    def eraseeof(self) -> Any: ...  # Apaga até o fim do campo.
    def eraseinput(self) -> Any: ...  # Apaga todos os campos de entrada.
    def escape(self) -> Any: ...  # Abre prompt c3270>
    def execute(self, command: str) -> Any: ...  # Executa comando no shell.
    def exit(self) -> Any: ...  # Sai do c3270.
    def expect(self, pattern: str) -> Any: ...  # Aguarda saída NVT.
    def fieldend(self) -> Any: ...  # Move cursor ao fim do campo.
    def fieldmark(self) -> Any: ...  # Envia tecla FIELD MARK.
    def flip(self) -> Any: ...  # Inverte a tela (espelho).
    def help(self, action: str) -> Any: ...  # Exibe ajuda para um tópico.
    def hexstring(self, digits: str) -> Any: ...  # Envia dados em hexadecimal.
    def home(self) -> Any: ...  # Move o cursor para o primeiro campo.
    def ignore(self) -> Any: ...  # Não faz nada.
    def info(
        self, text: str
    ) -> Any: ...  # Exibe texto na barra de status (OIA).
    def insert(self) -> Any: ...  # Ativa modo de inserção 3270.
    def interrupt(self) -> Any: ...  # Envia comando TELNET IAC IP.
    def key(self, symbol: str) -> Any: ...  # Envia um caractere específico.
    def keyboarddisable(
        self, mode: str
    ) -> Any: ...  # Modifica o bloqueio automático.
    def keymap(self, keymap_name: str) -> Any: ...  # Ativa keymap temporário.
    def keypad(self) -> Any: ...  # Mostra o teclado 3270 na tela.
    def left(self) -> Any: ...  # Move o cursor 1 coluna à esquerda.
    def left2(self) -> Any: ...  # Move o cursor 2 colunas à esquerda.
    def macro(self, name: str) -> Any: ...  # Executa um macro definido.
    def menu(self) -> Any: ...  # Exibe o menu de comandos.
    def movecursor(
        self, row: int, col: int
    ) -> Any: ...  # Move cursor para linha e coluna (origem 0).
    def movecursor1(
        self, row: int, col: int
    ) -> Any: ...  # Move cursor para linha e coluna (origem 1).
    def movecursoroffset(
        self, offset: int
    ) -> Any: ...  # Move cursor para offset na memória.
    def newline(
        self,
    ) -> Any: ...  # Move cursor para primeiro campo da linha seguinte.
    def nextword(self) -> Any: ...  # Move cursor para a próxima palavra.
    def previousword(self) -> Any: ...  # Move cursor para a palavra anterior.
    def open(self) -> Any: ...  # Alias para Connect.
    def pa(self, n: int) -> Any: ...  # Envia tecla PA1, PA2, etc.
    def pf(self, n: int) -> Any: ...  # Envia tecla PF1 a PF24.
    def pause(self) -> Any: ...  # Espera 350ms.
    def paste(self) -> Any: ...  # Cola conteúdo do clipboard.
    def printer(
        self, start: bool, lu: str, stop: bool
    ) -> Any: ...  # Inicia ou para sessão de impressão 3287.
    def printtext(
        self, file: str
    ) -> Any: ...  # Salva ou imprime imagem da tela.
    def prompt(self, app_name: str) -> Any: ...  # Abre prompt externo.
    def query(
        self, keyword: str
    ) -> Any: ...  # Consulta parâmetros operacionais.
    def quit(self) -> Any: ...  # Sai do terminal 3270.
    def readbuffer(self, mode: str) -> Any: ...  # Despeja o buffer de tela.
    def reconnect(self) -> Any: ...  # Reconecta ao host anterior.
    def redraw(self) -> Any: ...  # Reexibe a tela do terminal.
    def reset(self) -> Any: ...  # Desbloqueia o teclado.
    def right(self) -> Any: ...  # Move cursor 1 coluna à direita.
    def right2(self) -> Any: ...  # Move cursor 2 colunas à direita.
    def screentrace(
        self, mode: str, file: str
    ) -> Any: ...  # Salva imagens da tela em arquivo.
    def script(self, path: str) -> Any: ...  # Executa script filho.
    def scroll(self, direction: str) -> Any: ...  # Rola a tela.
    def set(self) -> Any: ...  # Altera ou exibe configurações.
    def show(self, item: str) -> Any: ...  # Exibe status e configurações.
    def snap(self, *args: str) -> Any: ...  # Manipula snapshots da tela.
    def source(self, file: str) -> Any: ...  # Executa comandos de um arquivo.
    def string(self, text: str) -> Any: ...  # Envia string para o campo atual.
    def sysreq(self) -> Any: ...  # Envia tecla System Request (SysReq).
    def tab(self) -> Any: ...  # Move cursor para próximo campo.
    def temporarycomposemap(
        self, map: str
    ) -> Any: ...  # Define mapa de composição temporário.
    def temporarykeymap(
        self, keymap_name: str
    ) -> Any: ...  # Alias para Keymap.
    def toggle(
        self, name: str, value: str
    ) -> Any: ...  # Alterna configuração específica.
    def toggleinsert(self) -> Any: ...  # Ativa/desativa modo inserção.
    def togglereverse(
        self,
    ) -> Any: ...  # Ativa/desativa modo reverso de entrada.
    def trace(self, mode: str) -> Any: ...  # Configura rastreamento.
    def transfer(selfs: str) -> Any: ...  # Transferência de arquivos IND$FILE.
    def up(self) -> Any: ...  # Move o cursor para cima.
    def wait(self, *args: Any) -> Any: ...  # Aguarda eventos do host.
