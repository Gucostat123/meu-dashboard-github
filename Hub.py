# github_repo_info.py

import requests
import json
import pandas as pd
import math # Para cálculo de paginação

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES DA API [EDITÁVEL - OBRIGATÓRIO]
# ============================================================================

GITHUB_API_BASE_URL = "https://api.github.com"

# 👤 Nome de usuário do GitHub para buscar os repositórios
GITHUB_USERNAME = "google" # ✏️ SUBSTITUA PELO NOME DE USUÁRIO (ex: "microsoft", "torvalds")

# 🔑 SEU TOKEN DE ACESSO PESSOAL DO GITHUB (PAT)
# Gere em: github.com -> Settings -> Developer settings -> Personal access tokens (classic)
# Marque o escopo 'repo' para este exercício para garantir acesso completo.
GITHUB_TOKEN = "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" # ✏️ SUBSTITUA POR SEU TOKEN REAL

# Número de itens por página na API (máximo permitido pelo GitHub é 100)
PER_PAGE = 100

# ============================================================================
# ⚙️ PASSO 2: FUNÇÃO PARA OBTER TODOS OS REPOSITÓRIOS (COM PAGINAÇÃO)
# ============================================================================

def get_all_user_repositories(username, token=None):
    """
    Busca TODAS as informações sobre os repositórios públicos de um usuário do GitHub,
    lidando com paginação.
    Retorna uma lista de dicionários com os dados dos repositórios.
    """
    all_repos_data = []
    page = 1
    total_pages = 1 # Inicia com 1, será atualizado pela primeira requisição

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    if token:
        headers["Authorization"] = f"token {token}"
        print("Usando Token de Acesso Pessoal para autenticação...")
    else:
        print("Fazendo requisição sem autenticação (sujeito a limites de taxa muito baixos)...")

    print(f"Buscando todos os repositórios de: {username}...")

    while page <= total_pages:
        repos_url = f"{GITHUB_API_BASE_URL}/users/{username}/repos?per_page={PER_PAGE}&page={page}"
        print(f"  -> Buscando página {page}/{total_pages}...")

        try:
            response = requests.get(repos_url, headers=headers)
            response.raise_for_status() # Lança exceção para status de erro

            repos_page_data = response.json()
            all_repos_data.extend(repos_page_data) # Adiciona os repos da página atual

            # Lidar com paginação: O GitHub usa cabeçalhos 'Link' ou 'x-total-count'
            # A forma mais robusta é usar o cabeçalho 'Link', mas para simplicidade
            # e para pegar o total, vamos tentar obter o total de repos diretamente se possível.
            # Alternativamente, podemos parar quando uma página vier vazia.

            # O GitHub não retorna o 'total_count' diretamente para /users/{user}/repos.
            # O jeito mais comum é iterar até a resposta vir vazia ou usar o cabeçalho 'Link'.
            # Para este exemplo, vamos iterar até a página vir vazia.
            if not repos_page_data:
                break # Se a página veio vazia, não há mais repositórios

            # Se esta for a primeira requisição, tente estimar o total de páginas
            if page == 1:
                # GitHub tipicamente envia um header 'Link' com links para 'next', 'last' page
                # Ou podemos assumir que o 'x-ratelimit-remaining' e 'x-ratelimit-reset' podem dar dicas
                # Mas para um usuário com muitos repos, apenas continuar até a lista vir vazia é comum.
                # Se o usuário tem mais de PER_PAGE repos, 'total_pages' será mais de 1.
                # Uma estimativa simples para exibição, pode não ser o total exato:
                # Se a primeira página já veio completa (PER_PAGE), assume que pode haver mais.
                if len(repos_page_data) == PER_PAGE:
                    # Não temos o total_count, então vamos iterar até não vir mais nada.
                    # Definimos total_pages como um número grande para continuar o loop,
                    # e o 'break' acima vai parar quando a resposta for vazia.
                    total_pages = math.inf # Número infinito para garantir que o loop continue
                else:
                    total_pages = page # Não há mais páginas se a primeira já não veio cheia

            page += 1

        except requests.exceptions.HTTPError as http_err:
            print(f"Erro HTTP ao buscar repositórios (página {page}): {http_err}")
            if response.status_code == 403:
                print("  -> Limite de taxa (Rate Limit) excedido. Verifique seu token ou espere.")
                if 'x-ratelimit-reset' in response.headers:
                    reset_time = datetime.fromtimestamp(int(response.headers['x-ratelimit-reset']))
                    print(f"  -> Limite reiniciará em: {reset_time}")
            elif response.status_code == 404:
                print(f"  -> Usuário '{username}' não encontrado.")
            return None
        except requests.exceptions.RequestException as req_err:
            print(f"Um erro inesperado ocorreu na página {page}: {req_err}")
            return None
    print(f"Busca completa. Total de repositórios encontrados: {len(all_repos_data)}")
    return all_repos_data

