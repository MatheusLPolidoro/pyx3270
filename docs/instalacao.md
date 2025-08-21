## Requisitos

- Python 3.8+
- [typer](https://typer.tiangolo.com/)
- [pynput](https://pynput.readthedocs.io/en/latest/)

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

## Exemplo
- Crie um arquivo main.py com:


```python
from x3270 import x3270

emulator = x3270(visible=True)
emulator.connect_host('myhost.example.com', '992')
```
