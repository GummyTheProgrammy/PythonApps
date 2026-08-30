import eel
import os
import math

# Inicializa o Eel apontando para a pasta 'web'
eel.init('web')

@eel.expose
def processar_divisao(nome_arquivo, conteudo_arquivo, num_partes):
    """
    Função que processa a divisão do texto.
    Recebe o nome, o conteúdo em formato de string e a quantidade de partes.
    Retorna mensagens de status para a interface.
    """
    linhas = conteudo_arquivo.splitlines(True)
    total_linhas = len(linhas)
    
    if total_linhas == 0:
        return "O arquivo selecionado está vazio."
        
    try:
        num_partes = int(num_partes)
    except ValueError:
        return "Número de partes inválido."

    if num_partes <= 0:
        return "O número de partes deve ser maior que zero."

    # Ajuste para evitar partes excedentes
    if num_partes > total_linhas:
        num_partes = total_linhas
        
    linhas_por_parte = math.ceil(total_linhas / num_partes)
    
    # Extrai a base do nome do arquivo
    nome_base, extensao = os.path.splitext(nome_arquivo)
    
    for i in range(num_partes):
        indice_inicio = i * linhas_por_parte
        indice_fim = indice_inicio + linhas_por_parte
        fatia = linhas[indice_inicio:indice_fim]
        
        # Gera o novo arquivo no diretório de execução atual do script
        novo_nome = f"{nome_base}_parte{i+1}{extensao}"
        
        try:
            with open(novo_nome, 'w', encoding='utf-8') as f:
                f.writelines(fatia)
        except Exception as e:
            return f"Erro ao gravar o arquivo {novo_nome}: {e}"
            
        # Calcula o progresso em float (0.0 a 100.0) e atualiza a interface
        progresso_float = float(((i + 1) / num_partes) * 100.0)
        eel.atualizar_progresso(progresso_float)()
        eel.sleep(0.2)  # Pausa para permitir a animação da interface
        
    return "Processo de divisão concluído com sucesso."

if __name__ == "__main__":
    # Inicia a aplicação otimizada para Eel
    eel.start('index.html', size=(600, 500))