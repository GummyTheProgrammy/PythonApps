# Robô de Gravação e Reprodução de Mouse com Python

Este documento explica como funcionam os scripts `GhostMouse_Recorder.py` e `GhostMouse_Player.py`, ferramentas projetadas para automatizar tarefas repetitivas capturando movimentos e cliques do mouse e reproduzindo-os em um loop contínuo.

---

### Como Usar

Para executar os scripts, você precisa ter o **Python** e as bibliotecas **`pynput`** e **`pyautogui`** instaladas. Instale-as via terminal:

```bash
pip install pynput pyautogui

```

**Passo 1: Gravação**
Execute o script de gravação para capturar seus movimentos:

```bash
python GhostMouse_Recorder.py

```

Siga as instruções no console: digite 's' para começar, realize as ações e pressione **ENTER** para finalizar e salvar o arquivo `mouse_events.json`.

**Passo 2: Reprodução**
Execute o script de reprodução para repetir as ações gravadas:

```bash
python GhostMouse_Player.py

```

Você terá 5 segundos para alternar para a janela desejada antes do início da execução.

---

### Como Funciona

O sistema é dividido em dois módulos que utilizam bibliotecas específicas para interagir com o hardware:

1. **`pynput`**: Utilizada no `GhostMouse_Recorder.py` para monitorar o mouse em tempo real. Ela permite que o script escute eventos de movimento e clique sem bloquear a execução do programa principal.
2. **`pyautogui`**: Utilizada no `GhostMouse_Player.py` para controlar o cursor do mouse e simular os cliques físicos com base nas coordenadas e tempos extraídos do arquivo JSON.

O fluxo de trabalho é o seguinte:

1. **Captura de Eventos**: O script de gravação registra a ação (mover, pressionar ou soltar), as coordenadas `(x, y)` e, o mais importante, o **delay** (tempo decorrido entre um evento e outro) para garantir que a reprodução seja natural.
2. **Armazenamento**: Os dados são estruturados em um dicionário Python e exportados para um arquivo `mouse_events.json`. Isso permite que você grave uma vez e reproduza quantas vezes quiser, mesmo em dias diferentes.
3. **Reprodução Precisa**: O script de reprodução lê o JSON e utiliza o `time.sleep()` para respeitar os intervalos originais, garantindo que a velocidade da automação seja idêntica à gravação original.
4. **Segurança (Fail-Safe)**: O script de reprodução possui uma trava de segurança. Se você perder o controle, basta mover o mouse bruscamente para o **canto superior esquerdo (0,0)** da tela para interromper a execução imediatamente.

---

### Benefícios

* **Automação de Loop**: Diferente de macros simples, este robô executa em um loop infinito até que seja interrompido manualmente.
* **Fidelidade**: Captura o tempo exato entre os movimentos, permitindo interagir com interfaces que possuem tempos de carregamento específicos.
* **Segurança Integrada**: O recurso *Fail-Safe* do PyAutoGUI evita que o computador fique "preso" em uma automação caso algo saia do esperado.

---

### Contribuições

Contribuições para este projeto são bem-vindas! Você pode:

* Adicionar suporte para gravação de teclas do teclado.
* Implementar uma interface gráfica (GUI) para gerenciar as gravações.
* Criar uma função para ajustar a velocidade de reprodução (ex: 2x mais rápido).

Siga as diretrizes no repositório principal para enviar suas melhorias via Pull Request.

---

### Licença

Este projeto está licenciado. Consulte o arquivo [LICENSE](https://www.google.com/search?q=../LICENSE) no repositório principal para obter detalhes.

```

---

Deseja que eu adicione a função de gravar o teclado também, Master?

```