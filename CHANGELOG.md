Versão 0.1.23 (2026-07-23)

### :bug: CORREÇÕES

- Corrija `X3270.reconnect_host` para não deixar processos do emulador órfãos: um `return` dentro do bloco `finally` fazia o código sempre criar uma instância/processo novo, mesmo quando o `reconnect()` nativo já tinha funcionado na instância atual — e ainda engolia silenciosamente qualquer erro ao tentar encerrar a instância antiga. Agora uma instância nova só é criada quando o reconnect nativo realmente falha, e a instância antiga é sempre encerrada antes (em melhor esforço) para não vazar processos.
- Corrija `X3270.terminate` para sempre fechar o app do emulador (`self.app.close()`), mesmo quando a tentativa de encerrar com educação (`Quit`/`Ignore`) falha por completo — cenário real quando o processo já morreu por fora (ex.: usuário fechou a janela do emulador manualmente): o `quit()` falhava com `BrokenPipeError`, a tentativa de recuperação via `ignore()` falhava com o mesmo erro (pipe já quebrado) e, por não estar tratada, abortava `terminate()` antes de chegar em `self.app.close()`. Isso fazia o fechamento dos pipes do processo antigo ficar pendente até o coletor de lixo descartar o `Popen`, gerando o "Exception ignored in: <BufferedWriter>" visto ao reconectar via `pyx3270 record`.
- Corrija `get_screen_log` para aplicar a cor base do 3270 (verde/vermelho para campos editáveis, azul/branco para campos protegidos, conforme protegido × intensificado do atributo básico `c0`) quando o campo não define `SF`/`SA` `42=fX` explícito. Antes, campos sem cor estendida (comum em aplicações mais antigas) saíam sem nenhuma cor no dump, mesmo tendo cor na tela real do emulador e no export de `printtext html`.
- Corrija condição de corrida em `X3270._exec_command`: chamadas concorrentes de múltiplas threads sobre a mesma instância (ex.: `pyx3270 record` aceitando mais de uma conexão de cliente ao mesmo tempo, como acontece ao reconectar manualmente no emulador) podiam entrelaçar escrita/leitura no pipe do processo do emulador, corrompendo o protocolo de scripting e derrubando a thread com `CommandError` (resposta toda zerada). Agora o acesso ao processo do emulador é serializado por um lock por instância.
- Corrija uma paralisação (starvation) introduzida pelo lock de `_exec_command`: o polling de `pyx3270 record` (`emu.readbuffer('ebcdic')`, chamado a cada iteração do laço de repasse de bytes do proxy) disputava o mesmo lock usado por `connect_host`. Enquanto uma conexão estava em negociação, o laço de repasse ficava bloqueado esperando o lock antes de voltar para o `select`, parando de repassar os bytes de que a própria negociação precisava para terminar — o que fazia a conexão travar por dezenas de segundos até o timeout interno do emulador ("Host disconnected"), exigindo desconectar/reconectar manualmente. Agora essa leitura usa `X3270.try_read_screen_buffer_ebcdic()`, uma tentativa não bloqueante (`RLock.acquire(blocking=False)`) que simplesmente pula a iteração se o pipe do emulador estiver ocupado, em vez de travar o repasse.
- Corrija uma race condition em `X3270.reconnect_host`: entre o `terminate()` da instância antiga e a troca para a instância nova (`__dict__.update`), o objeto `emu` compartilhado fica com `is_terminated=True` por um instante. Se outra thread (ex.: `record_handler` de uma conexão nova aceita nesse meio-tempo pelo `pyx3270 record`) tentar ler o buffer de tela nesse momento, o `_exec_command` estourava `TerminatedError` e derrubava a thread. Agora `reconnect_host` segura o lock do emulador durante toda a operação de troca, e `try_read_screen_buffer_ebcdic` também trata `TerminatedError` como "pular esta iteração", igual já fazia com o pipe ocupado.
- Faça `pyx3270 record` cair automaticamente para uma porta local livre quando a porta herdada de `--address` estiver bloqueada por permissão (comum no Linux para portas < 1024, ex.: 992), sem exigir `setcap`/root. O fallback só entra em ação quando `--local-port` **não** foi informado explicitamente — se o usuário escolher a porta local manualmente e ela estiver bloqueada, o comando continua falhando com a mensagem explicativa, respeitando a escolha explícita.
- Faça `pyx3270 record` esperar a negociação 3270 real terminar (`mode_3270=True`) antes de devolver o controle ao usuário, em vez de assumir "conectado" assim que o comando de conexão é aceito. Sem isso, o terminal podia abrir com a tela em branco (a negociação via proxy até o host de origem ainda não tinha terminado), exigindo desconectar e reconectar manualmente no emulador.
- Feche explicitamente stdin/stdout/stderr do processo do emulador em `ExecutableApp.close()`, engolindo erro de pipe já quebrado. Antes, se o processo morresse por fora (ex.: usuário fechando a janela do emulador), o fechamento dos pipes ficava pendente até o coletor de lixo descartar o `Popen`, e o flush de um pipe já quebrado nesse momento aparecia como um "Exception ignored in: <BufferedWriter>" barulhento e fora do nosso controle (visto ao reconectar via `pyx3270 record` depois de fechar a janela do emulador).
- Feche o socket/thread de escuta anterior antes de abrir um novo a cada reinício do loop de `pyx3270 record`/`pyx3270 replay` (usuário digitando "S" para continuar). Antes, cada reconexão criava um novo listener na mesma porta (via `SO_REUSEPORT`) sem nunca fechar o anterior, deixando sockets e threads de aceitação órfãos acumulando indefinidamente — possível causa de comportamento inconsistente (ex.: "Not Connected") ao reconectar várias vezes. `start_server_thread` agora também devolve o socket de escuta para o chamador poder fechá-lo, e a thread de aceitação trata `OSError` (socket fechado de propósito) sem crashar.


