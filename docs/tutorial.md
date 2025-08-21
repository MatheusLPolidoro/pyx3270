## Interface de linhas de comando
Detalhes de como utilizar a ferramenta CLI da biblioteca para gravar fluxo de sessões e reprodução offline.

### Gravação
<div style="position: relative; margin-top: 20px;">
  <!-- Botão de copiar -->
  <button class="copy-btn" onclick="copyText('pyx3270 record --address host:port', this)">📋 Copiar</button>

  <!-- Terminal animado -->
  <div class="termynal" data-termynal data-termynal-startDelay="400" style="min-height: 300px;">
    <span data-ty="input">pyx3270 record --address myhost.com:1234</span>
    <span data-ty data-ty-delay="800">[+] RECORD na porta <span class='aqua'>1234</span></span>
    <span data-ty data-ty-delay="825">[+] Escutando localhost, origem <span class='gold'>host</span>= <span class='lawngreen'>'myhost.com'</span> <span class='gold'>port</span>=<span class='aqua'>1234</span></span>
    <span data-ty data-ty-delay="935">[+] Conexão recebida de:</span>
    <span data-ty data-ty-delay="950">(<span class='lawngreen'>'127.0.0.1'</span>, <span class='aqua'>123456)</span></span>
  </div>
</div>

### Utilização: pyx3270 record [OPTIONS]

#### Options:
    --address TEXT              [required]
    --directory TEXT            [default: ./screens]
    --tls / --no-tls            [default: tls]
    --model TEXT                [default: 2]
    --emulator / --no-emulator  [default: emulator]
    --help                      Show this message and exit.


### Reprodução