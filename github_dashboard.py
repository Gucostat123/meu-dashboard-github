# github_dashboard.py

import streamlit as st
import pandas as pd
import requests # Importar para fazer requisições HTTP para sua própria API
import plotly.express as px
import os
import numpy as np

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES GLOBAIS DO DASHBOARD [EDITÁVEL]
# ============================================================================

st.set_page_config(layout="wide", page_title="Dashboard GitHub (Via API Local)")

# 🌐 URL base da SUA API Flask local
FLASK_API_BASE_URL = "http://127.0.0.1:5000" # ✏️ Verifique se este é o endereço da sua API Flask

# ============================================================================
# ⚙️ PASSO 2: FUNÇÃO PARA OBTER DADOS DA SUA PRÓPRIA API
# ============================================================================

@st.cache_data(ttl=120) # Cacheia os resultados da API por 2 minutos
def get_repos_from_api(username_filter=None):
    """
    Busca repositórios da SUA PRÓPRIA API Flask.
    Se username_filter for fornecido, filtra por proprietário.
    """
    api_url = f"{FLASK_API_BASE_URL}/repositorios"
    params = {}
    
    if username_filter:
        if isinstance(username_filter, list) and len(username_filter) > 0:
            for owner in username_filter:
                if 'proprietario' not in params:
                    params['proprietario'] = []
                params['proprietario'].append(owner)
        else: # Single username filter
            params['proprietario'] = username_filter
    
    try:
        st.info(f"Conectando à sua API em {api_url} com filtros: {params}")
        response = requests.get(api_url, params=params)
        response.raise_for_status() # Lança exceção para erros HTTP
        
        repos_data = response.json()
        
        st.success(f"✅ Dados carregados da sua API. Total de {len(repos_data)} repositórios.")
        return repos_data

    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ ERRO: Não foi possível conectar à sua API Flask em {FLASK_API_BASE_URL}.")
        st.warning("  -> Certifique-se de que seu servidor Flask (github_api_server.py) está rodando em um terminal separado.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ ERRO ao carregar dados da sua API: {e}")
        return []

# ============================================================================
# 📊 PASSO 3: FUNÇÃO PARA ANALISAR E EXIBIR NO DASHBOARD
# ============================================================================