Versão 0.1.22 (2026-07-23)

### :bug: CORREÇÕES

- Adicione suporte à distribuição Debian, usando os mesmos binários já validados para Ubuntu. Distribuições Linux não mapeadas explicitamente agora tentam usar os binários do Debian como fallback antes de falhar com `UnsupportedDistroError`.


Versão 0.1.21 (2026-07-20)

### :zap: NOVAS FUNCIONALIDADES

- Detecção automática da distribuição Linux (via `/etc/os-release`) para selecionar o binário correto de `s3270`/`x3270` (Ubuntu em `pyx3270/bin/linux/`, Nobara em `pyx3270/bin/linux/nobara/`). Distribuições não suportadas agora falham com uma mensagem clara (`UnsupportedDistroError`), listando as distros suportadas e orientando a abrir uma issue no GitHub solicitando suporte.

### :bug: CORREÇÕES

- Adicione suporte a diferentes distribuições Linux, atualmente somente ubunto e nobara.
- Adicione tratativa para envio de caracteres inválidos no método send_string.
- `send_string` agora remove caracteres de controle (ex: `\x1a`) além dos caracteres especiais já tratados, evitando falhas na interface de scripting do emulador, e registra um aviso (`warning`) no log quando isso ocorre.


Versão 0.1.20 (2026-07-13)

### :zap: NOVAS FUNCIONALIDADES

- Adicione `get_screen_log` em `X3270Cmd`, que retorna o dump completo da tela (com quebras de linha reais) convertendo cores e destaques de campo do 3270 em sequências ANSI (SGR), formato renderizado nativamente por painéis de logs como o do Grafana/Loki. Campos non-display (ex.: senha) são mascarados por padrão (`mask_hidden=True`).
- Inclua metodo para log de campos com cor e ajuste demais logs.


Versão 0.1.19 (2026-06-19)

### :bug: CORREÇÕES

- Adicione pausa de 0.1 após segundo pf1 de \_exec e após mudança de diretório de reprodução de telas em modulo offline.
- Adicione raise para casos onde KeyboardStateError permanece consecutivamente.


Versão 0.1.17 (2026-05-16)

