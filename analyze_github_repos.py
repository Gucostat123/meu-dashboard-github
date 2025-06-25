#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import os # Adicionado para verificar o caminho de output

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES DA ANÁLISE [EDITÁVEL]
# ============================================================================

CSV_FILENAME = "github_repos.csv"

# 📝 Nome do arquivo de saída para os resultados da análise
# Se vazio, imprime apenas no terminal. Se preenchido, salva no arquivo.
OUTPUT_FILENAME = "analise_repositorios_avancada.txt" # ✏️ Novo nome de arquivo para a análise avançada

# ============================================================================
# ⚙️ PASSO 2: FUNÇÃO PARA CARREGAR E ANALISAR DADOS
# ============================================================================

def analyze_repos(filename, output_file=None):
    if not os.path.exists(filename):
        print(f"❌ ERRO: O arquivo '{filename}' não foi encontrado.")
        print("  -> Certifique-se de que o script 'Hub.py' foi executado e salvou o CSV corretamente.")
        return

    # Define onde a saída será escrita
    if output_file:
        f_out = open(output_file, 'w', encoding='utf-8')
        sys.stdout = f_out
        print(f"Salvando resultados da análise em '{output_file}'...")
    else:
        sys.stdout = sys.__stdout__ # Restaura a saída padrão para o terminal

    try:
        df = pd.read_csv(filename)
        print(f"✅ Dados carregados com sucesso de '{filename}'! Total de {len(df)} repositórios.")

        # Converte a coluna de data para o tipo datetime do Pandas
        df['Ultima_Atualizacao'] = pd.to_datetime(df['Ultima_Atualizacao'], errors='coerce') # 'coerce' transforma inválidos em NaT (Not a Time)

        # --- ANÁLISES DE DADOS AVANÇADAS ---
        print("\n--- ANÁLISE DE DADOS DOS REPOSITÓRIOS ---")

        # 1. Média, Mediana e Desvio Padrão de Estrelas e Forks
        print("\n📊 Métricas de Estrelas e Forks:")
        print(f"  Média de Estrelas: {df['Estrelas'].mean():.2f}")
        print(f"  Mediana de Estrelas: {df['Estrelas'].median()}")
        print(f"  Média de Forks: {df['Forks'].mean():.2f}")
        print(f"  Mediana de Forks: {df['Forks'].median()}")

        # 2. Top 10 Repositórios por Estrelas
        print("\n⭐ Top 10 Repositórios por Estrelas:")
        top_stars = df.sort_values(by='Estrelas', ascending=False).head(10)
        for index, row in top_stars.iterrows():
            print(f"- {row['Nome']} (Estrelas: {row['Estrelas']}, Forks: {row['Forks']}, Ling: {row['Linguagem_Principal']})")

        # 3. Top 10 Repositórios por Forks
        print("\n🍴 Top 10 Repositórios por Forks:")
        top_forks = df.sort_values(by='Forks', ascending=False).head(10)
        for index, row in top_forks.iterrows():
            print(f"- {row['Nome']} (Forks: {row['Forks']}, Estrelas: {row['Estrelas']}, Ling: {row['Linguagem_Principal']})")

        # 4. As 5 Linguagens Mais Comuns e seus Repositórios Médios
        print("\n🗣️ Top 5 Linguagens Mais Comuns e Métricas Médias:")
        language_stats = df.groupby('Linguagem_Principal').agg(
            Total_Repos=('Nome', 'count'),
            Media_Estrelas=('Estrelas', 'mean'),
            Media_Forks=('Forks', 'mean')
        ).sort_values(by='Total_Repos', ascending=False).head(5)
        print(language_stats.round(2)) # Arredonda para 2 casas decimais

        # 5. Repositórios Atualizados nos Últimos 6 Meses
        print("\n🆕 Repositórios Atualizados nos Últimos 6 Meses:")
        # Calcula a data de 6 meses atrás a partir da data mais recente no dataset
        # ou da data atual, para ser mais preciso
        from datetime import timedelta
        # Se todos os Ultima_Atualizacao forem NaT, max() dará erro.
        # Usa pd.Timestamp.now() como fallback para o cálculo.
        if df['Ultima_Atualizacao'].dropna().empty:
            six_months_ago = pd.Timestamp.now() - timedelta(days=6*30) # Aprox. 6 meses
        else:
            most_recent_update = df['Ultima_Atualizacao'].max()
            six_months_ago = most_recent_update - timedelta(days=6*30) # Aprox. 6 meses

        recent_repos = df[df['Ultima_Atualizacao'] > six_months_ago].sort_values(by='Ultima_Atualizacao', ascending=False)
        if not recent_repos.empty:
            for index, row in recent_repos.head(10).iterrows(): # Mostra os 10 mais recentes
                print(f"- {row['Nome']} (Estrelas: {row['Estrelas']}, Última: {row['Ultima_Atualizacao'].strftime('%Y-%m-%d')})")
            if len(recent_repos) > 10:
                print(f"  ... e outros {len(recent_repos) - 10} repositórios recentes.")
        else:
            print("  Nenhum repositório atualizado nos últimos 6 meses encontrado.")


        # 6. Repositórios sem Descrição
        print("\n📝 Repositórios Sem Descrição:")
        no_description = df[df['Descricao'].isnull() | (df['Descricao'] == 'Sem descrição')]
        if not no_description.empty:
            for index, row in no_description.head(5).iterrows():
                print(f"- {row['Nome']}")
            if len(no_description) > 5:
                print(f"  ... e outros {len(no_description) - 5} repositórios sem descrição.")
        else:
            print("  Todos os repositórios possuem descrição.")


        print("\n--- FIM DA ANÁLISE ---")

    except FileNotFoundError:
        print(f"❌ ERRO: O arquivo '{filename}' não foi encontrado.")
        print("  -> Certifique-se de que o script 'Hub.py' foi executado e salvou o CSV corretamente.")
        print("  -> O arquivo CSV deve estar na mesma pasta do 'analyze_github_repos.py'.")
    except KeyError as e:
        print(f"❌ ERRO: Coluna '{e}' não encontrada no CSV.")
        print("  -> Verifique se os nomes das colunas no seu CSV correspondem aos esperados (Nome, Estrelas, Forks, etc.).")
    except Exception as e:
        print(f"❌ ERRO inesperado durante a análise: {e}")
    finally:
        if output_file:
            f_out.close()
            sys.stdout = sys.__stdout__
            print(f"\nAnálise concluída. Resultados salvos em '{output_file}'.")


# ============================================================================
# 🚀 PASSO 3: EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    if OUTPUT_FILENAME:
        analyze_repos(CSV_FILENAME, OUTPUT_FILENAME)
    else:
        analyze_repos(CSV_FILENAME)