# ============================================================================
# 📊 PASSO 3: FUNÇÃO PARA PROCESSAR E EXIBIR DADOS (RESUMO)
# ============================================================================

def process_and_display_repos_summary(repos, username):
    """Processa e exibe um resumo das informações dos repositórios."""
    print(f"\n--- RESUMO DOS REPOSITÓRIOS DE {username.upper()} ---")
    processed_repos_list = []
    for repo in repos:
        name = repo.get("name", "N/A")
        description = repo.get("description", "Sem descrição")
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        last_updated = repo.get("updated_at", "N/A")
        language = repo.get("language", "N/A")
        html_url = repo.get("html_url", "N/A")

        # Exibe apenas um resumo no terminal
        print(f"- {name} (⭐ {stars} / 🍴 {forks}) - {language} - Última: {last_updated}")

        # Adiciona para a lista a ser salva
        processed_repos_list.append({
            "Nome": name,
            "Descricao": description,
            "Estrelas": stars,
            "Forks": forks,
            "Ultima_Atualizacao": last_updated,
            "Linguagem_Principal": language,
            "URL": html_url
        })
    print("-----------------------------------")
    return processed_repos_list

# ============================================================================
# 💾 PASSO 4: FUNÇÃO PARA SALVAR DADOS EM CSV
# ============================================================================

def save_repos_to_csv(repos_data, filename="github_repos.csv"):
    """
    Salva uma lista de dicionários de repositórios em um arquivo CSV.
    """
    if not repos_data:
        print("Não há dados de repositórios para salvar.")
        return

    try:
        df = pd.DataFrame(repos_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Dados salvos com sucesso em '{filename}' na pasta do projeto!")
    except Exception as e:
        print(f"❌ Erro ao salvar os dados em CSV: {e}")

# ============================================================================
# 🚀 PASSO 5: EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    if not GITHUB_USERNAME:
        print("❌ ERRO: Por favor, defina um GITHUB_USERNAME no código.")
    else:
        # Tenta obter os repositórios, passando o token
        if GITHUB_TOKEN == "SEU_TOKEN_DE_ACESSO_PESSOAL_AQUI" or not GITHUB_TOKEN:
            print("\n⚠️ AVISO: GITHUB_TOKEN não configurado. Recomenda-se usar um token para evitar limites de taxa!")
            all_repos = get_all_user_repositories(GITHUB_USERNAME) # Sem token
        else:
            all_repos = get_all_user_repositories(GITHUB_USERNAME, GITHUB_TOKEN) # Com token

        if all_repos:
            # Processa e exibe um resumo dos repositórios
            processed_data_for_csv = process_and_display_repos_summary(all_repos, GITHUB_USERNAME)

            # Pergunta se o usuário quer salvar em CSV
            save_option = input("\nDeseja salvar todos os dados em um arquivo CSV? (s/n): ").lower()
            if save_option == 's':
                save_repos_to_csv(processed_data_for_csv)
            else:
                print("Dados não foram salvos em CSV.")
        else:
            print("Não foi possível obter os repositórios. Verifique as mensagens de erro acima.")