# visualize_github_repos.py

import pandas as pd
import plotly.express as px # Para gráficos mais fáceis com Plotly
import os # Para verificar a existência do arquivo

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES DA VISUALIZAÇÃO [EDITÁVEL]
# ============================================================================

# 📂 Nome do arquivo CSV gerado pelo script Hub.py
CSV_FILENAME = "github_repos.csv"

# 📊 Nomes dos arquivos HTML de saída para os gráficos
OUTPUT_CHART_STARS = "top_repos_por_estrelas.html"
OUTPUT_CHART_LANGUAGES = "repos_por_linguagem.html"

# ============================================================================
# ⚙️ PASSO 2: FUNÇÃO PARA CARREGAR DADOS E GERAR GRÁFICOS
# ============================================================================

def generate_interactive_charts(filename):
    """
    Carrega dados de repositórios de um CSV e gera gráficos interativos Plotly.
    Salva os gráficos como arquivos HTML.
    """
    if not os.path.exists(filename):
        print(f"❌ ERRO: O arquivo '{filename}' não foi encontrado.")
        print("  -> Certifique-se de que o script 'Hub.py' foi executado e salvou o CSV corretamente.")
        return

    try:
        df = pd.read_csv(filename)
        print(f"✅ Dados carregados com sucesso de '{filename}'! Total de {len(df)} repositórios.")

        # --- Geração de Gráficos ---

        # 1. Gráfico de Top 10 Repositórios por Estrelas
        print(f"\nGerando '{OUTPUT_CHART_STARS}' (Top 10 Repositórios por Estrelas)...")
        # Filtra para repositórios com um nome e estrelas para evitar problemas
        df_filtered_stars = df[df['Estrelas'].notna() & df['Nome'].notna()]
        top_stars_df = df_filtered_stars.sort_values(by='Estrelas', ascending=False).head(10)

        fig_stars = px.bar(top_stars_df,
                           x='Nome',
                           y='Estrelas',
                           title='Top 10 Repositórios por Estrelas',
                           labels={'Nome': 'Repositório', 'Estrelas': 'Número de Estrelas'},
                           hover_data=['Descricao', 'Forks', 'Linguagem_Principal', 'URL']) # Informações ao passar o mouse

        fig_stars.update_layout(xaxis_title="Repositório", yaxis_title="Estrelas", title_x=0.5)
        fig_stars.write_html(OUTPUT_CHART_STARS)
        print(f"✅ Gráfico '{OUTPUT_CHART_STARS}' salvo com sucesso!")

        # 2. Gráfico de Contagem de Repositórios por Linguagem Principal
        print(f"Gerando '{OUTPUT_CHART_LANGUAGES}' (Contagem de Repositórios por Linguagem)...")
        language_counts_df = df['Linguagem_Principal'].fillna('Desconhecida').value_counts().reset_index()
        language_counts_df.columns = ['Linguagem', 'Contagem']

        fig_languages = px.pie(language_counts_df,
                               names='Linguagem',
                               values='Contagem',
                               title='Distribuição de Repositórios por Linguagem Principal',
                               hole=0.3) # Faz um gráfico de rosca

        fig_languages.update_traces(textposition='inside', textinfo='percent+label')
        fig_languages.update_layout(title_x=0.5)
        fig_languages.write_html(OUTPUT_CHART_LANGUAGES)
        print(f"✅ Gráfico '{OUTPUT_CHART_LANGUAGES}' salvo com sucesso!")

        print("\nTodos os gráficos interativos foram gerados na pasta do projeto.")
        print("Abra os arquivos .html no seu navegador para visualizá-los!")

    except KeyError as e:
        print(f"❌ ERRO: Coluna '{e}' não encontrada no CSV.")
        print("  -> Verifique se os nomes das colunas no seu CSV correspondem aos esperados.")
        print("  -> Certifique-se de que o CSV foi gerado corretamente pelo script 'Hub.py'.")
    except Exception as e:
        print(f"❌ ERRO inesperado durante a geração dos gráficos: {e}")

# ============================================================================
# 🚀 PASSO 3: EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    generate_interactive_charts(CSV_FILENAME)