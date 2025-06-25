# github_to_db.py

import requests
import sqlite3
import pandas as pd
import os
from datetime import datetime
import sys # <--- ADICIONADO: Importar sys para sys.exit()

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES GLOBAIS [EDITÁVEL]
# ============================================================================

GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_USERNAME = "google" # ✏️ MANTENHA O TOKEN INVÁLIDO AQUI PARA TESTAR O ERRO
import os # <--- Adicione esta linha no TOPO do arquivo (se não estiver lá)
# ...
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN_ENV") # Lê o token de uma variável de ambiente

DB_NAME = "github_repos.db" # Nome do arquivo do banco de dados SQLite
PER_PAGE = 100 # Itens por página na API

# ============================================================================
# ⚙️ PASSO 2: FUNÇÕES PARA INTERAGIR COM A API E O BANCO DE DADOS
# ============================================================================

def get_all_user_repositories(username, token=None):
    """
    Busca TODAS as informações sobre os repositórios públicos de um usuário do GitHub,
    lidando com paginação. Retorna uma lista de dicionários.
    """
    print(f"Buscando repositórios para o usuário: {username} na API do GitHub...")
    all_repos_data = []
    page = 1
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    while True:
        repos_url = f"{GITHUB_API_BASE_URL}/users/{username}/repos?per_page={PER_PAGE}&page={page}"
        print(f"  -> Buscando página {page}...")
        try:
            response = requests.get(repos_url, headers=headers)
            response.raise_for_status()
            repos_page_data = response.json()
            if not repos_page_data:
                break
            all_repos_data.extend(repos_page_data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"ERRO ao buscar dados da API do GitHub: {e}")
            return None # Retorna None em caso de erro
    print(f"Busca completa. Total de {len(all_repos_data)} repositórios encontrados.")
    return all_repos_data

def create_table_if_not_exists(conn):
    """Cria a tabela 'repos' no banco de dados se ela ainda não existir."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            proprietario TEXT NOT NULL,
            descricao TEXT,
            estrelas INTEGER,
            forks INTEGER,
            ultima_atualizacao TEXT,
            linguagem_principal TEXT,
            url TEXT NOT NULL UNIQUE,
            data_coleta TEXT NOT NULL
        );
    """)
    conn.commit()
    print(f"Tabela 'repos' verificada/criada no '{DB_NAME}'.")

def insert_repo_data(conn, repo_data, owner_username):
    """Insere os dados de um repositório na tabela 'repos'."""
    cursor = conn.cursor()
    
    repo_id = repo_data.get('id')
    nome = repo_data.get('name')
    proprietario = owner_username
    descricao = repo_data.get('description')
    estrelas = repo_data.get('stargazers_count')
    forks = repo_data.get('forks_count')
    ultima_atualizacao = repo_data.get('updated_at')
    linguagem_principal = repo_data.get('language')
    url = repo_data.get('html_url')
    data_coleta = datetime.now().isoformat()

    try:
        cursor.execute("""
            INSERT OR REPLACE INTO repos (
                id, nome, proprietario, descricao, estrelas, forks,
                ultima_atualizacao, linguagem_principal, url, data_coleta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (repo_id, nome, proprietario, descricao, estrelas, forks,
              ultima_atualizacao, linguagem_principal, url, data_coleta))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao inserir '{nome}': {e}")
        return False
    except Exception as e:
        print(f"ERRO inesperado ao inserir '{nome}': {e}")
        return False

# ============================================================================
# 🚀 PASSO 3: EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    if not GITHUB_TOKEN or GITHUB_TOKEN == "SEU_TOKEN_DE_ACESSO_PESSOAL_AQUI":
        print("ERRO: GITHUB_TOKEN nao configurado. Por favor, adicione seu token.")
        sys.exit(1) # Sai com erro se o token não estiver configurado
    elif not GITHUB_USERNAME:
        print("ERRO: GITHUB_USERNAME nao definido. Por favor, defina um usuario.")
        sys.exit(1) # Sai com erro se o usuário não estiver definido
    else:
        # 1. Obter dados da API do GitHub
        repos_from_api = get_all_user_repositories(GITHUB_USERNAME, GITHUB_TOKEN)

        if repos_from_api:
            # 2. Conectar ao banco de dados SQLite
            try:
                conn = sqlite3.connect(DB_NAME)
                print(f"Conectado ao banco de dados '{DB_NAME}'.")
                
                # 3. Criar a tabela se nao existir
                create_table_if_not_exists(conn)

                # 4. Inserir dados no banco de dados
                print(f"Iniciando insercao/atualizacao de {len(repos_from_api)} repositorios no banco de dados...")
                inserted_count = 0
                for repo in repos_from_api:
                    if insert_repo_data(conn, repo, GITHUB_USERNAME):
                        inserted_count += 1
                
                conn.close()
                print(f"Processo concluido. {inserted_count} repositorios inseridos/atualizados no banco de dados.")

            except sqlite3.Error as e:
                print(f"ERRO no banco de dados SQLite: {e}")
                sys.exit(1) # Sai com erro se houver problema no DB
            except Exception as e:
                print(f"ERRO inesperado no processo de banco de dados: {e}")
                sys.exit(1) # Sai com erro se houver outro erro
        else:
            print("Nao foi possivel obter repositorios da API. Nenhuma insercao no banco de dados.")
            sys.exit(1) # <--- MUDANÇA AQUI: Sai com erro se a API falhou