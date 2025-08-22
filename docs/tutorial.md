## Interface de linhas de comando
Aqui você irá aprender sobre a ferramenta CLI <span class='aqua'>'*Comand Line Interface*'</span> para gravar fluxo de sessões e realizar reprodução offline.

## ⏺ Gravação
<div style="position: relative; margin-top: 20px;">
  <!-- Botão de copiar -->
  <button class="copy-btn" onclick="copyText('pyx3270 record --address host:port', this)">📋 Copiar</button>

  <!-- Terminal animado -->
  <div class="termynal" data-termynal data-termynal-startDelay="400" style="min-height: 300px;">
    <span data-ty="input">pyx3270 record --address host.com:1234</span>
    <span data-ty data-ty-delay="800">[+] RECORD na porta <span class='aqua'>1234</span></span>
    <span data-ty data-ty-delay="810">[+] Conectando ao emulador<span class='gold'>...</span></span>
    <span data-ty data-ty-delay="825">[+] Escutando localhost, origem <span class='gold'>host</span>= <span class='lawngreen'>'host.com'</span> <span class='gold'>port</span>=<span class='aqua'>1234</span></span>
    <span data-ty data-ty-delay="935">[+] Cliente conectado: (<span class='lawngreen'>'127.0.0.1'</span>, <span class='aqua'>123456)</span>
  </div>
</div>

### <span class="gold">Opções</span>
    --address TEXT              [obrigatório]
    --directory TEXT            [padrão: ./screens]
    --tls / --no-tls            [padrão: tls]
    --model TEXT                [padrão: 2]
    --emulator / --no-emulator  [padrão: emulator]
    --help                      Demonstra essa mensagem e saí.
<details>
  <summary>Endereço (<span class='aqua'>'address'</span>) <span class='deeppink'>[OBRIGAÓRIO]</span></summary>
  <p><strong>Descrição:</strong> IP/Hostname e porta do sistema mainframe.</p>
  ```shell
  pyx3270 record --address 177.139.188.25:3270 --no-tls
  ```
  <p>
    <blockquote>
    <strong>Nota:</strong> Este é o endereço para o mainframe do curso de mainframe/cobol da 
    <a href="https://futureschoolead.com.br/" target="_blank" rel="noopener">
      Futureschool
    </a>
    </blockquote>
  </p>
</details> 

<details>
  <summary>Diretório (<span class='aqua'>'directory'</span>) <span class='gold'>[PADRÃO: ./screens]</span></summary>
  <p><strong>Descrição:</strong> Caminho onde as telas serão salvas como <span class='deeppink'>'.bin'</span></p>
  ```shell
  pyx3270 record --address host:port --directory './exemplo de caminho'
  ```
</details>

<details>
  <summary>TLS (<span class='aqua'>'Transport Layer Security'</span>) <span class='gold'>[PADRÃO: tls]</span></summary>
  <p><strong>Descrição:</strong> Protocolo de segurança que criptografa os dados na comunicação. Caso não tenha TLS use: `--no-tls`</p>
  ```shell
  pyx3270 record --address host:port --no-tls
  ```
</details>

<details>
  <summary>Modelo (<span class='aqua'>'model'</span>) <span class='gold'>[PADRÃO: 2]</span></summary>
  <p><strong>Descrição:</strong>O X3270 suporta diferentes modelos de terminal, cada um com dimensões específicas de linhas e colunas. Abaixo estão os modelos disponíveis:</p>
  <table>
    <thead>
      <tr>
        <th>Modelo</th>
        <th>Linhas</th>
        <th>Colunas</th>
        <th>Descrição</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>2</td>
        <td>24</td>
        <td>80</td>
        <td>Modelo clássico 24x80, usado em terminais básicos.</td>
      </tr>
      <tr>
        <td>3</td>
        <td>32</td>
        <td>80</td>
        <td>Modelo de 32 linhas com 80 colunas, oferece mais espaço vertical.</td>
      </tr>
      <tr>
        <td>4</td>
        <td>43</td>
        <td>80</td>
        <td>Modelo de 43 linhas com 80 colunas, adequado para telas mais longas.</td>
      </tr>
      <tr>
        <td>5</td>
        <td>27</td>
        <td>132</td>
        <td>Modelo estendido com 27 linhas e 132 colunas, ideal para telas largas.</td>
      </tr>
    </tbody>
  </table>
  <blockquote>
    <strong>Nota:</strong> A escolha do modelo influencia o layout das telas 
    TN3270 exibidas pelo emulador.
  </blockquote>
</details>

