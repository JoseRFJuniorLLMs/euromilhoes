import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime, timedelta
import re


class EuromilhoesScraper:
    def __init__(self):
        self.base_url = "https://www.euro-millions.com"
        self.results_url = f"{self.base_url}/results"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def obter_resultados_recentes(self, num_sorteios=50):
        """
        Obtém os resultados mais recentes do EuroMilhões
        """
        resultados = []

        try:
            print(f"A obter {num_sorteios} resultados recentes...")

            # Primeira página
            response = self.session.get(self.results_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Procurar por resultados na página
            resultados_encontrados = self._extrair_resultados_pagina(soup)
            resultados.extend(resultados_encontrados)

            # Se precisarmos de mais resultados, navegar pelas páginas seguintes
            pagina = 1
            while len(resultados) < num_sorteios and pagina < 10:  # Limite de segurança
                pagina += 1
                url_pagina = f"{self.results_url}?page={pagina}"

                print(f"A obter página {pagina}...")
                response = self.session.get(url_pagina)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    novos_resultados = self._extrair_resultados_pagina(soup)

                    if not novos_resultados:  # Se não há mais resultados, parar
                        break

                    resultados.extend(novos_resultados)
                    time.sleep(1)  # Pausa respeitosa entre requests
                else:
                    break

            # Limitar ao número solicitado
            resultados = resultados[:num_sorteios]

            print(f"✅ {len(resultados)} resultados obtidos com sucesso!")
            return resultados

        except Exception as e:
            print(f"❌ Erro ao obter resultados: {str(e)}")
            return []

    def _extrair_resultados_pagina(self, soup):
        """
        Extrai resultados de uma página específica
        """
        resultados = []

        # Tentar diferentes seletores CSS dependendo da estrutura do site
        possivel_containers = [
            '.result',
            '.draw-result',
            '.euromillions-result',
            '[class*="result"]',
            '.table tbody tr'
        ]

        for selector in possivel_containers:
            elementos = soup.select(selector)
            if elementos:
                for elemento in elementos:
                    resultado = self._extrair_resultado_elemento(elemento)
                    if resultado:
                        resultados.append(resultado)
                break

        return resultados

    def _extrair_resultado_elemento(self, elemento):
        """
        Extrai dados de um elemento de resultado específico
        """
        try:
            # Procurar pela data
            data_elem = elemento.find(class_=re.compile(r'date|data'))
            if not data_elem:
                data_elem = elemento.find('td')  # Primeira célula pode ser a data

            # Procurar pelos números
            numeros_elem = elemento.find_all(class_=re.compile(r'ball|number|num'))
            if not numeros_elem:
                # Tentar encontrar números em spans ou divs
                numeros_elem = elemento.find_all('span', string=re.compile(r'^\d+$'))

            # Procurar pelas estrelas
            estrelas_elem = elemento.find_all(class_=re.compile(r'star|estrela'))

            if len(numeros_elem) >= 5 and len(estrelas_elem) >= 2:
                # Extrair números
                numeros = [int(elem.get_text().strip()) for elem in numeros_elem[:5]]
                estrelas = [int(elem.get_text().strip()) for elem in estrelas_elem[:2]]

                # Extrair data
                data_texto = data_elem.get_text().strip() if data_elem else datetime.now().strftime('%Y-%m-%d')
                data = self._parsear_data(data_texto)

                return {
                    'Date': data,
                    'Number 1': numeros[0],
                    'Number 2': numeros[1],
                    'Number 3': numeros[2],
                    'Number 4': numeros[3],
                    'Number 5': numeros[4],
                    'Star 1': estrelas[0],
                    'Star 2': estrelas[1]
                }

        except Exception as e:
            print(f"⚠️ Erro ao extrair resultado: {str(e)}")
            return None

    def _parsear_data(self, data_texto):
        """
        Converte texto de data para formato padrão
        """
        formatos_data = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d %B %Y',
            '%d %b %Y'
        ]

        for formato in formatos_data:
            try:
                return datetime.strptime(data_texto, formato).strftime('%Y-%m-%d')
            except ValueError:
                continue

        # Se não conseguir parsear, usar data atual
        return datetime.now().strftime('%Y-%m-%d')

    def obter_resultados_api_alternativa(self, num_sorteios=50):
        """
        Método alternativo usando API pública (se disponível)
        """
        try:
            # Exemplo de API alternativa (pode não estar sempre disponível)
            api_url = "https://api.euro-millions.com/draws"

            response = self.session.get(f"{api_url}?limit={num_sorteios}")

            if response.status_code == 200:
                data = response.json()
                resultados = []

                for draw in data.get('draws', []):
                    resultado = {
                        'Date': draw.get('date'),
                        'Number 1': draw['numbers'][0],
                        'Number 2': draw['numbers'][1],
                        'Number 3': draw['numbers'][2],
                        'Number 4': draw['numbers'][3],
                        'Number 5': draw['numbers'][4],
                        'Star 1': draw['stars'][0],
                        'Star 2': draw['stars'][1]
                    }
                    resultados.append(resultado)

                return resultados

        except Exception as e:
            print(f"❌ API alternativa falhou: {str(e)}")
            return []

    def salvar_csv(self, resultados, nome_ficheiro="euromilhoes_recentes.csv"):
        """
        Salva os resultados num ficheiro CSV
        """
        if not resultados:
            print("❌ Nenhum resultado para salvar!")
            return False

        try:
            df = pd.DataFrame(resultados)
            df.to_csv(nome_ficheiro, index=False)
            print(f"✅ Resultados salvos em '{nome_ficheiro}'!")
            return True

        except Exception as e:
            print(f"❌ Erro ao salvar CSV: {str(e)}")
            return False

    def atualizar_dataset_existente(self, ficheiro_existente, novo_ficheiro="euromilhoes_atualizado.csv"):
        """
        Atualiza um dataset existente com novos resultados
        """
        try:
            # Carregar dataset existente
            df_existente = pd.read_csv(ficheiro_existente)
            df_existente['Date'] = pd.to_datetime(df_existente['Date'])

            # Obter última data no dataset
            ultima_data = df_existente['Date'].max()
            print(f"Última data no dataset: {ultima_data.strftime('%Y-%m-%d')}")

            # Obter novos resultados
            novos_resultados = self.obter_resultados_recentes(100)  # Obter mais para garantir

            if novos_resultados:
                df_novos = pd.DataFrame(novos_resultados)
                df_novos['Date'] = pd.to_datetime(df_novos['Date'])

                # Filtrar apenas resultados mais recentes que a última data
                df_novos = df_novos[df_novos['Date'] > ultima_data]

                if not df_novos.empty:
                    # Combinar datasets
                    df_completo = pd.concat([df_existente, df_novos], ignore_index=True)
                    df_completo = df_completo.sort_values('Date', ascending=False)
                    df_completo = df_completo.drop_duplicates(subset=['Date'], keep='first')

                    # Salvar dataset atualizado
                    df_completo.to_csv(novo_ficheiro, index=False)
                    print(f"✅ Dataset atualizado com {len(df_novos)} novos resultados!")
                    return True
                else:
                    print("ℹ️ Nenhum resultado novo encontrado.")
                    return False

        except Exception as e:
            print(f"❌ Erro ao atualizar dataset: {str(e)}")
            return False


