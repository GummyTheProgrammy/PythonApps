# EcomReport

O EcomReport é uma aplicação desktop baseado em Python, projetado para gerar relatórios de vendas detalhados a partir de dados CSV de e-commerce. Integrante do repositório [PythonApps](https://github.com/GummyTheProgrammy/PythonApps), ele processa dados de vendas, realiza análises estatísticas e cria visualizações profissionais (gráficos de barras, linhas e rosca) com recursos de exportação para PDF. A aplicação apresenta uma arquitetura modular para escalabilidade e facilidade de manutenção.

---

### Principais características

* **Processamento de Dados Robusto**: Limpa e valida dados brutos de vendas em formato CSV, lidando com problemas como valores ausentes, tipos de dados incorretos e entradas malformadas.
* **Análise Estatística**: Calcula métricas importantes, como receita total, total de pedidos, valor médio do pedido, produtos mais vendidos, vendas por período e vendas por categoria.
* **Relatórios Visuais**: Gera visualizações, incluindo gráficos de barras (produtos mais vendidos), gráficos de linhas (receita ao longo do tempo) e gráficos de rosca (distribuição de vendas por produto e categoria), com a opção de salvar como PDF.
* **Interface Amigável**: Uma GUI baseada em Tkinter com layout dividido (30% para visualização do CSV, 70% para exibição do relatório) para interação intuitiva.

---

### Tecnologias e Bibliotecas

* **Python**: Linguagem principal da aplicação.
* **Tkinter**: Responsável pela interface gráfica do usuário para seleção de arquivos, visualização de dados e exibição de relatórios.
* **Pandas**: Responsável pela manipulação e análise de dados para processamento e agregação de dados de vendas.
* **Matplotlib**: Cria visualizações de alta qualidade (gráficos de barras, linhas e rosca).
* **Pillow**: Combina gráficos e texto em uma única imagem de relatório e suporta exportação para PDF.

---

### Instalação

1. Certifique-se de ter clonado o repositório `PythonApps`:
   ```bash
   git clone https://github.com/<your-username>/PythonApps.git
   cd PythonApps/EcomReport
   ```

2. Instale as dependências a partir do arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. Verifique se o Python 3.8 ou superior está instalado em seu sistema.

---

### Modo de uso

1. Navegue até o diretório `EcomReport`:
   ```bash
   cd PythonApps/EcomReport
   ```

2. Execute a aplicação:
   ```bash
   python app.py
   ```

3. Na interface gráfica:
    - Clique em **"1. Select CSV File"** para carregar um arquivo CSV de vendas.
    - Clique em **"2. Generate Report"** para processar os dados e exibir o relatório (gráficos e estatísticas).
    - Clique em **"3. Save as PDF"** para exportar o relatório como um arquivo PDF.

A interface exibe uma pré-visualização em CSV à esquerda (30% da largura) e o relatório gerado à direita (70% da largura).

---

### Formato do Arquivo CSV

O aplicativo espera arquivos CSV com as seguintes colunas:
- `id_pedido`: ID único do pedido (ex.: `1001`).
- `data_do_pedido`: Data do pedido no formato `AAAA-MM-DD` (ex.: `2025-01-15`).
- `valor_total`: Valor total do pedido (numérico, ex.: `150.50`).
- `id_produto`: ID do produto (ex.: `PROD001`).
- `categoria`: Categoria do produto (opcional, ex.: `Eletrônicos`).

O aplicativo processa arquivos CSV com ou sem cabeçalhos e ignora colunas irrelevantes (por exemplo, `cor`, `tamanho`, `sabor`). Exemplo de CSV (`test1.csv`):
```csv
cor,tamanho,id_produto,sabor,valor_total,categoria,data_do_pedido,id_pedido
vermelho,M,PROD001,doce,150.50,Eletrônicos,2025-01-15,1001
azul,G,PROD002,salgado,89.90,Roupas,2025-02-10,1002
```

Os arquivos CSV de exemplo (`test1.csv`, `test2.csv`, `test3.csv`) estão incluídos no diretório `EcomReport` para fins de teste.

---

### Exemplo de Saída

O relatório gerado inclui:
- **Estatísticas Resumidas**: Receita total, total de pedidos e valor médio do pedido.

- **Gráfico de Barras**: Os 5 produtos mais vendidos por vendas totais.

- **Gráfico de Linhas**: Receita ao longo do tempo (por mês).

- **Gráficos de Rosca**: Distribuição das vendas por produto e categoria (se `categoria` estiver presente no arquivo CSV).

O relatório é exibido na interface gráfica do usuário e pode ser salvo como um arquivo PDF.

---

### Estrutura do Projeto

* **`app.py`**: Arquivo principal da aplicação, orquestra o fluxo de dados e gerencia a interface gráfica Tkinter.
* **`processor.py`**: Lida com a ingestão, validação e limpeza de dados CSV.

* **`analyzer.py`**: Realiza análises estatísticas e agregação de dados.

* **`reporter.py`**: Gera visualizações e compila a imagem do relatório.

* **`test1.csv`, `test2.csv`, `test3.csv`**: Arquivos CSV de exemplo para testes.

---

### Contribuições

Contribuições para o EcomReport são bem-vindas! Você pode:
- Adicionar novos recursos (por exemplo, tipos de gráficos adicionais, filtros de dados).

- Melhorar o processamento de dados ou a interface do usuário/experiência do usuário.

- Enviar problemas ou solicitações de pull request via GitHub.

Siga as diretrizes no repositório principal do `PythonApps` (`../README.md`) para contribuir.

---

### Licença

Este projeto está licenciado. Consulte o arquivo [LICENSE](../LICENSE) no repositório principal para obter detalhes.