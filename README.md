# Emulador x3270
Uma interface comum utilizada para manipulação com terminais 3270 da IBM.


## Comandos de Entrada e Controle:

- Attn()
  - Tradução: Atenção
  - Descrição: Envia a sequência ATTN do 3270, equivalente ao comando TELNET IP. Usado para interromper certas operações no mainframe.

- BackSpace()
  - Tradução: Backspace (voltar o cursor)
  - Descrição: Move o cursor uma posição para a esquerda (sem apagar o caractere).

- BackTab()
    - Tradução: Voltar aba
    - Descrição: Move o cursor para o campo anterior no formulário.

- CircumNot()
    - Tradução: Circunflexo/Não
    - Descrição: Envia o caractere ~ em modo NVT (modo de terminal padrão) ou o caractere NOT SIGN (¬) em modo 3270.

- Clear()
    - Tradução: Limpar
    - Descrição: Envia o comando CLEAR (limpa a tela no terminal 3270).

- Copy()
    - Tradução: Copiar
    - Descrição: Copia o texto selecionado para a área de transferência (clipboard) do Windows (válido se estiver rodando em um ambiente gráfico).

- CursorSelect()
    - Tradução: Seleção do cursor
    - Descrição: Emula o clique com a caneta luminosa (light pen) no local atual do cursor (usado historicamente nos mainframes).

- Cut()
    - Tradução: Recortar
    - Descrição: Copia o texto selecionado para o clipboard e depois apaga do terminal.

- Delete()
    - Tradução: Deletar
    - Descrição: Apaga o caractere na posição atual do cursor.

- DeleteField()
    - Tradução: Apagar campo
    - Descrição: Apaga todo o conteúdo do campo em que o cursor está (Ctrl+U).

- DeleteWord()
    - Tradução: Apagar palavra
    - Descrição: Apaga a palavra antes da posição atual do cursor (Ctrl+W).

## Navegação com o Cursor:

- Down()
    - Tradução: Para baixo
    - Descrição: Move o cursor para a linha abaixo.

- Dup()
    - Tradução: Duplicar
    - Descrição: Envia a tecla DUP do terminal 3270 (X'1C'). É usada para preencher campos repetidos.

- Enter()
    - Tradução: Enter
    - Descrição: Envia o comando ENTER (envia o formulário, executa comando, etc.).

- Erase()
    - Tradução: Apagar (voltar)
    - Descrição: Apaga o caractere anterior ao cursor (backspace destrutivo).

- EraseEOF()
    - Tradução: Apagar até o fim do campo
    - Descrição: Apaga do cursor até o final do campo.

- EraseInput()
    - Tradução: Apagar entrada
    - Descrição: Apaga todos os campos de entrada da tela.

- FieldEnd()
    - Tradução: Fim do campo
    - Descrição: Move o cursor para o final do campo atual.

- FieldMark()
    - Tradução: Marcar campo
    - Descrição: Envia a tecla FIELD MARK (marca visual usada em terminais 3270, X'1E').

- Flip()
    - Tradução: Inverter
    - Descrição: Inverte a tela da direita para a esquerda (como um espelho). Usado para teste de exibição.

- HexString(<digits>)
    - Tradução: String Hexadecimal
    - Descrição: Envia uma sequência de dados codificados em hexadecimal diretamente para o campo.

- Home()
    - Tradução: Início
    - Descrição: Move o cursor para o primeiro campo da tela.

- ignore()
    - Tradução: Ignorar
    - Descrição: Não faz nada. Pode ser usado para desabilitar uma tecla.

- Insert()
    - Tradução: Inserir
    - Descrição: Ativa o modo de inserção do terminal 3270.

- Interrupt()
    - Tradução: Interromper
    - Descrição: Envia o comando TELNET IAC IP (usado no modo NVT para interrupção).

- Key(<symbol>|0x<nn>)
    - Tradução: Tecla
    - Descrição: Envia um caractere específico. Pode ser o nome do caractere ou o valor hexadecimal.

- Left() / Left2()
    - Tradução: Esquerda
    - Descrição: Move o cursor 1 ou 2 colunas para a esquerda.

- Right() / Right2()
    - Tradução: Direita
    - Descrição: Move o cursor 1 ou 2 colunas para a direita.

- MoveCursor(<row>,<col>)
    - Tradução: Mover cursor (origem 0)
    - Descrição: Move o cursor para uma linha e coluna específicas (começando do 0). Depreciado.

- MoveCursor1(<row>,<col>)
    - Tradução: Mover cursor (origem 1)
    - Descrição: Move o cursor para uma posição específica na tela, começando da posição 1.

- MoveCursor(<offset>)
    - Tradução: Mover cursor por offset
    - Descrição: Move o cursor para uma posição de offset na memória de tela (avançado).

- Newline()
    - Tradução: Nova linha
    - Descrição: Move o cursor para o primeiro campo da próxima linha.

- NextWord() / PreviousWord()
    - Tradução: Próxima palavra / Palavra anterior
    - Descrição: Move o cursor para a próxima ou anterior palavra.

## Comandos Específicos de Mainframe:

- PA(<n>)
    - Tradução: Atenção de Programa (Program Attention)
    - Descrição: Envia a tecla de atenção de programa PA1, PA2, etc. Usado por certas aplicações em mainframe.

- PF(<n>)
    - Tradução: Função Programada (Program Function)
    - Descrição: Envia uma tecla de função 3270 (PF1 a PF24). Equivale a F1–F24 em terminais 3270.

- Printer(start[,lu]|stop)
    - Tradução: Impressora (iniciar/parar)
    - Descrição: Inicia ou para uma sessão de impressão 3287 associada a uma LU (Logical Unit).

## Utilitários:

- Paste()
    - Tradução: Colar
    - Descrição: Cola o conteúdo do clipboard no terminal.

- Redraw()
    - Tradução: Redesenhar
    - Descrição: Atualiza (força a reexibição) da tela do terminal.

- Reset()
    - Tradução: Resetar
    - Descrição: Libera o teclado se estiver travado (como quando o terminal mostra "X SYSTEM").

- String(<texto>)
    - Tradução: Texto
    - Descrição: Envia uma string diretamente para o campo atual.

- SysReq()
    - Tradução: Requisição de sistema
    - Descrição: Envia a tecla System Request (SysReq), usada para alternar sessões LU ou invocar menus no host.


# Tipos de campos MAINFRAME

| **SF**        | **Hex equivalente** | **Significado** |
|--------------|----------------|----------------|
| SF(c0=e8)   | `1D E8`         | Campo protegido, editável, MDT ativo |
| SF(c0=e0)   | `1D E0`         | Campo protegido, MDT desativado |
| SF(c0=f0)   | `1D F0`         | Campo editável, MDT ativo |
| SF(c0=40)   | `1D 40`         | Intensificado (brilhante) |
| SF(c0=80)   | `1D 80`         | Campo protegido (não editável) |
| SF(c0=20)   | `1D 20`         | Sublinhado |
| SF(c0=10)   | `1D 10`         | MDT ativo (Modified Data Tag) |
| SF(c0=08)   | `1D 08`         | Campo gráfico |

Obs.: Algumas telas são construidas enviando comandos que não são capturados utilizando o readbuffer do x3270, logo elas são reproduzidas com diferenças.


# Build do modulo

```shell
python -m build --no-isolation --skip-dependency-check
```
