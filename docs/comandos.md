# Comandos do X3270

## Entrada e Controle
<details>
    <summary>Abort - Aborta scripts e macros pendentes</summary>
    <p><strong>Descrição:</strong> Aborta scripts e macros pendentes.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.abort()
    ```

    <p><strong>Observações:</strong> Útil para interromper operações em execução.</p>
    <br>
</details> 

<details>
    <summary>Attn - Atenção</summary>
    <p><strong>Descrição:</strong> Envia a sequência ATTN do 3270, equivalente ao comando TELNET IP. Usado para
        interromper certas operações no mainframe.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.attn()
    ```
    <p><strong>Observações:</strong> Interrompe processos ou comandos no host.</p>
    <br>
</details> 

<details>
    <summary>Backspace - Voltar cursor uma posição</summary>
    <p><strong>Descrição:</strong> Move o cursor uma posição para a esquerda (sem apagar o caractere).</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.backspace()
    ```
    <p><strong>Observações:</strong> Cursor apenas se move, não apaga.</p>
    <br>
</details> 

<details>
    <summary>Backtab - Voltar para campo anterior</summary>
    <p><strong>Descrição:</strong> Move o cursor para o campo anterior no formulário.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.backtab()
    ```
    <p><strong>Observações:</strong> Útil para navegação em formulários.</p>
    <br>
</details> 

<details>
    <summary>Bell - Toca sino</summary>
    <p><strong>Descrição:</strong> Toca o sino do terminal para alertar o usuário.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.bell()
    ```
    <p><strong>Observações:</strong> Pode ser ignorado se terminal não suportar.</p>
    <br>
</details> 

<details>
    <summary>CircumNot - Envia ~ ou ¬</summary>
    <p><strong>Descrição:</strong> Envia o caractere ~ em modo NVT (terminal padrão) ou ¬ em modo 3270.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.circumnot()
    ```
    <p><strong>Observações:</strong> Usado em ambientes específicos de terminal.</p>
    <br>
</details> 

<details>
    <summary>Clear - Limpa tela</summary>
    <p><strong>Descrição:</strong> Envia o comando CLEAR para limpar a tela no terminal 3270.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.clear()
    ```
    <p><strong>Observações:</strong> Reseta a tela para estado inicial.</p>
    <br>
</details> 

<details>
    <summary>Close - Fecha conexão</summary>
    <p><strong>Descrição:</strong> Alias para disconnect, fecha a conexão com o host.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.close()
    ```
    <p><strong>Observações:</strong> Encerramento limpo da sessão.</p>
    <br>
</details> 

<details>
    <summary>Closescript - Encerra script em execução</summary>
    <p><strong>Descrição:</strong> Encerra o script em execução no terminal.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.closescript()
    ```
    <p><strong>Observações:</strong> Útil para abortar scripts longos ou travados.</p>
    <br>
</details> 

<details>
    <summary>Compose - Interpreta próximas teclas</summary>
    <p><strong>Descrição:</strong> Interpreta as próximas duas teclas conforme o mapa de composição.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.compose()
    ```
    <p><strong>Observações:</strong> Usado para entrada de caracteres especiais.</p>
    <br>
</details> 

<details>
    <summary>Connect - Conecta ao host</summary>
    <p><strong>Descrição:</strong> Estabelece conexão com o host mainframe.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    emulator = X3270()
    from x3270 import x3270

    emulator = x3270(visible=True)
    emulator.connect(host='mainframe.example.com')
    ```
    <p><strong>Observações:</strong> Essencial para iniciar sessões.</p>
    <br>
</details> 

<details>
    <summary>CursorSelect - Seleciona local do cursor (light pen)</summary>
    <p><strong>Descrição:</strong> Emula o clique com a caneta luminosa no local atual do cursor.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.cursorselect()
    ```
    <p><strong>Observações:</strong> Pouco usado atualmente.</p>
    <br>
</details> 

<details>
    <summary>Delete - Apaga caractere na posição do cursor</summary>
    <p><strong>Descrição:</strong> Apaga o caractere na posição atual do cursor.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.delete()
    ```
    <p><strong>Observações:</strong> Útil para edição de campos.</p>
    <br>
</details> 

<details>
    <summary>DeleteField - Apaga conteúdo do campo atual</summary>
    <p><strong>Descrição:</strong> Apaga todo o conteúdo do campo em que o cursor está.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.deletefield()
    ```
    <p><strong>Observações:</strong> Limpa campo para nova entrada.</p>
    <br>