def main():
    """
    Função principal para demonstrar o uso do scraper
    """
    print("🎰 EuroMilhões Scraper - Atualização Automática de Dados")
    print("=" * 60)

    scraper = EuromilhoesScraper()

    # Opções do utilizador
    print("\nOpções disponíveis:")
    print("1. Obter resultados recentes (novo ficheiro)")
    print("2. Atualizar dataset existente")
    print("3. Testar API alternativa")

    opcao = input("\nEscolha uma opção (1-3): ").strip()

    if opcao == "1":
        num_sorteios = int(input("Quantos sorteios obter? (padrão 50): ") or "50")
        nome_ficheiro = input(
            "Nome do ficheiro (padrão 'euromilhoes_recentes.csv'): ").strip() or "euromilhoes_recentes.csv"

        resultados = scraper.obter_resultados_recentes(num_sorteios)
        scraper.salvar_csv(resultados, nome_ficheiro)

    elif opcao == "2":
        ficheiro_existente = input("Caminho do ficheiro existente: ").strip()
        novo_ficheiro = input(
            "Nome do ficheiro atualizado (padrão 'euromilhoes_atualizado.csv'): ").strip() or "euromilhoes_atualizado.csv"

        scraper.atualizar_dataset_existente(ficheiro_existente, novo_ficheiro)

    elif opcao == "3":
        num_sorteios = int(input("Quantos sorteios obter via API? (padrão 20): ") or "20")

        resultados = scraper.obter_resultados_api_alternativa(num_sorteios)
        if resultados:
            scraper.salvar_csv(resultados, "euromilhoes_api.csv")
        else:
            print("❌ API não disponível ou falhou.")

    else:
        print("❌ Opção inválida!")


# Função para uso automático/agendado
def atualizar_automaticamente(ficheiro_dataset="euromilhoes_historico.csv"):
    """
    Função que pode ser chamada automaticamente (ex: via cron job)
    """
    scraper = EuromilhoesScraper()

    try:
        sucesso = scraper.atualizar_dataset_existente(
            ficheiro_dataset,
            ficheiro_dataset  # Sobrescrever o mesmo ficheiro
        )

        if sucesso:
            print(f"✅ Dataset '{ficheiro_dataset}' atualizado automaticamente!")
        else:
            print(f"ℹ️ Nenhuma atualização necessária para '{ficheiro_dataset}'")

    except Exception as e:
        print(f"❌ Erro na atualização automática: {str(e)}")


if __name__ == "__main__":
    main()