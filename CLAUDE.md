# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é

`pyx3270` é uma biblioteca Python para automação de terminais mainframe IBM 3270. Ela não implementa o protocolo TN3270 do zero para automação — em vez disso, controla como subprocesso os emuladores nativos da família x3270 (`s3270`, `x3270`, `ws3270`, `wc3270`, binários pré-compilados embutidos em `pyx3270/bin/`) via sua interface de scripting, e expõe uma API Python de alto nível sobre isso. Também inclui uma ferramenta CLI separada de gravação/reprodução (record/replay) de sessões TN3270 para testes offline.

**Palavras-chave**: mainframe, terminal 3270, TN3270, emulador s3270/x3270/ws3270/wc3270, scripting interface, automação de tela, record/replay, offline manager, PyX3270Manager, X3270 (classe principal), status line, keyboard locked, PF keys, structured fields, Typer CLI (`pyx3270 record` / `pyx3270 replay`), PyInstaller hook, taskipy, ruff, towncrier.

## Comandos de desenvolvimento

Gerenciados via `taskipy` (`[tool.taskipy.tasks]` em `pyproject.toml`), mas podem ser rodados diretamente:

- Rodar todos os testes com cobertura: `python -m pytest . -s -x --cov=pyx3270 -vv` (task `test`)
- Rodar um teste único: `pytest tests/test_emulator.py::test_nome -vv`
- Gerar relatório HTML de cobertura (após rodar testes): `python -m coverage html` (task `post_test`)
- Lint com correção automática: `ruff check . --fix` (task `fix`)
- Formatar: `ruff format .` (task `format`)

Config do ruff: `line-length = 79`, aspas simples, preview mode, regras `I, F, E, W, PL, PT`. `pyx3270/x3270_commands.py` está isento de `PLR0904` (muitos métodos públicos, esperado pelo padrão dinâmico de comandos).

Changelog gerenciado com `towncrier`: fragmentos em `chanlogs.d/`, categorias mapeando para os prefixos usados nas mensagens de commit deste repo (`[FIX]`, `[INFRA]`, `[TEST]`, `[FEATURE]`, etc. — ver `[[tool.towncrier.type]]` em `pyproject.toml`).

## Arquitetura

### Camada de execução do emulador (`emulator.py`, `iemulator.py`, `x3270_commands.py`)

- `iemulator.py` define os contratos abstratos: `AbstractExecutableApp` (processo do emulador), `AbstractCommand` (um comando de script), `AbstractEmulatorCmd`/`AbstractEmulator` (API de alto nível).
- `ExecutableApp` (em `emulator.py`) faz `subprocess.Popen` do binário certo conforme SO/visibilidade:
  - Windows + visível → `Wc3270App` (fala com o processo via **socket TCP** em porta livre, `-scriptport`)
  - Windows + invisível → `Ws3270App` (fala via **stdin/stdout pipes**)
  - Linux + visível → `X3270App` / Linux + invisível → `S3270App` (ambos via pipes)
- `Command` encapsula o protocolo texto do scripting interface do x3270: escreve `"Comando(args)\n"`, lê linhas `data: ...` até uma linha de status (12 campos, parseada por `Status`), seguida de `ok`/mensagem de erro. Erros com "keyboard locked"/"canceled" viram `KeyboardStateError`; outros viram `CommandError`.
- `X3270Cmd` usa `__getattr__` para despachar **qualquer** nome de método como um comando nativo do x3270 (`self.algumcomando(...)` → `"AlgumComando(args)"` enviado ao emulador). `x3270_commands.py::x3270_command` é o ponto central desse despacho, com regras especiais para `send_pf`/`pf` (aguarda unlock) e alias descontinuado `send_string_not_log` → `send_string(password=True)`.
- `X3270` (classe pública principal, exportada em `pyx3270/__init__.py`) junta `AbstractEmulator` + `X3270Cmd`, gerencia ciclo de vida (`connect_host`, `reconnect_host`, `terminate`, `is_connected` — considera desconectado após 600s de inatividade) e helpers de tela (`get_string`, `get_full_screen`, `search_string`, `get_string_positions`, limites de linha/coluna por modelo de terminal em `MODEL_DIMENSIONS`).
- Em modo Windows visível (`Wc3270App`), reconectar (`reconnect_host`) recria a instância `X3270` inteira e faz `self.__dict__.update(...)`, pois o processo/porta antigos não são reaproveitáveis.

### Camada de record/replay (`server.py`, `cli.py`, `tn3270.py`, `state.py`)

