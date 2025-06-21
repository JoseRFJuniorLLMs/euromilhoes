import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import itertools

# Configuração da página Streamlit
st.set_page_config(
    page_title="Analisador EuroMilhões",
    page_icon="🎰",
    layout="wide"
)


class EuromilhoesAnalyzer:
    def __init__(self):
        self.df = None
        self.colunas_bolas = ['Number 1', 'Number 2', 'Number 3', 'Number 4', 'Number 5']
        self.colunas_estrelas = ['Star 1', 'Star 2']

    def carregar_dados(self, uploaded_file):
        """Carrega os dados do ficheiro CSV"""
        try:
            self.df = pd.read_csv(uploaded_file)

            # Tenta converter coluna de data se existir
            date_columns = [col for col in self.df.columns if 'date' in col.lower() or 'data' in col.lower()]
            if date_columns:
                self.df[date_columns[0]] = pd.to_datetime(self.df[date_columns[0]], errors='coerce')

            return True, f"Dataset carregado com sucesso! {len(self.df)} registos encontrados."
        except Exception as e:
            return False, f"Erro ao carregar ficheiro: {str(e)}"

    def verificar_colunas(self):
        """Verifica e ajusta os nomes das colunas automaticamente"""
        if self.df is None:
            return False, "Nenhum dataset carregado"

        # Tenta encontrar colunas de números automaticamente
        num_cols = [col for col in self.df.columns if any(x in col.lower() for x in ['number', 'num', 'bola'])]
        star_cols = [col for col in self.df.columns if any(x in col.lower() for x in ['star', 'estrela'])]

        if len(num_cols) >= 5:
            self.colunas_bolas = num_cols[:5]
        if len(star_cols) >= 2:
            self.colunas_estrelas = star_cols[:2]

        return True, f"Colunas identificadas: {self.colunas_bolas + self.colunas_estrelas}"

    def filtrar_por_data(self, data_inicio, data_fim):
        """Filtra o dataset por intervalo de datas"""
        if self.df is None:
            return False, "Nenhum dataset carregado"

        date_columns = [col for col in self.df.columns if 'date' in col.lower() or 'data' in col.lower()]
        if not date_columns:
            return False, "Nenhuma coluna de data encontrada"

        date_col = date_columns[0]
        mask = (self.df[date_col] >= data_inicio) & (self.df[date_col] <= data_fim)
        self.df = self.df[mask]

        return True, f"Dataset filtrado: {len(self.df)} registos no período selecionado"

    def calcular_frequencias(self):
        """Calcula frequências dos números e estrelas"""
        if self.df is None:
            return None, None

        # Frequência dos números principais
        freq_bolas = pd.concat([self.df[col] for col in self.colunas_bolas]).value_counts().sort_index()

        # Frequência das estrelas
        freq_estrelas = pd.concat([self.df[col] for col in self.colunas_estrelas]).value_counts().sort_index()

        return freq_bolas, freq_estrelas

    def numeros_quentes_frios(self, freq_series, top_n=10):
        """Identifica números quentes e frios"""
        quentes = freq_series.nlargest(top_n)
        frios = freq_series.nsmallest(top_n)
        return quentes, frios

    def analisar_pares(self):
        """Analisa frequência de pares de números"""
        if self.df is None:
            return None

        pares = []
        for _, row in self.df.iterrows():
            numeros = sorted([row[col] for col in self.colunas_bolas])
            pares.extend(list(itertools.combinations(numeros, 2)))

        freq_pares = Counter(pares)
        return pd.Series(freq_pares).sort_values(ascending=False)

    def analisar_por_intervalos(self, freq_series):
        """Analisa frequência por intervalos de números"""
        intervalos = {
            '1-10': range(1, 11),
            '11-20': range(11, 21),
            '21-30': range(21, 31),
            '31-40': range(31, 41),
            '41-50': range(41, 51)
        }

        freq_intervalos = {}
        for nome, intervalo in intervalos.items():
            freq_intervalos[nome] = sum(freq_series.get(num, 0) for num in intervalo)

        return pd.Series(freq_intervalos)

    def criar_grafico_frequencias(self, freq_series, titulo, cor='blue'):
        """Cria gráfico de barras das frequências"""
        fig = go.Figure(data=go.Bar(
            x=freq_series.index,
            y=freq_series.values,
            marker_color=cor,
            text=freq_series.values,
            textposition='auto'
        ))

        fig.update_layout(
            title=titulo,
            xaxis_title="Número",
            yaxis_title="Frequência",
            showlegend=False,
            height=500
        )

        return fig

    def criar_heatmap_correlacao(self):
        """Cria heatmap de correlação entre posições"""
        if self.df is None:
            return None

        # Matriz de correlação entre as posições dos números
        matriz_numeros = self.df[self.colunas_bolas].corr()

        fig = go.Figure(data=go.Heatmap(
            z=matriz_numeros.values,
            x=self.colunas_bolas,
            y=self.colunas_bolas,
            colorscale='RdYlBu',
            text=np.round(matriz_numeros.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))

        fig.update_layout(
            title="Correlação entre Posições dos Números",
            height=500
        )

        return fig


def main():
    st.title("🎰 Analisador Avançado de EuroMilhões")
    st.markdown("---")

    # Inicializar o analisador
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = EuromilhoesAnalyzer()

    analyzer = st.session_state.analyzer

    # Sidebar para upload e configurações
    with st.sidebar:
        st.header("📁 Carregar Dados")
        uploaded_file = st.file_uploader("Escolha o ficheiro CSV", type=['csv'])

        if uploaded_file is not None:
            success, message = analyzer.carregar_dados(uploaded_file)
            if success:
                st.success(message)

                # Verificar colunas
                success, col_message = analyzer.verificar_colunas()
                st.info(col_message)

                # Filtros de data
                st.header("📅 Filtros")
                if analyzer.df is not None:
                    date_columns = [col for col in analyzer.df.columns if
                                    'date' in col.lower() or 'data' in col.lower()]

                    if date_columns:
                        col_data = date_columns[0]
                        min_date = analyzer.df[col_data].min()
                        max_date = analyzer.df[col_data].max()

                        data_inicio = st.date_input("Data de início", min_date)
                        data_fim = st.date_input("Data de fim", max_date)

                        if st.button("Aplicar Filtro de Data"):
                            success, filter_message = analyzer.filtrar_por_data(
                                pd.to_datetime(data_inicio),
                                pd.to_datetime(data_fim)
                            )
                            if success:
                                st.success(filter_message)
                            else:
                                st.error(filter_message)
            else:
                st.error(message)

    # Área principal
    if analyzer.df is not None:
        # Tabs para diferentes análises
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Frequências Básicas",
            "🔥 Quentes & Frios",
            "👥 Análise de Pares",
            "📈 Por Intervalos",
            "🔗 Correlações"
        ])

        with tab1:
            st.header("Frequências dos Números e Estrelas")

            freq_bolas, freq_estrelas = analyzer.calcular_frequencias()

            if freq_bolas is not None and freq_estrelas is not None:
                col1, col2 = st.columns(2)

                with col1:
                    fig_bolas = analyzer.criar_grafico_frequencias(
                        freq_bolas, "Frequência dos Números Principais (1-50)", 'lightblue'
                    )
                    st.plotly_chart(fig_bolas, use_container_width=True)

                with col2:
                    fig_estrelas = analyzer.criar_grafico_frequencias(
                        freq_estrelas, "Frequência das Estrelas (1-12)", 'gold'
                    )
                    st.plotly_chart(fig_estrelas, use_container_width=True)

                # Estatísticas resumo
                st.subheader("📈 Estatísticas Resumo")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total de Sorteios", len(analyzer.df))
                with col2:
                    st.metric("Número Mais Frequente", freq_bolas.idxmax())
                with col3:
                    st.metric("Frequência Máxima", freq_bolas.max())
                with col4:
                    st.metric("Estrela Mais Frequente", freq_estrelas.idxmax())

        with tab2:
            st.header("Números Quentes e Frios")

            freq_bolas, freq_estrelas = analyzer.calcular_frequencias()

            if freq_bolas is not None:
                top_n = st.slider("Quantos números mostrar?", 5, 25, 10)

                quentes_bolas, frios_bolas = analyzer.numeros_quentes_frios(freq_bolas, top_n)
                quentes_estrelas, frios_estrelas = analyzer.numeros_quentes_frios(freq_estrelas, min(top_n, 12))

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("🔥 Números Mais Quentes")
                    st.dataframe(quentes_bolas.to_frame('Frequência'))

                    st.subheader("⭐ Estrelas Mais Quentes")
                    st.dataframe(quentes_estrelas.to_frame('Frequência'))

                with col2:
                    st.subheader("🧊 Números Mais Frios")
                    st.dataframe(frios_bolas.to_frame('Frequência'))

                    st.subheader("⭐ Estrelas Mais Frias")
                    st.dataframe(frios_estrelas.to_frame('Frequência'))

        with tab3:
            st.header("Análise de Pares de Números")

            with st.spinner("Calculando pares mais frequentes..."):
                freq_pares = analyzer.analisar_pares()

            if freq_pares is not None:
                top_pares = st.slider("Quantos pares mostrar?", 10, 50, 20)

                st.subheader(f"Top {top_pares} Pares Mais Frequentes")

                # Criar DataFrame para melhor visualização
                pares_df = pd.DataFrame({
                    'Par': [f"{par[0]}-{par[1]}" for par in freq_pares.head(top_pares).index],
                    'Frequência': freq_pares.head(top_pares).values
                })

                # Gráfico de barras dos pares
                fig = px.bar(
                    pares_df,
                    x='Par',
                    y='Frequência',
                    title=f"Top {top_pares} Pares Mais Frequentes"
                )
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

                # Tabela detalhada
                st.dataframe(pares_df, use_container_width=True)

        with tab4:
            st.header("Análise por Intervalos de Números")

            freq_bolas, _ = analyzer.calcular_frequencias()

            if freq_bolas is not None:
                freq_intervalos = analyzer.analisar_por_intervalos(freq_bolas)

                # Gráfico de pizza
                fig = px.pie(
                    values=freq_intervalos.values,
                    names=freq_intervalos.index,
                    title="Distribuição por Intervalos de Números"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Gráfico de barras
                fig_bar = px.bar(
                    x=freq_intervalos.index,
                    y=freq_intervalos.values,
                    title="Frequência por Intervalos",
                    labels={'x': 'Intervalo', 'y': 'Frequência Total'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                # Tabela
                st.dataframe(freq_intervalos.to_frame('Frequência Total'))

        with tab5:
            st.header("Análise de Correlações")

            heatmap = analyzer.criar_heatmap_correlacao()
            if heatmap:
                st.plotly_chart(heatmap, use_container_width=True)

                st.info("""
                **Como interpretar:** 
                - Valores próximos de 1: correlação positiva forte
                - Valores próximos de 0: sem correlação
                - Valores próximos de -1: correlação negativa forte
                """)

        # Aviso importante
        st.markdown("---")
        st.warning(
            "⚠️ **Aviso Importante:** Esta análise descreve padrões históricos e não tem poder preditivo sobre sorteios futuros. Os resultados da lotaria são aleatórios.")

    else:
        st.info("👆 Por favor, carregue um ficheiro CSV na barra lateral para começar a análise.")

        # Exemplo de formato esperado
        st.subheader("📋 Formato Esperado do CSV")
        exemplo_df = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Number 1': [12, 5],
            'Number 2': [23, 15],
            'Number 3': [34, 25],
            'Number 4': [45, 35],
            'Number 5': [50, 45],
            'Star 1': [3, 7],
            'Star 2': [8, 11]
        })
        st.dataframe(exemplo_df)


if __name__ == "__main__":
    main()