## Requisitos

- Python 3.8+
- [typer](https://typer.tiangolo.com/)

Crie e ative um ambiente virtual, e então instale o Pyx3270:

<div style="position: relative; margin-top: 20px;">
  <!-- Botão de copiar -->
  <button class="copy-btn" onclick="copyText('pip install pyx3270', this)">📋 Copiar</button>

  <!-- Terminal animado -->
  <div class="termynal" data-termynal data-termynal-startDelay="600" style="min-height: 300px;" data-command="pip install pyx3270">
    <span data-ty="input">pip install pyx3270</span>
    <span data-ty="progress"></span>
  </div>
</div>

## Sistemas operacionais suportados

Os emuladores da família x3270 já vêm embutidos no pacote (`pyx3270/bin/`), não é preciso instalar nada além do `pip install`:

| Sistema | `visible=False` (sem janela) | `visible=True` (com janela) |
| --- | --- | --- |
| Windows | `ws3270.exe` | `wc3270.exe` (janela de console própria) |
| Linux (Ubuntu, Debian, Nobara) | `s3270` | `x3270` (janela X11) |
| macOS 11+ (Apple Silicon e Intel) | `s3270` | `c3270` em uma janela nova do Terminal.app |

Observações para macOS:

- Os binários são universais (arm64 + x86_64) e usam o TLS nativo do sistema (Secure Transport); não dependem de Homebrew, OpenSSL nem XQuartz.
- No modo visível, o `c3270` é aberto em uma janela nova do Terminal.app e controlado pelo pyx3270 por um socket local. Ao encerrar o emulador (`terminate()`), a janela mostra `[Process completed]` ou fecha sozinha, conforme a preferência *Terminal > Ajustes > Perfis > Shell > "Quando o shell encerrar"*.
- Se o binário embutido não puder ser usado (por exemplo, macOS mais antigo que o 11), o pyx3270 procura um `s3270`/`c3270` no `PATH` — basta instalar a suíte com `brew install x3270`.

## Exemplo
- Crie um arquivo main.py com:


```python
from x3270 import x3270

emulator = x3270(visible=True)
emulator.connect_host('myhost.example.com', '992')
```