<details>
  <summary>Emulador (<span class='aqua'>'emulator'</span>) <span class='gold'>[PADRÃO: emulator]</span></summary>
  <p><strong>Descrição:</strong> Abre o emulador x3270 ou wc3270 de acordo com o sistema operacional, caso apenas queira abrir o servidor e usar outro emulador use: `--no-emulator`</p>
  ```shell
  pyx3270 record --address host:port --no-emulator
  ```
</details>


## ⏭ Reprodução
<div style="position: relative; margin-top: 20px;">
  <!-- Botão de copiar -->
  <button class="copy-btn" onclick="copyText('pyx3270 replay', this)">📋 Copiar</button>

  <!-- Terminal animado -->
  <div class="termynal" data-termynal data-termynal-startDelay="400" style="min-height: 300px;">
    <span data-ty="input">pyx3270 replay</span>
    <span data-ty data-ty-delay="800">[+] REPLAY do caminho: <span class='deeppink'>./screens</span></span>
    <span data-ty data-ty-delay="825">[+] Servidor de replay escutando na porta <span class='aqua'>992</span></span>
    <span data-ty data-ty-delay="935">[+] Conexão recebida de: (<span class='lawngreen'>'127.0.0.1'</span>, <span class='aqua'>123456)</span>
    <span data-ty data-ty-delay="955">[?] Digite um comando:</span>
  </div>
</div>

### <span class="gold">Opções</span>
    --directory TEXT            [padrão: ./screens]
    --port INTEGER              [padrão: 992]
    --tls / --no-tls            [padrão: tls]
    --model TEXT                [padrão: 2]
    --emulator / --no-emulator  [padrão: emulator]
    --help                      Demonstra essa mensagem e saí.

<details>
  <summary>Diretório (<span class='aqua'>'directory'</span>) <span class='gold'>[PADRÃO: ./screens]</span></summary>
  <p><strong>Descrição:</strong> Caminho onde as telas gravadas serão lidas para reprodução.</p>
  ```shell
  pyx3270 replay --directory './screens'
  ```
</details> 

 <details>
  <summary>Porta (<span class='aqua'>'port'</span>) <span class='gold'>[PADRÃO: 992]</span></summary>
  <p><strong>Descrição:</strong> Porta TCP onde o servidor de replay irá escutar conexões.</p>
  ```shell
  pyx3270 replay --port 12345
  ```
</details>

<details>
  <summary>TLS (<span class='aqua'>'Transport Layer Security'</span>) <span class='gold'>[PADRÃO: tls]</span></summary>
  <p><strong>Descrição:</strong> Protocolo de segurança que criptografa os dados na comunicação. Caso não tenha TLS
      use: `--no-tls`</p> 
      
  ```shell
  pyx3270 replay --no-tls
  ```
</details>

<details>
  <summary>Modelo (<span class='aqua'>'model'</span>) <span class='gold'>[PADRÃO: 2]</span></summary>
  <p><strong>Descrição:</strong>O X3270 suporta diferentes modelos de terminal, cada um com dimensões específicas de
      linhas e colunas.</p>
  <table>
      <thead>
          <tr>
              <th>Modelo</th>
              <th>Linhas</th>
              <th>Colunas</th>
              <th>Descrição</th>
          </tr>
      </thead>
      <tbody>
          <tr>
              <td>2</td>
              <td>24</td>
              <td>80</td>
              <td>Modelo clássico 24x80, usado em terminais básicos.</td>
          </tr>
          <tr>
              <td>3</td>
              <td>32</td>
              <td>80</td>
              <td>Modelo de 32 linhas com 80 colunas, oferece mais espaço vertical.</td>
          </tr>
          <tr>
              <td>4</td>
              <td>43</td>
              <td>80</td>
              <td>Modelo de 43 linhas com 80 colunas, adequado para telas mais longas.</td>
          </tr>
          <tr>
              <td>5</td>
              <td>27</td>
              <td>132</td>
              <td>Modelo estendido com 27 linhas e 132 colunas, ideal para telas largas.</td>
          </tr>
      </tbody>
  </table>
  <blockquote> <strong>Nota:</strong> A escolha do modelo influencia o layout das telas TN3270 exibidas pelo emulador.
  </blockquote>
</details>

<details>
  <summary>Emulador (<span class='aqua'>'emulator'</span>) <span class='gold'>[PADRÃO: emulator]</span></summary>
  <p><strong>Descrição:</strong> Abre o emulador x3270 ou wc3270 de acordo com o sistema operacional. Caso apenas
      queira abrir o servidor use: `--no-emulator`</p>
  ```shell
  pyx3270 replay --no-emulator
  ```
</details>