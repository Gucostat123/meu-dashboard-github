# citacao_aleatoria.py

import requests

# ============================================================================
# ?? PASSO 1: CONFIGURAÇÕES DA API
# ============================================================================

BASE_URL = "https://api.quotable.io/random"

# ============================================================================
# ?? PASSO 2: FUNÇÃO PARA OBTER DADOS DA API
# ============================================================================

def get_random_quote():
    """
    Faz uma requisição à API Quotable para obter uma citação aleatória.
    Retorna os dados em formato JSON se a requisição for bem-sucedida.
    """
    print(f"Buscando citação aleatória em: {BASE_URL}...")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status() # Lança uma exceção para erros HTTP (4xx ou 5xx)
        
        quote_data = response.json()
        print("Citação obtida com sucesso!")
        return quote_data
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar a citação: {e}")
        print("Verifique sua conexão com a internet ou o URL da API.")
        return None

# ============================================================================
# ?? PASSO 3: EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    quote_info = get_random_quote()

    if quote_info:
        content = quote_info.get("content", "N/A")
        author = quote_info.get("author", "Desconhecido")
        
        print("\n--- CITAÇÃO ALEATÓRIA ---")
        print(f'"{content}"')
        print(f"- {author}")
        print("-------------------------")
    else:
        print("Não foi possível obter a citação. Verifique as mensagens de erro acima.")