</details> 

<details>
    <summary>DeleteWord - Apaga palavra anterior ao cursor</summary>
    <p><strong>Descrição:</strong> Apaga a palavra antes da posição atual do cursor.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.deleteword()
    ```
    <p><strong>Observações:</strong> Atalho útil para edição rápida.</p>
    <br>
</details> 

<details>
    <summary>Disconnect - Fecha conexão com host</summary>
    <p><strong>Descrição:</strong> Fecha a conexão ativa com o host mainframe.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.disconnect()
    ```
    <p><strong>Observações:</strong> Fecha sessão atual.</p>
    <br>
</details> 

<details>
    <summary>Erase - Backspace destrutivo</summary>
    <p><strong>Descrição:</strong> Apaga o caractere anterior ao cursor (backspace destrutivo).</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.erase()
    ```
    <p><strong>Observações:</strong> Apaga caractere e move cursor.</p>
    <br>
</details> 

<details>
    <summary>EraseEOF - Apaga até o fim do campo</summary>
    <p><strong>Descrição:</strong> Apaga do cursor até o final do campo.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.eraseeof()
    ```
    <p><strong>Observações:</strong> Apaga grandes blocos de texto.</p>
    <br>
</details> 

<details>
    <summary>EraseInput - Apaga todos campos de entrada</summary>
    <p><strong>Descrição:</strong> Apaga todos os campos de entrada da tela.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.eraseinput()
    ```
    <p><strong>Observações:</strong> Útil para limpar formulários inteiros.</p>
    <br>
</details> 

<details>
    <summary>Execute - Executa comando no shell</summary>
    <p><strong>Descrição:</strong> Executa um comando no shell do sistema.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.execute('dir')
    ```
    <p><strong>Observações:</strong> Apenas para comandos do sistema local.</p>
    <br>
</details> 

<details>
    <summary>Enter - Envia comando ENTER</summary>
    <p><strong>Descrição:</strong> Envia o comando ENTER para o terminal 3270.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.enter()
    ```
    <p><strong>Observações:</strong> Confirma formulário ou comando.</p>
    <br>
</details> 

<details>
    <summary>Escape - Abre prompt c3270</summary>
    <p><strong>Descrição:</strong> Abre prompt c3270 para comandos manuais.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.escape()
    ```
    <p><strong>Observações:</strong> Útil para diagnóstico.</p>
    <br>
</details> 

<details>
    <summary>FieldEnd - Move cursor ao fim do campo</summary>
    <p><strong>Descrição:</strong> Move o cursor para o final do campo atual.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.fieldend()
    ```
    <p><strong>Observações:</strong> Facilita edição rápida.</p>
    <br>
</details> 

<details>
    <summary>FieldMark - Envia tecla FIELD MARK</summary>
    <p><strong>Descrição:</strong> Envia a tecla FIELD MARK (marca visual usada em terminais 3270).</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.fieldmark()
    ```
    <p><strong>Observações:</strong> Usado para delimitar campos.</p>
    <br>
</details> 

<details>
    <summary>Flip - Inverte tela (espelho)</summary>
    <p><strong>Descrição:</strong> Inverte a tela da direita para a esquerda.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.flip()
    ```
    <p><strong>Observações:</strong> Usado para teste de exibição.</p>
    <br>
</details> 

<details>
    <summary>Help - Exibe ajuda</summary>
    <p><strong>Descrição:</strong> Exibe ajuda para um tópico.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.help('enter')
    ```
    <p><strong>Observações:</strong> Ajuda interativa.</p>
    <br>
</details> 

<details>
    <summary>HexString - Envia dados hexadecimais</summary>
    <p><strong>Descrição:</strong> Envia sequência de dados codificados em hexadecimal diretamente para o campo.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.hexstring('7F8A9B')
    ```
    <p><strong>Observações:</strong> Útil para comandos avançados.</p>
    <br>
</details> 

<details>
    <summary>Home - Move cursor para início</summary>
    <p><strong>Descrição:</strong> Move o cursor para o primeiro campo da tela.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.home()
    ```
    <p><strong>Observações:</strong> Rápido retorno ao início.</p>
    <br>
</details> 

