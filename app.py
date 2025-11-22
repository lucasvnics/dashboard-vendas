import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# CONFIG. DA PAGINA

st.set_page_config(
    page_title="Dashboard de Vendas E-commerce",
    page_icon="📊",
    layout="wide"
)

# FUNÇÃO GERAÇAO DE DADOS

@st.cache_data # Cache para não recriar os dados a cada interação
def carregar_dados_ficticios(n_linhas=1000):
    
    np.random.seed(42)

    produtos = {
        'Eletrônicos': ['Smartphone', 'Laptop', 'Tablet', 'Monitor'],
        'Roupas': ['Camiseta', 'Calça Jeans', 'Jaqueta', 'Tênis'],
        'Casa': ['Sofá', 'Mesa', 'Luminária', 'Cadeira Gamer']
    }
    regioes = ['Sudeste', 'Sul', 'Nordeste', 'Norte', 'Centro-Oeste']

    dados = []

    data_inicial = datetime(2024, 1, 1)
    for _ in range(n_linhas):
        categoria = np.random.choice(list(produtos.keys()))
        produto = np.random.choice(produtos[categoria])

        preco_base = {'Eletrônicos': 800, 'Roupas': 50, 'Casa': 300}
        valor = round(np.random.normal(preco_base[categoria], 50), 2)
        if valor < 0: valor = 20.00

        dados.append({
            'Data': data_inicial + timedelta(days=np.random.randint(0, 365)),
            'Produto': produto,
            'Categoria': categoria,
            'Valor Unitário': valor,
            'Quantidade': np.random.randint(1, 5),
            'Região': np.random.choice(regioes)
        })

        df = pd.DataFrame(dados)

        df['Faturamento'] = df['Valor Unitário'] * df['Quantidade']

        df = pd.concat([df, df.sample(frac=0.02)])

        indices_nulos = df.sample(frac=0.05).index
    df.loc[indices_nulos, 'Região'] = np.nan

    return df

def limpar_dados(df):


    linhas_iniciais = len(df)

    df = df.drop_duplicates()

    df = df.dropna(subset=['Região', 'Categoria'])

    linhas_finais = len(df)
    linhas_removidas = linhas_iniciais - linhas_finais
    
    return df, linhas_removidas

def main():
    st.title("📊 Dashboard de Vendas E-commerce")
    st.markdown("### Análise Interativa de Performance de Vendas")

    df_raw = carregar_dados_ficticios()
    df_clean, linhas_removidas = limpar_dados(df_raw)

    with st.expander("ℹ️ Detalhes do Processamento de Dados"):
        st.write(f"Dados brutos carregados: {len(df_raw)} linhas.")
        st.write(f"Linhas removidas (duplicadas/nulas): {linhas_removidas}.")
        st.write(f"Dados limpos para análise: {len(df_clean)} linhas.")
        st.dataframe(df_clean.head())

        st.divider()

        st.sidebar.header("Filtros")

        regioes_disponiveis = sorted(df_clean['Região'].unique())
    regiao_selecionada = st.sidebar.multiselect(
        "Selecione a Região", 
        options=regioes_disponiveis,
        default=regioes_disponiveis
    )
    categorias_disponiveis = sorted(df_clean['Categoria'].unique())
    categoria_selecionada = st.sidebar.multiselect(
        "Selecione a Categoria", 
        options=categorias_disponiveis, 
        default=categorias_disponiveis
    )

    df_filtrado = df_clean[
        (df_clean['Região'].isin(regiao_selecionada)) & 
        (df_clean['Categoria'].isin(categoria_selecionada))
    ]

    if df_filtrado.empty:
        st.warning("Nenhum dado disponível com os filtros selecionados.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    faturamento_total = df_filtrado['Faturamento'].sum()
    total_vendas = df_filtrado['Quantidade'].sum()
    ticket_medio = df_filtrado['Faturamento'].mean()

    with col1:
        st.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
    with col2:
        st.metric("📦 Total de Itens Vendidos", f"{total_vendas}")
    with col3:
        st.metric("🏷️ Ticket Médio", f"R$ {ticket_medio:,.2f}")

        st.divider()

        chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Faturamento por Categoria")
        fig_bar = px.bar(
            df_filtrado.groupby('Categoria')['Faturamento'].sum().reset_index(),
            x='Categoria', 
            y='Faturamento',
            text_auto='.2s',
            color='Categoria',
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with chart_col2:
        st.subheader("Distribuição por Região")
        fig_pie = px.pie(
            df_filtrado, 
            values='Faturamento', 
            names='Região',
            hole=0.4, # Gráfico de Rosca (Donut)
            template="plotly_white"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Evolução Mensal do Faturamento")  

        df_filtrado['Mes_Ano'] = df_filtrado['Data'].dt.to_period('M').astype(str)
    vendas_mensais = df_filtrado.groupby('Mes_Ano')['Faturamento'].sum().reset_index()
    
    fig_line = px.line(
        vendas_mensais, 
        x='Mes_Ano', 
        y='Faturamento', 
        markers=True,
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)

if __name__ == "__main__":
    main()