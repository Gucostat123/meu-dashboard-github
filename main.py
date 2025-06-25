# main.py

import time
import os
import pandas as pd

# Importa as configura��es
from config import CAMPAIGN_SETTINGS, FILE_SETTINGS, EMAIL_CREDENTIALS, EMAIL_CONTENT, DESIGN_CONFIG, EMAIL_SUBJECTS

# Importa a fun��o de envio de email
from email_utils import send_email

print("?? CARREGANDO SISTEMA DE EMAIL MARKETING PROFISSIONAL...")
print("================================================================================")

# ============================================================================
# INFORMA��ES GERAIS E VERIFICA��O DE ARQUIVOS
# ============================================================================
print(f"? Email configurado: {EMAIL_CREDENTIALS['SENDER_EMAIL']}")
print(f"? Empresa: {EMAIL_CREDENTIALS['COMPANY_NAME']}")
print(f"? M�ximo por lote: {CAMPAIGN_SETTINGS['MAX_EMAILS_PER_BATCH']} emails")
print(f"? Delay entre emails: {CAMPAIGN_SETTINGS['DELAY_BETWEEN_EMAILS']} segundos")
print(f"? Formato HTML: {'Ativo' if CAMPAIGN_SETTINGS['ENABLE_HTML'] else 'Desativo'}")

print("\n?? Verificando caminhos de arquivos e carregando contatos...")

# Carrega contatos do arquivo Excel
contacts_file_path = FILE_SETTINGS["CONTACTS_FILE"]
CONTACTS_DATABASE = []

if os.path.exists(contacts_file_path):
    print(f"? Arquivo de contatos encontrado: {contacts_file_path}")
    try:
        df = pd.read_excel(contacts_file_path, engine='openpyxl')
        CONTACTS_DATABASE = df.to_dict(orient='records')
        print(f"? Total de contatos carregados do Excel: {len(CONTACTS_DATABASE)}")
    except FileNotFoundError:
        print(f"? ERRO: O arquivo de contatos '{contacts_file_path}' n�o foi encontrado.")
        print("Por favor, verifique o caminho e o nome do arquivo em config.py.")
    except Exception as e:
        print(f"? ERRO ao ler o arquivo de contatos Excel: {e}")
        print("Certifique-se de que o arquivo est� fechado, no formato correto e as colunas est�o como esperado (Nome, Email, Assunto Personalizado, etc.).")
else:
    print(f"? ERRO: Arquivo de contatos n�o encontrado: {contacts_file_path}")
    print("Por favor, crie 'contatos_campanhas.xlsx' com suas informa��es de contato na pasta correta.")

# Verifica outros arquivos (imagens, etc.)
for key, path in FILE_SETTINGS.items():
    if key not in ["CONTACTS_FILE", "BACKUP_FOLDER", "PROPOSAL_TEMPLATE", "BROCHURE_PATH"]:
        if os.path.exists(path):
            print(f"? Arquivo de imagem encontrado: {key} -> {path}")
        else:
            print(f"?? Arquivo de imagem n�o encontrado: {key} -> {path} (ser� ignorado ou pode causar erro no email se for obrigat�rio)")

print("\n?? Iniciando a campanha de email marketing...")

def run_campaign():
    """
    Executa a campanha de email marketing, enviando emails em lotes.
    """
    selected_contacts = CONTACTS_DATABASE

    successful_sends = 0
    total_contacts = len(selected_contacts)

    if total_contacts == 0:
        print("? NENHUM CONTATO ENCONTRADO/CARREGADO. Campanha encerrada.")
        return

    # Op��o para enviar APENAS UM contato espec�fico do Excel (�til para testes di�rios)
    # Descomente e ajuste a linha abaixo se quiser enviar um email por vez
    # email_para_enviar = "gucostat2468@uni9.edu.br"
    # selected_contacts = [c for c in selected_contacts if c["Email"].lower() == email_para_enviar.lower()]

    if CAMPAIGN_SETTINGS["SEND_CONFIRMATION"]:
        confirmation = input(f"\nConfirma o envio para {total_contacts} contatos encontrados? (s/n): ").lower()
        if confirmation != 's':
            print("?? Envio cancelado pelo usu�rio.")
            return

    print("\n--- IN�CIO DO ENVIO DE EMAILS ---")

    for i, contact in enumerate(selected_contacts):
        print(f"\nProcessando contato {i+1}/{total_contacts}: {contact['Nome']} <{contact['Email']}>")

        if send_email(contact):
            successful_sends += 1

        # Pausa entre emails
        if i < total_contacts - 1:
            print(f"Aguardando {CAMPAIGN_SETTINGS['DELAY_BETWEEN_EMAILS']} segundos antes do pr�ximo email...")
            time.sleep(CAMPAIGN_SETTINGS['DELAY_BETWEEN_EMAILS'])

        # Pausa entre lotes
        if (i + 1) % CAMPAIGN_SETTINGS["MAX_EMAILS_PER_BATCH"] == 0 and (i + 1) < total_contacts:
            print(f"\n--- Lote de {CAMPAIGN_SETTINGS['MAX_EMAILS_PER_BATCH']} emails enviado. ---")
            print(f"Aguardando {CAMPAIGN_SETTINGS['DELAY_BETWEEN_BATCHES']} segundos antes do pr�ximo lote...")
            time.sleep(CAMPAIGN_SETTINGS['DELAY_BETWEEN_BATCHES'])
            print("Retomando o envio...")

    print("\n--- CAMPANHA CONCLU�DA ---")
    print(f"Resumo: {successful_sends} emails enviados com sucesso de {total_contacts} contatos.")
    print("Obrigado por usar o Sistema de Email Marketing Profissional!")

# ============================================================================
# ?? INICIAR O PROGRAMA
# ============================================================================
if __name__ == "__main__":
    run_campaign()
    print("\nPrograma finalizado.")