<details>
    <summary>Ignore - Não faz nada</summary>
    <p><strong>Descrição:</strong> Não faz nada. Pode ser usado para desabilitar uma tecla.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.ignore()
    ```
    <p><strong>Observações:</strong> Útil para scripts condicionalmente desabilitarem ações.</p>
    <br>
</details> 

<details>
    <summary>Insert - Ativa modo inserção</summary>
    <p><strong>Descrição:</strong> Ativa o modo de inserção do terminal 3270.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.insert()
    ```
    <p><strong>Observações:</strong> Modo inserção insere caracteres ao invés de sobrescrever.</p>
    <br>
</details> 

<details>
    <summary>Interrupt - Envia comando TELNET IAC IP</summary>
    <p><strong>Descrição:</strong> Envia o comando TELNET IAC IP para interrupção (modo NVT).</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.interrupt()
    ```
    <p><strong>Observações:</strong> Para interrupções rápidas no host.</p>
    <br>
</details> 

<details>
    <summary>Key - Envia caractere específico</summary>
    <p><strong>Descrição:</strong> Envia um caractere específico, por nome ou valor hexadecimal.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.key('0x41')
    ```
    <p><strong>Observações:</strong> Útil para envio direto de caracteres.</p>
    <br>
</details> 

<details>
    <summary>KeyboardDisable - Modifica bloqueio automático</summary>
    <p><strong>Descrição:</strong> Modifica o bloqueio automático do teclado.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.keyboarddisable(True)
    ```
    <p><strong>Observações:</strong> Controle avançado do teclado.</p>
    <br>
</details> 

<details>
    <summary>Keymap - Ativa keymap temporário</summary>
    <p><strong>Descrição:</strong> Ativa um keymap temporário para mapeamento de teclas.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.keymap('custommap')
    ```
    <p><strong>Observações:</strong> Útil para teclas customizadas.</p>
    <br>
</details> 

<details>
    <summary>Keypad - Mostra teclado 3270</summary>
    <p><strong>Descrição:</strong> Mostra o teclado virtual 3270 na tela.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.keypad()
    ```
    <p><strong>Observações:</strong> Facilita interação via mouse.</p>
    <br>
</details> 

<details>
    <summary>Left - Move cursor 1 coluna à esquerda</summary>
    <p><strong>Descrição:</strong> Move o cursor uma coluna para a esquerda.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.left()
    ```
    <p><strong>Observações:</strong> Navegação simples.</p>
    <br>
</details> 

<details>
    <summary>Left2 - Move cursor 2 colunas à esquerda</summary>
    <p><strong>Descrição:</strong> Move o cursor duas colunas para a esquerda.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.left2()
    ```
    <p><strong>Observações:</strong> Navegação rápida.</p>
    <br>
</details> 

<details>
    <summary>Macro - Executa macro definido</summary>
    <p><strong>Descrição:</strong> Executa um macro previamente definido.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.macro('login_sequence')
    ```
    <p><strong>Observações:</strong> Automatiza sequências de comandos.</p>
    <br>
</details> 

<details>
    <summary>Menu - Exibe menu de comandos</summary>
    <p><strong>Descrição:</strong> Exibe o menu de comandos do terminal.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.menu()
    ```
    <p><strong>Observações:</strong> Navegação via menu.</p>
    <br>
</details> 

<details>
    <summary>Movecursor - Move cursor linha e coluna (origem 0)</summary>
    <p><strong>Descrição:</strong> Move o cursor para linha e coluna específicas (origem 0).</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.movecursor(5, 10)
    ```
    <p><strong>Observações:</strong> Útil para posicionamento preciso.</p>
    <br>
</details> 

<details>
    <summary>Movecursor1 - Move cursor linha e coluna (origem 1)</summary>
    <p><strong>Descrição:</strong> Move o cursor para linha e coluna específicas (origem 1).</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.movecursor1(1, 1)
    ```
    <p><strong>Observações:</strong> Base 1, diferente do padrão Python.</p>
    <br>
</details> 

<details>
    <summary>Movecursoroffset - Move cursor por offset</summary>
    <p><strong>Descrição:</strong> Move o cursor para uma posição de offset na memória da tela.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.movecursoroffset(100)
    ```
    <p><strong>Observações:</strong> Uso avançado para controle interno.</p>
    <br>
</details> 

<details>
    <summary>Newline - Move cursor para próxima linha</summary>
    <p><strong>Descrição:</strong> Move o cursor para o primeiro campo da próxima linha.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.newline()
    ```
    <p><strong>Observações:</strong> Facilita inserção em múltiplas linhas.</p>
    <br>
</details> 

<details>
    <summary>Nextword - Move cursor para próxima palavra</summary>
    <p><strong>Descrição:</strong> Move o cursor para a próxima palavra.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.nextword()
    ```
    <p><strong>Observações:</strong> Navegação rápida.</p>
    <br>
