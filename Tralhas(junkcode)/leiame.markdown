# Data Analytics Tools 

DistinctValues.py: Script interativo em pandas que lê Superstore.csv, lista colunas e mostra contagem de valores distintos da coluna escolhida. Dependências: pandas. Requer Superstore.csv (presente).

TotalSales.py: Calcula soma total de Sales e agrupa vendas por Category usando pandas. Dependências: pandas. Lê Superstore.csv (presente).

Superstore.csv: Dataset CSV (amplo) usado como entrada por DistinctValues.py e TotalSales.py. Presente.


# Image Tools

Recolor.py: Processador de lote de imagens com PIL/Numpy; quantiza cores para uma paleta, aplica efeitos (flash vertical, contraste, bloom, grão) e salva em processed/. Dependências: Pillow, numpy. Espera imagens em pasta batch (se não existir, cria e pede para colocar imagens) — ou seja, requer amostras de imagem para rodar.