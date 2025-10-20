# dashboard/app_dashboard.py

import streamlit as st
import requests
import pandas as pd

# Configuração da Página
st.set_page_config(
    page_title="Dashboard de Monitoramento da API de Livros",
    page_icon="📚",
    layout="wide"
)
API_BASE_URL = "https://turetto-api-livros-3a30130b990d.herokuapp.com/"

def get_stats_overview():
    """Busca as estatísticas gerais da API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/stats/overview")
        response.raise_for_status()  # lança um erro para status ruins (4xx ou 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar estatísticas gerais: {e}")
        return None

def get_all_books():
    """Busca todos os livros da API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/books")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar a lista de livros: {e}")
        return None


# Insterface streamlit
st.title("Dashboard de Monitoramento da API de Livros")
st.markdown("Este dashboard consome os dados da API de Livros para exibir insights sobre a coleção.")

# Botão para recarregar os dados
if st.button("Recarregar Dados"):
    st.rerun()

st.header("Visão Geral da Coleção")

# Busca e exibe as estatísticas gerais
stats = get_stats_overview()

if stats:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Livros", stats.get("total_livros", 0))
    col2.metric("Preço Médio", f"£ {stats.get('preco_medio', 0):.2f}")
    
    # Exibe a distribuição de ratings
    ratings = stats.get("distribuicao_ratings", {})
    if ratings:
        df_ratings = pd.DataFrame(list(ratings.items()), columns=['Avaliação', 'Quantidade'])
        st.subheader("Distribuição de Avaliações")
        st.bar_chart(df_ratings.set_index('Avaliação'))

st.divider()

st.header("Navegador de Livros")
st.markdown("A tabela abaixo mostra todos os livros da coleção e pode ser ordenada e pesquisada.")

# Busca e exibe todos os livros em uma tabela
books = get_all_books()
if books:
    df_books = pd.DataFrame(books)
    st.dataframe(df_books, use_container_width=True)