</details> 

<details>
    <summary>Previousword - Move cursor para palavra anterior</summary>
    <p><strong>Descrição:</strong> Move o cursor para a palavra anterior.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.previousword()
    ```
    <p><strong>Observações:</strong> Navegação rápida.</p>
    <br>
</details> 

<details>
    <summary>Pause - Espera 350ms</summary>
    <p><strong>Descrição:</strong> Aguarda por 350 milissegundos.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.pause()
    ```
    <p><strong>Observações:</strong> Usado para esperar respostas lentas do host.</p>
    <br>
</details> 

<details>
    <summary>Prompt - Abre prompt externo</summary>
    <p><strong>Descrição:</strong> Abre prompt externo com nome da aplicação.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.prompt('diagnostic')
    ```
    <p><strong>Observações:</strong> Diagnóstico avançado.</p>
    <br>
</details> 

<details>
    <summary>Quit - Sai do terminal</summary>
    <p><strong>Descrição:</strong> Sai do terminal 3270.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.quit()
    ```
    <p><strong>Observações:</strong> Finaliza a sessão.</p>
    <br>
</details> 

<details>
    <summary>Set - Altera ou exibe configurações</summary>
    <p><strong>Descrição:</strong> Altera ou exibe configurações do terminal.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.set()
    ```
    <p><strong>Observações:</strong> Configurações avançadas.</p>
    <br>
</details> 

<details>
    <summary>Show - Exibe status e configurações</summary>
    <p><strong>Descrição:</strong> Exibe status e configurações do terminal.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.show()
    ```
    <p><strong>Observações:</strong> Útil para diagnóstico.</p>
    <br>
</details> 

<details>
    <summary>String - Envia texto</summary>
    <p><strong>Descrição:</strong> Envia uma string diretamente para o campo atual.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.string('Olá mundo')
    ```
    <p><strong>Observações:</strong> Entrada direta de texto.</p>
    <br>
</details> 

<details>
    <summary>Temporarycomposemap - Define mapa de composição temporário</summary>
    <p><strong>Descrição:</strong> Define um mapa temporário de composição para teclas.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.temporarycomposemap('custommap')
    ```
    <p><strong>Observações:</strong> Mapeamento temporário para caracteres.</p>
    <br>
</details> 

<details>
    <summary>Temporarykeymap - Alias para Keymap</summary>
    <p><strong>Descrição:</strong> Alias para ativar keymap temporário.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.temporarykeymap('custommap')
    ```
    <p><strong>Observações:</strong> Uso temporário de keymaps.</p>
    <br>
</details> 

<details>
    <summary>Toggle - Alterna configuração</summary>
    <p><strong>Descrição:</strong> Alterna uma configuração específica para ligado/desligado.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.toggle('insert_mode', 'off')
    ```
    <p><strong>Observações:</strong> Ativa ou desativa opções.</p>
    <br>
</details> 

<details>
    <summary>Toggleinsert - Ativa/desativa modo inserção</summary>
    <p><strong>Descrição:</strong> Alterna o modo inserção ligado/desligado.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.toggleinsert()
    ```
    <p><strong>Observações:</strong> Ativa modo inserção alternado.</p>
    <br>
</details> 

<details>
    <summary>Togglereverse - Ativa/desativa modo reverso</summary>
    <p><strong>Descrição:</strong> Alterna o modo reverso de entrada.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.togglereverse()
    ```
    <p><strong>Observações:</strong> Alterna modo reverso.</p>
    <br>
</details> 

<details>
    <summary>Transfer - Transferência de arquivos IND$FILE</summary>
    <p><strong>Descrição:</strong> Transferência de arquivos via IND$FILE entre host e cliente.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.transfer('receive file.txt')
    ```
    <p><strong>Observações:</strong> Requer configuração no host.</p>
    <br>
</details> 

<details>
    <summary>Up - Move cursor para cima</summary>
    <p><strong>Descrição:</strong> Move o cursor para a linha acima.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.up()
    ```
    <p><strong>Observações:</strong> Navegação vertical.</p>
    <br>
</details> 

