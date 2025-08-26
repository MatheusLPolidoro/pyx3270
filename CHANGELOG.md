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
