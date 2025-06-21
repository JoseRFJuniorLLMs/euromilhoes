import pandas as pd


def analisar_frequencias_euromilhoes(caminho_ficheiro):
    """
    Analisa um ficheiro CSV com o histórico de resultados do Euromilhões.
    Calcula e imprime a frequência dos números principais e das estrelas.
    """
    try:
        # Tenta ler o ficheiro CSV fornecido pelo utilizador
        df = pd.read_csv(caminho_ficheiro)
        print(f"Dataset '{caminho_ficheiro}' carregado com sucesso com {len(df)} registos.\n")

        # --- INFORMAÇÕES ADICIONAIS PARA AJUDAR NA DEPURAÇÃO ---
        # Estas linhas são úteis para verificar os nomes das colunas e o formato dos dados.
        # Por favor, veja a saída destas linhas para nos dizer os nomes corretos das suas colunas.
        print("--- Nomes das Colunas no seu CSV (para verificar se B1, B2, etc. estão corretos) ---")
        print(df.columns.tolist()) # .tolist() para uma melhor visualização em lista
        print("-" * 50)

        print("\n--- Primeiras 5 linhas do seu CSV (para inspecionar o formato dos dados) ---")
        print(df.head())
        print("-" * 50)
        # --- FIM DAS INFORMAÇÕES ADICIONAIS ---

        # ATENÇÃO: As listas 'colunas_bolas' e 'colunas_estrelas' DEVEM CORRESPONDER
        # aos nomes EXATOS das colunas no seu ficheiro CSV.
        # As colunas foram atualizadas com base no output que você forneceu.
        colunas_bolas = ['Number 1', 'Number 2', 'Number 3', 'Number 4', 'Number 5']
        colunas_estrelas = ['Star 1', 'Star 2']

        # --- Análise dos Números Principais ---
        # Concatena todas as colunas de bolas numa única Série pandas para contagem
        frequencia_bolas = pd.concat([df[col] for col in colunas_bolas]).value_counts()

        print("\n--- Frequência dos Números Principais (1-50) ---")
        print(frequencia_bolas)
        print("-" * 50)

        # --- Análise das Estrelas ---
        # Concatena as colunas de estrelas numa única Série pandas para contagem
        frequencia_estrelas = pd.concat([df[col] for col in colunas_estrelas]).value_counts()

        print("\n--- Frequência das Estrelas (1-12) ---")
        print(frequencia_estrelas)
        print("-" * 50)

        print("\nLembrete: Esta análise descreve o passado e não tem poder preditivo sobre sorteios futuros.")

    except KeyError as e:
        print(f"Erro: Uma das colunas esperadas não foi encontrada: {e}.")
        print(f"As colunas existentes no seu DataFrame são: {df.columns.tolist()}")
        print("Por favor, certifique-se de que as listas 'colunas_bolas' e 'colunas_estrelas' no script correspondem aos nomes exatos das colunas no seu CSV.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# --- Executar a Análise ---
# Substitua pelo caminho exato do seu ficheiro Euromilhões
# Lembre-se que o caminho deve estar correto para o seu sistema.
# Se o ficheiro estiver no mesmo diretório do script, pode usar apenas o nome do ficheiro.
# Se usar barras invertidas (\) no Windows, adicione um 'r' antes da string (raw string) ou use barras normais (/).
caminho_do_seu_ficheiro = r'D:\dev\SIGEC-VE\julio_euromilhoes\euromilhoes_historico.csv'
analisar_frequencias_euromilhoes(caminho_do_seu_ficheiro)