<details>
    <summary>Wait - Aguarda eventos do host</summary>
    <p><strong>Descrição:</strong> Aguarda por eventos do host, com parâmetros flexíveis.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)

    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    # Espera até a sessão estar em modo 3270
    emulator.wait('3270mode')

    # Espera até um campo de entrada estar disponível
    emulator.wait('inputfield')

    # Espera até mudar para modo NVT (TELNET puro)
    emulator.wait('nvtmode')

    # Espera até não haver mais dados pendentes de saída
    emulator.wait('output')

    # Espera até o teclado desbloquear
    emulator.wait('unlock')

    # Espera por 3 segundos
    emulator.wait('seconds', 3)

    # Aguarda até ser desconectado
    emulator.wait('disconnect')

    # Aguarda o cursor estar na linha 5, coluna 10
    emulator.wait('cursorat', row=5, col=10)

    # Aguarda a string "READY" aparecer na linha 1, coluna 1
    emulator.wait('stringat', row=1, col=1, string='READY')

    # Aguarda até existir um campo de entrada na linha 6, coluna 20
    emulator.wait('inputfieldat', row=6, col=20)
    ```
    <p><strong>Observações:</strong> Pode aguardar eventos ou tempo.</p>
<table>
  <thead>
    <tr>
      <th>Parâmetro</th>
      <th>Descrição</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>inputfield</code></td>
      <td>Aguarda até um campo de entrada estar disponível.</td>
    </tr>
    <tr>
      <td><code>nvtmode</code></td>
      <td>Aguarda até entrar em modo NVT (modo TELNET puro).</td>
    </tr>
    <tr>
      <td><code>3270mode</code></td>
      <td>Aguarda até entrar em modo 3270 (sessão estabelecida).</td>
    </tr>
    <tr>
      <td><code>output</code></td>
      <td>Aguarda até não haver mais dados pendentes de saída.</td>
    </tr>
    <tr>
      <td><code>seconds</code></td>
      <td>Aguarda um número de segundos.</td>
    </tr>
    <tr>
      <td><code>disconnect</code></td>
      <td>Aguarda até a sessão ser desconectada.</td>
    </tr>
    <tr>
      <td><code>unlock</code></td>
      <td>Aguarda o teclado ficar desbloqueado.</td>
    </tr>
    <tr>
      <td><code>cursorat</code></td>
      <td>Aguarda o cursor estar em uma posição específica.</td>
    </tr>
    <tr>
      <td><code>stringat</code></td>
      <td>Aguarda uma string aparecer em uma posição específica.</td>
    </tr>
    <tr>
      <td><code>inputfieldat</code></td>
      <td>Aguarda um campo de entrada em uma posição específica.</td>
    </tr>
  </tbody>
</table>

</details>

## Navegação com o Cursor

<details>
    <summary>Down - Move cursor para baixo</summary>
    <p><strong>Descrição:</strong> Move o cursor para a linha de baixo.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.down()
    ```
    <p><strong>Observações:</strong> Navegação vertical simples.</p>
    <br>
</details> 

<details>
    <summary>Left - Move cursor para esquerda</summary>
    <p><strong>Descrição:</strong> Move o cursor uma coluna para a esquerda.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.left()
    ```
    <p><strong>Observações:</strong> Navegação horizontal.</p>
    <br>
</details> 

<details>
    <summary>Left2 - Move cursor 2 colunas para esquerda</summary>
    <p><strong>Descrição:</strong> Move o cursor duas colunas para a esquerda.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.left2()
    ```
    <p><strong>Observações:</strong> Movimento mais rápido para a esquerda.</p>
    <br>
</details> 

<details>
    <summary>Right - Move cursor para direita</summary>
    <p><strong>Descrição:</strong> Move o cursor uma coluna para a direita.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.right()
    ```
    <p><strong>Observações:</strong> Navegação horizontal.</p>
    <br>
</details> 

<details>
    <summary>Right2 - Move cursor 2 colunas para direita</summary>
    <p><strong>Descrição:</strong> Move o cursor duas colunas para a direita.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.right2()
    ```
    <p><strong>Observações:</strong> Movimento mais rápido para a direita.</p>
    <br>
</details> 

<details>
    <summary>Up - Move cursor para cima</summary>
    <p><strong>Descrição:</strong> Move o cursor para a linha de cima.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.up()
    ```
    <p><strong>Observações:</strong> Navegação vertical simples.</p>
    <br>
</details> 

<details>
    <summary>Tab - Move cursor para próximo campo</summary>
    <p><strong>Descrição:</strong> Move o cursor para o próximo campo de entrada.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.tab()
    ```
    <p><strong>Observações:</strong> Navegação entre campos.</p>
    <br>
