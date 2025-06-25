# citacao_aleatoria.py

import requests

# ============================================================================
# ?? PASSO 1: CONFIGURA��ES DA API
# ============================================================================

BASE_URL = "https://api.quotable.io/random"

# ============================================================================
# ?? PASSO 2: FUN��O PARA OBTER DADOS DA API
# ============================================================================

def get_random_quote():
    """
    Faz uma requisi��o � API Quotable para obter uma cita��o aleat�ria.
    Retorna os dados em formato JSON se a requisi��o for bem-sucedida.
    """
    print(f"Buscando cita��o aleat�ria em: {BASE_URL}...")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status() # Lan�a uma exce��o para erros HTTP (4xx ou 5xx)
        
        quote_data = response.json()
        print("Cita��o obtida com sucesso!")
        return quote_data
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar a cita��o: {e}")
        print("Verifique sua conex�o com a internet ou o URL da API.")
        return None

# ============================================================================
# ?? PASSO 3: EXECU��O PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    quote_info = get_random_quote()

    if quote_info:
        content = quote_info.get("content", "N/A")
        author = quote_info.get("author", "Desconhecido")
        
        print("\n--- CITA��O ALEAT�RIA ---")
        print(f'"{content}"')
        print(f"- {author}")
        print("-------------------------")
    else:
        print("N�o foi poss�vel obter a cita��o. Verifique as mensagens de erro acima.")