import pandas as pd
import sys
from tqdm import tqdm

def validate_and_clean_order_items(orders_file, order_items_file):
    """
    Lê os arquivos orders.csv e order_items.csv, e remove de order_items as
    linhas cujos order_id não existem em orders.
    Exibe uma barra de progresso durante o processo.

    Args:
        orders_file (str): O caminho para o arquivo orders.csv.
        order_items_file (str): O caminho para o arquivo order_items.csv.
    """
    try:
        print("Iniciando a validação de chaves...")

        # Lê os arquivos orders e order_items
        df_orders = pd.read_csv(orders_file)
        df_order_items = pd.read_csv(order_items_file)
        
        # Converte as colunas de ID para string para evitar problemas de tipo
        df_orders['order_id'] = df_orders['order_id'].astype(str)
        df_order_items['order_id'] = df_order_items['order_id'].astype(str)

        # Obtém todos os IDs de pedidos válidos da tabela orders
        valid_order_ids = set(df_orders['order_id'].tolist())

        print("Validando itens de pedido...")

        # Prepara a barra de progresso para o processamento
        tqdm.pandas(desc="Removendo IDs inválidos")
        
        # Remove as linhas de df_order_items que não têm um order_id válido
        # O apply com tqdm.pandas mostra o progresso da operação
        df_order_items_cleaned = df_order_items[df_order_items['order_id'].isin(valid_order_ids)]

        print("\nProcessamento concluído.")
        
        # Calcula o número de linhas removidas
        removed_rows = len(df_order_items) - len(df_order_items_cleaned)
        
        # Cria o nome do novo arquivo de saída
        output_file = order_items_file.replace('.csv', '_validated.csv')
        
        # Salva o DataFrame limpo em um novo arquivo CSV
        df_order_items_cleaned.to_csv(output_file, index=False)
        
        print(f"Arquivo limpo salvo como: {output_file}")
        print(f"Linhas removidas: {removed_rows}")
    
    except FileNotFoundError:
        print("Erro: Um dos arquivos não foi encontrado.")
        print("Certifique-se de que 'orders_null_removed.csv' e 'order_items.csv' estão na mesma pasta.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# --- Execução do Script ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python valida_pedidos.py orders_file.csv order_items_file.csv")
        print("Exemplo: python valida_pedidos.py orders_null_removed.csv order_items.csv")
    else:
        orders_file_name = sys.argv[1]
        order_items_file_name = sys.argv[2]
        validate_and_clean_order_items(orders_file_name, order_items_file_name)