</details> 

<details>
    <summary>Newline - Move cursor para próximo campo da linha seguinte</summary>
    <p><strong>Descrição:</strong> Move o cursor para o primeiro campo da próxima linha.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.newline()
    ```
    <p><strong>Observações:</strong> Navegação vertical e horizontal combinada.</p>
    <br>
</details> 

<details>
    <summary>Nextword - Move cursor para próxima palavra</summary>
    <p><strong>Descrição:</strong> Move o cursor para a próxima palavra.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.nextword()
    ```
    <p><strong>Observações:</strong> Navegação rápida em texto.</p>
    <br>
</details> 

<details>
    <summary>Previousword - Move cursor para palavra anterior</summary>
    <p><strong>Descrição:</strong> Move o cursor para a palavra anterior.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.previousword()
    ```
    <p><strong>Observações:</strong> Navegação rápida em texto.</p>
</details>

## Comandos Específicos de Mainframe

<details>
    <summary>PA - Atenção de Programa</summary>
    <p><strong>Descrição:</strong> Envia a tecla de atenção de programa PA1, PA2, etc.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.PA(2) # envia PA2
    ```
    <p><strong>Observações:</strong> Usado por aplicações específicas mainframe.</p>
    <br>
</details> 

<details>
    <summary>PF - Função Programada</summary>
    <p><strong>Descrição:</strong> Envia tecla de função PF1 a PF24, equivalente às teclas F1-F24.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.pf(12) # envia PF12
    ```
    <p><strong>Observações:</strong> Comandos padrão em terminais 3270.</p>
    <br>
</details> 

<details>
    <summary>Printer - Impressora 3287 iniciar/parar</summary>
    <p><strong>Descrição:</strong> Inicia ou para uma sessão de impressão associada a uma LU (Logical Unit).</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.printer(stop=True)
    ```
    <p><strong>Observações:</strong> Requer configuração de LU no host.</p>
    <br>
</details> 

<details>
    <summary>SysReq - Requisição de sistema</summary>
    <p><strong>Descrição:</strong> Envia a tecla System Request (SysReq), usada para alternar sessões LU ou invocar
        menus no host.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.sysreq()
    ```
    <p><strong>Observações:</strong> Comando especial mainframe.</p>
</details>

## Utilitários

<details>
    <summary>Paste - Colar</summary>
    <p><strong>Descrição:</strong> Cola o conteúdo do clipboard no terminal.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.paste()
    ```
    <p><strong>Observações:</strong> Requer permissão de acesso ao clipboard.</p>
    <br>
</details> 

<details>
    <summary>Redraw - Redesenhar</summary>
    <p><strong>Descrição:</strong> Atualiza (força a reexibição) da tela do terminal.</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.redraw()
    ```
    <p><strong>Observações:</strong> Útil quando a tela está corrompida.</p>
    <br>
</details> 

<details>
    <summary>Reset - Resetar teclado travado</summary>
    <p><strong>Descrição:</strong> Libera o teclado se estiver travado (como na mensagem "X SYSTEM").</p>
    <p><strong>Exemplo:</strong></p>
    ```python
    from x3270 import x3270

    emulator = x3270(visible=True)
    # Conecta ao host mainframe na porta 992 (TLS)
    emulator.connect_host('myhost.example.com', '992')

    emulator.reset()
    ```
    <p><strong>Observações:</strong> Resolve travamentos temporários.</p>
</details>

# Tipos de campos MAINFRAME

| **SF**    | **Hex equivalente** | **Significado**                      |
| --------- | ------------------- | ------------------------------------ |
| SF(c0=e8) | `1D E8`             | Campo protegido, editável, MDT ativo |
| SF(c0=e0) | `1D E0`             | Campo protegido, MDT desativado      |
| SF(c0=f0) | `1D F0`             | Campo editável, MDT ativo            |
| SF(c0=40) | `1D 40`             | Intensificado (brilhante)            |
| SF(c0=80) | `1D 80`             | Campo protegido (não editável)       |
| SF(c0=20) | `1D 20`             | Sublinhado                           |
| SF(c0=10) | `1D 10`             | MDT ativo (Modified Data Tag)        |
| SF(c0=08) | `1D 08`             | Campo gráfico                        |

Obs.: Algumas telas são construidas enviando comandos que não são capturados utilizando o readbuffer do x3270, logo elas são reproduzidas com diferenças.