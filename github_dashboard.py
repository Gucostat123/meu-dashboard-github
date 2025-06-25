# github_dashboard.py

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import numpy as np

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES GLOBAIS DO DASHBOARD [EDITÁVEL]
# ============================================================================

st.set_page_config(layout="wide", page_title="Análise de Repositórios GitHub (Avançado)")

# 📂 Nome do arquivo do banco de dados SQLite
DB_NAME = "github_repos.db"

# ============================================================================
# ⚙️ PASSO 2: FUNÇÃO PARA OBTER DADOS DO BANCO DE DADOS
# ============================================================================

@st.cache_data(ttl=600) # Armazena em cache os resultados da função por 10 minutos
def get_repos_from_db(username_filter=None):
    """
    Busca repositórios do banco de dados SQLite.
    Se username_filter for fornecido, filtra por proprietário.
    """
    if not os.path.exists(DB_NAME):
        st.error(f"❌ ERRO: Banco de dados '{DB_NAME}' não encontrado.")
        st.info("Por favor, execute 'python github_to_db.py' primeiro para criar e popular o banco de dados.")
        return pd.DataFrame()

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT * FROM repos"
        params = []
        
        if username_filter:
            if isinstance(username_filter, list) and len(username_filter) > 0:
                placeholders = ', '.join(['?' for _ in username_filter])
                query += f" WHERE proprietario IN ({placeholders})"
                params.extend(username_filter)
            else: # Single username filter
                query += " WHERE proprietario = ?"
                params.append(username_filter)
        
        df = pd.read_sql_query(query, conn, params=params)
        
        df.rename(columns={
            'id': 'ID_DB',
            'nome': 'Nome',
            'proprietario': 'Proprietario',
            'descricao': 'Descricao',
            'estrelas': 'Estrelas',
            'forks': 'Forks',
            'ultima_atualizacao': 'Ultima_Atualizacao',
            'linguagem_principal': 'Linguagem_Principal',
            'url': 'URL',
            'data_coleta': 'Data_Coleta'
        }, inplace=True)
        
        st.success(f"✅ Dados carregados do banco de dados '{DB_NAME}'. Total de {len(df)} repositórios.")
        return df

    except sqlite3.Error as e:
        st.error(f"❌ ERRO ao carregar dados do banco de dados: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

# ============================================================================
# 📊 PASSO 3: FUNÇÃO PARA ANALISAR E EXIBIR NO DASHBOARD
# ============================================================================

def analyze_and_display_dashboard(df_original, username): # Renomeado para df_original
    st.header(f"Análise de Repositórios GitHub de {username}")

    # --- Widgets de Filtragem ---
    st.sidebar.header("Opções de Filtragem")

    # Slider para filtrar por Estrelas mínimas
    min_stars = int(df_original['Estrelas'].min()) if not df_original['Estrelas'].empty else 0
    max_stars = int(df_original['Estrelas'].max()) if not df_original['Estrelas'].empty else 0
    selected_min_stars = st.sidebar.slider(
        "Estrelas Mínimas:",
        min_value=min_stars,
        max_value=max_stars,
        value=min_stars # Valor inicial
    )

    # Seleção múltipla para Linguagem Principal
    all_languages = df_original['Linguagem_Principal'].fillna('Desconhecida').unique().tolist()
    selected_languages = st.sidebar.multiselect(
        "Filtrar por Linguagem Principal:",
        options=all_languages,
        default=all_languages # Seleciona todas por padrão
    )

    # Campo de busca por nome ou descrição do repositório
    search_query = st.sidebar.text_input("Buscar por Nome/Descrição:").lower()

    # Aplicar filtros
    df_filtered = df_original[df_original['Estrelas'] >= selected_min_stars]
    df_filtered = df_filtered[df_filtered['Linguagem_Principal'].fillna('Desconhecida').isin(selected_languages)]
    
    if search_query:
        df_filtered = df_filtered[
            df_filtered['Nome'].str.lower().str.contains(search_query) |
            df_filtered['Descricao'].str.lower().str.contains(search_query)
        ]

    if df_filtered.empty:
        st.warning("Nenhum repositório encontrado com os filtros selecionados.")
        return # Sai da função se não houver dados para exibir após filtragem


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
# 🚀 PASSO 4: EXECUÇÃO PRINCIPAL DO DASHBOARD (LENDO DO DB E COM FILTROS)
# ============================================================================

if __name__ == "__main__":
    st.title("Analisador de Repositórios Públicos do GitHub (Fonte: Banco de Dados)")

    # Obter todos os proprietários únicos do DB para o filtro
    all_owners_df = get_repos_from_db()
    if not all_owners_df.empty:
        unique_owners = ['Todos'] + sorted(all_owners_df['Proprietario'].unique().tolist())
        
        selected_owner = st.selectbox(
            "Selecione um Proprietário (Usuário GitHub) para analisar:",
            options=unique_owners,
            index=unique_owners.index('google') if 'google' in unique_owners else 0
        )
    else:
        selected_owner = None
        st.warning("Nenhum dado encontrado no banco de dados para filtrar proprietários.")
        st.info("Certifique-se de ter executado 'python github_to_db.py' para popular o banco de dados.")

    df_repos = pd.DataFrame() 

    if selected_owner and selected_owner != 'Todos':
        df_repos = get_repos_from_db(username_filter=selected_owner)
    elif selected_owner == 'Todos':
        df_repos = get_repos_from_db()
    else:
        st.info("Aguardando seleção de proprietário ou dados no banco de dados.")

    if not df_repos.empty:
        # Converter colunas para tipos numéricos/datetime
        df_repos['Estrelas'] = pd.to_numeric(df_repos['Estrelas'], errors='coerce').fillna(0).astype(float)
        df_repos['Forks'] = pd.to_numeric(df_repos['Forks'], errors='coerce').fillna(0).astype(float)
        df_repos['Ultima_Atualizacao'] = pd.to_datetime(df_repos['Ultima_Atualizacao'], errors='coerce')
        
        display_username = selected_owner if selected_owner != 'Todos' else "Todos os Repositórios Coletados"
        
        analyze_and_display_dashboard(df_repos, display_username)
    elif selected_owner and selected_owner != 'Todos':
        st.info(f"Nenhum repositório encontrado para o proprietário '{selected_owner}' no banco de dados.")
    else:
        st.info("Carregue o banco de dados primeiro executando 'python github_to_db.py'.")