def analyze_and_display_dashboard(df_original, username_display):
    st.header(f"Análise de Repositórios GitHub de {username_display}")

    # --- Widgets de Filtragem ---
    st.sidebar.header("Opções de Filtragem")

    min_stars = int(df_original['Estrelas'].min()) if not df_original['Estrelas'].empty else 0
    max_stars = int(df_original['Estrelas'].max()) if not df_original['Estrelas'].empty else 0
    selected_min_stars = st.sidebar.slider(
        "Estrelas Mínimas:",
        min_value=min_stars,
        max_value=max_stars,
        value=min_stars
    )

    all_languages = df_original['Linguagem_Principal'].fillna('Desconhecida').unique().tolist()
    selected_languages = st.sidebar.multiselect(
        "Filtrar por Linguagem Principal:",
        options=all_languages,
        default=all_languages
    )

    search_query = st.sidebar.text_input("Buscar por Nome/Descrição:").lower()

    df_filtered = df_original[df_original['Estrelas'] >= selected_min_stars]
    df_filtered = df_filtered[df_filtered['Linguagem_Principal'].fillna('Desconhecida').isin(selected_languages)]
    
    if search_query:
        df_filtered = df_filtered[
            df_filtered['Nome'].str.lower().str.contains(search_query) |
            df_filtered['Descricao'].str.lower().str.contains(search_query)
        ]

    if df_filtered.empty:
        st.warning("Nenhum repositório encontrado com os filtros selecionados.")
        return


    # --- Métricas Chave ---
    st.subheader("Métricas Principais (Filtradas)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Repositórios", len(df_filtered))

    mean_stars = df_filtered['Estrelas'].mean()
    if np.isnan(mean_stars):
        col2.metric("Média de Estrelas", "N/A")
    else:
        col2.metric("Média de Estrelas", f"{float(mean_stars):.2f}")

    mean_forks = df_filtered['Forks'].mean()
    if np.isnan(mean_forks):
        col3.metric("Média de Forks", "N/A")
    else:
        col3.metric("Média de Forks", f"{float(mean_forks):.2f}")

    # 2. Top 10 Repositórios por Estrelas (Gráfico Interativo)
    st.subheader("⭐ Top 10 Repositórios por Estrelas (Filtrados)")
    top_stars_df = df_filtered.sort_values(by='Estrelas', ascending=False).head(10)
    if not top_stars_df.empty:
        fig_stars = px.bar(top_stars_df,
                           x='Nome',
                           y='Estrelas',
                           hover_data=['Descricao', 'Forks', 'Linguagem_Principal', 'URL'],
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_stars.update_layout(xaxis_title="Repositório", yaxis_title="Estrelas", showlegend=False)
        st.plotly_chart(fig_stars, use_container_width=True)
    else:
        st.info("Nenhum repositório com estrelas para exibir no gráfico com os filtros aplicados.")


    # 3. Distribuição de Repositórios por Linguagem
    st.subheader("🗣️ Distribuição de Repositórios por Linguagem Principal (Filtrados)")
    language_counts_df = df_filtered['Linguagem_Principal'].fillna('Desconhecida').value_counts().reset_index()
    language_counts_df.columns = ['Linguagem', 'Contagem']
    if not language_counts_df.empty and language_counts_df['Contagem'].sum() > 0:
        fig_languages = px.pie(language_counts_df,
                               names='Linguagem',
                               values='Contagem',
                               hole=0.3,
                               color_discrete_sequence=px.colors.qualitative.Set2)
        fig_languages.update_traces(textposition='inside', textinfo='percent+label')
        fig_languages.update_layout(title_x=0.5)
        st.plotly_chart(fig_languages, use_container_width=True)
    else:
        st.info("Nenhum dado de linguagem para exibir no gráfico com os filtros aplicados.")

    # 4. Tabela Completa de Dados
    st.subheader("Tabela Completa de Repositórios (Filtrados)")
    display_cols = ['Nome', 'Estrelas', 'Forks', 'Linguagem_Principal', 'Ultima_Atualizacao', 'URL', 'Descricao']
    st.dataframe(df_filtered[display_cols].set_index('Nome'), use_container_width=True)

# ============================================================================
# 🚀 PASSO 4: EXECUÇÃO PRINCIPAL DO DASHBOARD (LENDO DA API LOCAL)
# ============================================================================

if __name__ == "__main__":
    st.title("Analisador de Repositórios Públicos do GitHub (Fonte: Sua API Local)")

    # Obter todos os proprietários únicos da SUA API Flask (chamando /proprietarios)
    unique_owners_list_from_api = []
    try:
        owners_api_url = f"{FLASK_API_BASE_URL}/proprietarios"
        st.info(f"Conectando à sua API para listar proprietários: {owners_api_url}")
        owners_response = requests.get(owners_api_url)
        owners_response.raise_for_status() # Lança exceção para erros HTTP
        unique_owners_list_from_api = owners_response.json()
        
    except requests.exceptions.ConnectionError:
        st.error(f"❌ ERRO: Não foi possível conectar à sua API Flask em {FLASK_API_BASE_URL} para listar proprietários.")
        st.warning("  -> Certifique-se de que seu servidor Flask (github_api_server.py) está rodando em um terminal separado.")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ ERRO ao carregar proprietários da sua API: {e}")
        
    unique_owners = ['Todos']
    if unique_owners_list_from_api:
        unique_owners.extend(sorted(unique_owners_list_from_api))
        
    selected_owner_display = st.selectbox(
        "Selecione um Proprietário (Usuário GitHub) para analisar:",
        options=unique_owners,
        index=unique_owners.index('google') if 'google' in unique_owners else 0
    )

    df_repos = pd.DataFrame() 
    repos_from_api_raw = []

    if selected_owner_display and selected_owner_display != 'Todos':
        repos_from_api_raw = get_repos_from_api(username_filter=selected_owner_display)
    elif selected_owner_display == 'Todos':
        repos_from_api_raw = get_repos_from_api()
    else:
        st.info("Aguardando seleção de proprietário ou dados da sua API.")

    if repos_from_api_raw:
        df_repos = pd.DataFrame(repos_from_api_raw)
        
        # As colunas já vêm da API renomeadas do DB (estrelas, forks, etc.)
        # Mas para o Streamlit Display, precisamos dos nomes "Nome", "Estrelas", etc.
        # e a conversão para float
        
        # Converter colunas numéricas e de data
        df_repos['estrelas'] = pd.to_numeric(df_repos['estrelas'], errors='coerce').fillna(0).astype(float)
        df_repos['forks'] = pd.to_numeric(df_repos['forks'], errors='coerce').fillna(0).astype(float)
        df_repos['ultima_atualizacao'] = pd.to_datetime(df_repos['ultima_atualizacao'], errors='coerce')
        
        # Renomear para nomes de exibição no dashboard
        df_repos.rename(columns={
            'nome_repositorio': 'Nome',
            'proprietario_github': 'Proprietario',
            'estrelas': 'Estrelas',
            'forks': 'Forks',
            'ultima_atualizacao': 'Ultima_Atualizacao',
            'linguagem_principal': 'Linguagem_Principal',
            'url_html': 'URL',
            'descricao': 'Descricao',
            'data_coleta_api': 'Data_Coleta'
        }, inplace=True)


        analyze_and_display_dashboard(df_repos, selected_owner_display) # Passa o df_repos e o proprietario selecionado para exibicao
    elif selected_owner_display and selected_owner_display != 'Todos':
        st.info(f"Nenhum repositório encontrado para o proprietário '{selected_owner_display}' na sua API.")
    else:
        st.info("Certifique-se de que seu servidor Flask (github_api_server.py) está rodando e contém dados.")