### :bug: CORREÇÕES

- Ajuste interface de AbstractEmulatorCmd e adicione \*args e \*\*kwargs para comandos next e prev de PyX3270Manager (Offline).


Versão 0.1.16 (2026-05-16)

### :bug: CORREÇÕES

- Inclua a opção de wait\_input\_field em send\_enter para evitar bugs de time e adicione padrão wait\_unlock para aguardar host após 0.03s em todos os métodos que utilizam.


Versão 0.1.15 (2026-05-13)

### :bug: CORREÇÕES

- Troque Wait(0.03, 'seconds') por sleep(0.03) em clear_screen.


Versão 0.1.13 (2026-05-04)

### :bug: CORREÇÕES

- Corrija conta para captura de strings da tela na função _get_ypos_and_xpos_from_index.


Versão 0.1.10 (2026-03-12)

### :bug: CORREÇÕES

- Adicione variável run_raise para validação de comandos que não podem ser tratados com KeyboardStateError.


Versão 0.1.10 (2026-03-06)

# :bug: CORREÇÕES

- Ajuste log de send_string incluindo a devida f-string para apresentar o dado nos logs.

# :test_tube: TESTES

- Arrume os testes para validação de limpeza de tela e de troca de diretório em reprodução.


Versão 0.1.10 (2026-02-26)

### :classical_building: INFRAESTRUTURA

- Ajuste versão de dependencias do typer.


Versão 0.1.9 (2026-02-23)

### :bug: CORREÇÕES

- Adicione 0.03s após clear de tela, para garantir a limpeza.


Versão 0.1.8 (2026-02-06)

### :bug: CORREÇÕES

- Ajuste nivel dos logs para limpeza de tela e envio de string None para debug, para não subir warnings desnecessarios.


Versão 0.1.7 (2025-12-23)

### :bug: CORREÇÕES

- Corrija fechamento seguro em caso de KeyboardInterrupt.
- Corrija reinicialização em caso de reinicializar record.
- Corrija set para troca de telas.


Versão 0.1.4 (2025-09-18)

### :bug: CORREÇÕES

- Corrija caminho completo de WS3270.exe


Versão 0.1.3 (2025-09-18)

### :zap: NOVAS FUNCIONALIDADES

- Inclua hook para passar pasta com emulador ao gerar executável com pyinstaller.


Versão 0.1.2 (2025-09-17)

### :bug: CORREÇÕES

- Corrija gravação de tela com TLS ativa.


Versão 0.1.1 (2025-08-25)

### :bug: CORREÇÕES

- Inclua join por espaço em get_full_string para adequação com versão anterior a LIB.

### :wastebasket: OBSOLETOS

- Inclua comandos depreciados da versão antiga utilizada antes da criação da LIB.

### :open_file_folder: DOCUMENTAÇÃO

- Inclua titulos para os comandos builtins do x3270.

### :test_tube: TESTES

- Ajuste os testes para comportar alteração de join com espaço.

### :classical_building: INFRAESTRUTURA

- Altere versão limite do python para <3.14.


Versão 0.1.0 (2025-08-24)

### :zap: NOVAS FUNCIONALIDADES

- Adicione classe PyX3270Manager base para herança na criação de classes de sistemas offline.
- Adicione comandos para utilização de todos os métodos originais disponíveis no terminal.
- Adicione erros customizados herdados de Exception para cada tipo de exceção do terminal.
- Adicione funcionalidade set_screen e add para server record.
- Adicione server para gravação e reprodução de telas em modo offline.

### :bug: CORREÇÕES

- Adicione server.replay_handler leitura de teclas não é feita quando servidor de aplicações abre em modo sem emulador.
- Aumente de tempo limite para aguardo de desbloqueio padrão (time_unlock) de 30 para 60 segundos.
- Corrija captura em função get_string_area para pegar até a ultima linha passada no parametro.

### :test_tube: TESTES

- Adicione maior cobertura de testes para os módulos cli, exceptions offline.
- Adicione testes para emulador e para server.
