class BrokenPipeError(Exception):
    """o PIPE/cano de envio do TerminalClient não esta funcionando."""


class CommandError(Exception):
    """Falha na execução do comando TerminalClient."""


class TerminatedError(Exception):
    """Instância TerminalClient foi encerrada."""


class KeyboardStateError(Exception):
    """Posição do cursor no TerminalClient esta bloqueada."""


class FieldTruncateError(Exception):
    """Envio de texto fora do limite do TerminalClient."""


class NotConnectedException(Exception):
    """Não foi possivel conectar com o TerminalClient."""
