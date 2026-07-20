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