- `tn3270.py` só tem constantes de baixo nível do protocolo Telnet/TN3270 (IAC, AIDs, structured fields) — usado exclusivamente por esta camada, não pela automação via `X3270`.
- `server.py::record_handler` atua como proxy entre um cliente (emulador local) e o host mainframe real, salvando cada tela TN3270 recebida como `NNN.bin` em um diretório (gravação de sessão).
- `server.py::replay_handler` é um servidor TN3270 falso que serve telas gravadas (`.bin`) na ordem, navegável via PF3/PF7 (anterior), PF4/PF8/Enter (próxima) e CLEAR; comandos administrativos (`next`, `prev`, `set <tela>`, `change directory <dir>`, `add`, `q`) chegam por um processo separado (`multiprocessing.Process` + `Queue`, ver `state.py` e `start_command_process`) que lê stdin.
- `cli.py` expõe isso como comandos Typer `pyx3270 record` e `pyx3270 replay` (entry point `pyx3270 = "pyx3270.__main__:app"`).

### Modo offline determinístico (`offline.py`)

- `PyX3270Manager` combina as duas camadas acima: sobe `pyx3270 replay --no-tls --no-emulator` como subprocess e dirige a navegação (`next`, `prev`, `set_screen`, `change_directory`) escrevendo comandos no stdin desse subprocesso **e** enviando PF1 duas vezes via uma instância real de `X3270` conectada a ele, para manter o emulador sincronizado com a tela servida. Usado para testes de automação sem depender de um mainframe real.

### Exceções (`exceptions.py`)

Hierarquia plana e específica de domínio: `CommandError`, `TerminatedError`, `KeyboardStateError`, `FieldTruncateError`, `NotConnectedException`, `BrokenPipeError` (redefinida localmente, não é a do builtin). São usadas para diferenciar timeouts/travamentos de teclado de falhas reais de comando.

## Testes

Testes em `tests/` usam mocks pesados de `subprocess.Popen` e `socket.socket` (ver fixtures em `tests/conftest.py`: `mock_subprocess_popen`, `mock_socket`, `mock_executable_app_instance`, `x3270_emulator_instance`, `x3270_real_exec_instance`) — nenhum teste sobe um emulador real ou binário de `pyx3270/bin/`. Ao adicionar testes para `emulator.py`, prefira reaproveitar essas fixtures em vez de mockar subprocess/socket do zero.

## Convenção de logging

Todos os módulos com `logger` (`emulator.py`, `server.py`, `offline.py`; config em `logging_config.py`, arquivos `x3270_emulator.log`/`x3270_server.log`/`x3270_offline.log`) devem usar **string composta (lazy `%`-formatting)** nas chamadas de log, nunca f-string:

```python
logger.debug('Comando executado: %s', cmdstr)   # correto
logger.debug(f'Comando executado: {cmdstr}')    # evitar
```

Motivo: com f-string a interpolação ocorre sempre, mesmo se o nível do log estiver desabilitado; com `%s` lazy, o `logging` só formata a mensagem se o handler for de fato emitir o registro.

**Exceção aceita**: quando a mesma string formatada também compõe uma exceção levantada em seguida (`error_msg = f'...'; logger.error(error_msg); raise Erro(error_msg)`), mantém-se o f-string — o custo de formatação já é pago pela exceção, então a troca não traria ganho e duplicaria a construção da mensagem.

**Regra adicional aplicada nesta revisão**: blocos `except Exception: logger.error('mensagem estática'); raise` que hoje descartam a exceção passam a capturá-la (`except Exception as e`) e incluir `%s` com o detalhe — a mensagem geralmente diz o quê falhou mas não o porquê.

Guardrail de lint: `ruff` inclui a categoria `G` (`flake8-logging-format`), que reprova f-string em chamadas de log (`G004`), para evitar regressão futura.

**Status**: revisão completa aplicada em 2026-07-08 nas ~201 chamadas de log existentes (`emulator.py`, `server.py`, `offline.py`), incluindo a atualização das 4 asserções de teste que checavam a chamada exata do logger mockado (`tests/test_server.py::test_load_screens_logs_error_and_returns_empty`, `tests/test_server.py::test_handle_add_invalid_format`, `tests/test_offline.py::test_pyx3270_manager_exec`, `tests/test_offline.py::test_pyx3270_manager_exec_inactive_process`) — suíte completa (175 testes) validada em verde após a mudança.

## Empacotamento

- Binários nativos (`pyx3270/bin/**`) e o hook do PyInstaller (`pyx3270/hook/hook-pyx3270.py`) são incluídos via `package-data` e registrados como plugin `pyinstaller40` (`hook-dirs = "pyx3270.hook:get_hook_dirs"`) — necessário para que aplicações empacotadas com PyInstaller que usam `pyx3270` consigam localizar os binários (`get_binary_path` em `emulator.py` trata o caso `sys._MEIPASS`).
- Suporta Python `>=3.8,<=3.14`.
