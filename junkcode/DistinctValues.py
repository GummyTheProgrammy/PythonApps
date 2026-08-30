import pandas as pd

try:
    # Tenta ler o arquivo com a codificação padrão 'utf-8'
    df = pd.read_csv('Superstore.csv')
    
except UnicodeDecodeError:
    # Se falhar, tenta novamente com uma codificação mais comum para arquivos CSV como 'latin-1'
    df = pd.read_csv('Superstore.csv', encoding='latin-1')

except FileNotFoundError:
    # Se o arquivo não for encontrado, exibe uma mensagem de erro útil
    print("Erro: O arquivo 'Superstore.csv' não foi encontrado. Por favor, verifique se ele está no mesmo diretório do seu script.")
    exit() # Interrompe a execução do programa

# Exibe as colunas disponíveis para escolha
print("Colunas disponíveis:")
for i, coluna in enumerate(df.columns):
    print(f"{i+1}. {coluna}")

try:
    # Pede ao usuário para escolher uma coluna
    escolha = int(input("\nDigite o número da coluna que você quer analisar: "))
    
    # Verifica se a escolha é válida
    if 1 <= escolha <= len(df.columns):
        nome_coluna = df.columns[escolha - 1]
        
        # Conta os valores distintos na coluna escolhida
        contagem_valores = df[nome_coluna].value_counts()
        
        # Mostra o total de campos distintos
        print(f"\nA coluna '{nome_coluna}' tem {len(contagem_valores)} campos distintos.")
        
        # Mostra a quantidade e o valor de cada campo distinto
        print("\nContagem de cada valor distinto:")
        print(contagem_valores)
        
    else:
        print("Erro: O número da coluna é inválido.")
        
except ValueError:
    print("Erro: Por favor, digite um número válido.")