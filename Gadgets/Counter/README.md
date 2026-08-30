# Widget de contador simples

Não há muito a dizer, apenas um contador mesmo, você pode somar 1, diminuir 1, copiar o valor atual e fechar o aplicativo.
Recursos: se você clicar em qualquer outro lugar além dos botões, poderá arrastá-lo livremente. Se você abrir outra janela ela permanecerá no topo, muito útil para acompanhar entre as abas.

---

### Como usar

Para executar o script, você precisa ter o **Python** e as bibliotecas **`pandas`** e **`tqdm`** instaladas. Se você ainda não os possui, instale-os através do terminal:

Para executar o script, você precisa ter o **Python** e a biblioteca **`PySide6`** instaladas. Se você ainda não os possui, instale-os através do terminal:

```bash
pip instalar PySide6

````

Em seguida, execute o script no terminal:

```bash
contador python.py

```

**Nota**: Certifique-se de ter uma imagem chamada **`circle.png`** no mesmo diretório do script. Se a imagem não for encontrada, o programa irá gerar automaticamente um fundo circular azul temporário para você.

-----

### Como funciona

O script `Counter.py` cria um widget de desktop personalizado e sem moldura usando a estrutura **PySide6**:

1. **`PySide6 (Qt)`**: A biblioteca principal usada para criar a interface gráfica do usuário (GUI). Ele cuida da transparência da janela, das formas personalizadas (máscaras) e da renderização do contador digital.
2. **Mascaramento de janela personalizado**: O script usa `QBitmap` e `setMask` para criar uma janela perfeitamente circular, mesmo que a janela subjacente seja tecnicamente um quadrado.
3. **Camada de interação transparente**: Implementa áreas clicáveis ​​invisíveis (`QLabel`) posicionadas estrategicamente sobre a imagem de fundo para funcionar como botões sem confusão visual.

O fluxo de trabalho do script é o seguinte:

1. **Inicialização**: O widget está definido como "Sempre visível" e "Sem moldura". Ele carrega o fundo `circle.png` e o dimensiona para 200x200 pixels.
2. **Manipulação de eventos**: Como a janela não tem moldura, uma lógica personalizada `mouseMoveEvent` e `mousePressEvent` é implementada para permitir que você arraste o gadget para qualquer lugar da tela.
3. **Lógica de Contador**: Mantém um estado inteiro interno. Clicar nas áreas "Mais" ou "Menos" atualiza esse estado, que é então formatado como uma sequência de 4 dígitos (por exemplo, `0001`) e exibido usando uma fonte de estilo digital.
4. **Integração com a área de transferência**: A área "Copiar" usa `QApplication.clipboard()` para enviar instantaneamente o valor atual do contador para a área de transferência do seu sistema para uso em outros aplicativos.

---

### Benefícios

* **Design minimalista**: uma interface de usuário limpa e circular que fica no topo de outras janelas sem a quantidade de barras de título ou bordas padrão.
* **Interação personalizável**: ajuste facilmente as posições, tamanhos e níveis de transparência dos botões diretamente no código para corresponder a qualquer imagem de fundo.
* **Baixo uso de recursos**: Construído em Qt, garantindo desempenho suave e tempos de resposta rápidos para incrementos de contador e arrastamento.
* **Pronto para uso**: Inclui um mecanismo substituto que gera seus próprios ativos se a imagem de fundo estiver faltando.

---

### Contribuições

Contribuições são bem-vindas! Você pode:

* Adicione novos recursos (como efeitos sonoros ao clicar ou confirmação visual quando o conteúdo é copiado).
* Melhore a UI/UX ou adicione suporte para vários temas.
* Envie problemas ou receba solicitações via GitHub.

Siga as orientações do repositório principal para contribuir.

---

### Licença

Este projeto está licenciado. Consulte o arquivo [LICENSE] no repositório principal para obter detalhes.

---