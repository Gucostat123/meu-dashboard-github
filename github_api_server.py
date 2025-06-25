# github_api_server.py

from flask import Flask, jsonify, request
import sqlite3
import pandas as pd
import os
import sys # Adicionar para sys.executable, importante para o Flask saber onde está rodando

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES DA API [EDITÁVEL]
# ============================================================================

app = Flask(__name__)

# Caminho absoluto para o banco de dados, importante para deployment
# Isso garante que o Flask encontre o DB, independentemente de onde o script é executado
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "github_repos.db")
print(f"DEBUG: Caminho do Banco de Dados: {DB_PATH}") # Adicionado para debug

# ============================================================================
# ⚙️ PASSO 2: FUNÇÃO PARA OBTER DADOS DO BANCO DE DADOS
#    (Reutilizada e adaptada do seu dashboard)
# ============================================================================

def get_repos_from_db_raw(username_filter=None):
    """
    Busca repositórios do banco de dados SQLite e retorna como lista de dicionários.
    """
    if not os.path.exists(DB_PATH): # Usar DB_PATH aqui
        print(f"ERRO: Banco de dados '{DB_PATH}' não encontrado para a API.")
        return []

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH) # Usar DB_PATH aqui
        query = "SELECT * FROM repos"
        params = []
        
        if username_filter:
            if isinstance(username_filter, list) and len(username_filter) > 0:
                placeholders = ', '.join(['?' for _ in username_filter])
                query += f" WHERE proprietario IN ({placeholders})"
                params.extend(username_filter)
            else:
                query += " WHERE proprietario = ?"
                params.append(username_filter)
        
        df = pd.read_sql_query(query, conn, params=params)
        
        df.rename(columns={
            'id': 'github_id',
            'nome': 'nome_repositorio',
            'proprietario': 'proprietario_github',
            'descricao': 'descricao',
            'estrelas': 'estrelas',
            'forks': 'forks',
            'ultima_atualizacao': 'ultima_atualizacao',
            'linguagem_principal': 'linguagem_principal',
            'url': 'url_html',
            'data_coleta': 'data_coleta_api'
        }, inplace=True)

        return df.to_dict(orient='records')

    except sqlite3.Error as e:
        print(f"ERRO ao carregar dados do banco de dados para a API: {e}")
        return []
    finally:
        if conn:
            conn.close()

# ============================================================================
# 🚀 PASSO 3: DEFINIÇÃO DOS ENDPOINTS DA API
# ============================================================================

@app.route('/')
def home():
    """Endpoint principal da API."""
    return "Bem-vindo à sua API de Repositórios GitHub! Use /repositorios ou /proprietarios."

@app.route('/repositorios', methods=['GET'])
def get_repos():
    """
    Endpoint para obter todos os repositórios ou filtrar por proprietário.
    Ex: /repositorios
    Ex: /repositorios?proprietario=google
    Ex: /repositorios?proprietario=google&proprietario=microsoft
    """
    proprietarios = request.args.getlist('proprietario')

    if proprietarios:
        data = get_repos_from_db_raw(username_filter=proprietarios)
    else:
        data = get_repos_from_db_raw()
    
    if not data:
        return jsonify({"message": "Nenhum repositorio encontrado para os criterios especificados."}), 404
    
    return jsonify(data), 200

@app.route('/proprietarios', methods=['GET'])
def get_owners():
    """
    Endpoint para obter uma lista de todos os proprietários de repositórios no DB.
    """
    df_all_repos = get_repos_from_db_raw()
    if not df_all_repos:
        return jsonify({"message": "Nenhum proprietario encontrado no banco de dados."}), 404
    
    df_temp = pd.DataFrame(df_all_repos)
    if 'proprietario_github' in df_temp.columns:
        owners = df_temp['proprietario_github'].unique().tolist()
        return jsonify(sorted(owners)), 200
    else:
        return jsonify({"message": "Coluna 'proprietario_github' não encontrada nos dados."}), 500

# ============================================================================
# 🚀 PASSO 4: INÍCIO DO SERVIDOR DA API (PARA DEPLOYMENT E LOCAL)
# ============================================================================

if __name__ == '__main__':
    print(f"Iniciando sua API Flask. Conectado ao banco de dados: {DB_PATH}")
    # Quando em ambiente de desenvolvimento local, use app.run()
    # Para deployment, o Gunicorn ou outro servidor WSGI chamará o 'app' diretamente.
    app.run(debug=True, host='0.0.0.0') # host='0.0.0.0' para ser acessível externamente em alguns setups