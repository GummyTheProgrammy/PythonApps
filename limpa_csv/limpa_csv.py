import pandas as pd
import sys
from tqdm import tqdm

def remove_nulls_with_progress(input_file):
    """
    Lê um arquivo CSV, remove todas as linhas com valores nulos e salva o resultado.
    Exibe uma barra de progresso durante a leitura do arquivo.

    Args:
        input_file (str): O caminho do arquivo CSV de entrada.
    """
    try:
        print("Iniciando a limpeza do seu CSV...")
        
        # Lê o arquivo em pedaços (chunks) para processar arquivos grandes
        # A barra de progresso será exibida durante a leitura
        chunk_size = 1000
        total_rows = sum(1 for line in open(input_file)) - 1 # Conta o total de linhas, ignorando o cabeçalho
        
        chunks = []
        with tqdm(total=total_rows, desc="Lendo CSV") as pbar:
            for chunk in pd.read_csv(input_file, chunksize=chunk_size):
                chunks.append(chunk)
                pbar.update(len(chunk))
        
        # Concatena os pedaços em um único DataFrame
        df = pd.concat(chunks, ignore_index=True)
        
        # Armazena o número original de linhas
        original_rows = len(df)
        
        # Remove todas as linhas com valores nulos
        print("\nProcessando dados...")
        df_cleaned = df.dropna()
        
        # Calcula o número de linhas removidas
        removed_rows = original_rows - len(df_cleaned)
        
        # Cria o nome do novo arquivo de saída
        output_file = input_file.replace('.csv', '_null_removed.csv')
        
        # Salva o DataFrame limpo em um novo arquivo CSV
        df_cleaned.to_csv(output_file, index=False)
        
        print(f"\nConcluído!")
        print(f"Arquivo limpo salvo como: {output_file}")
        print(f"Linhas removidas: {removed_rows}")
        
    except FileNotFoundError:
        print(f"Erro: O arquivo '{input_file}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# --- Execução do Script ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python nome_do_script.py nome_do_arquivo.csv")
    else:
        nome_do_arquivo = sys.argv[1]
        remove_nulls_with_progress(nome_do_arquivo)