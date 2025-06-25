# config.py

import os
from datetime import datetime

# ============================================================================
# ?? PASSO 1: CONFIGURAÇÕES BÁSICAS [EDITÁVEL - OBRIGATÓRIO]
# ============================================================================
EMAIL_CREDENTIALS = {
    # ?? SUAS CREDENCIAIS (OBRIGATÓRIO EDITAR)
    "SENDER_EMAIL": "gucostat2468@gmail.com",           # ?? COLOQUE SEU EMAIL AQUI
    "SENDER_PASSWORD": "SUA_SENHA_DE_APLICATIVO_AQUI",  # ?? SENHA DE APLICATIVO GMAIL (16 dígitos) - COLOQUE A SENHA QUE FUNCIONOU!
    "SENDER_NAME": "Gustavo Costa",                     # ?? SEU NOME COMPLETO

    # ?? INFORMAÇÕES DA EMPRESA (OBRIGATÓRIO EDITAR)
    "COMPANY_NAME": "Midas Solutions",                  # ?? NOME DA SUA EMPRESA
    "COMPANY_SLOGAN": "Transformando Negócios com IA", # ?? SLOGAN DA EMPRESA
    "PHONE": "(11) 99999-9999",                        # ?? SEU TELEFONE
    "WEBSITE": "https://www.midasolutions.com.br",     # ?? SITE DA EMPRESA
    "ADDRESS": "São Paulo, SP - Brasil",               # ?? ENDEREÇO DA EMPRESA

    # ?? REDES SOCIAIS (OPCIONAL - EDITAR SE QUISER)
    "LINKEDIN": "https://linkedin.com/in/seu-perfil",  # ?? SEU LINKEDIN
    "INSTAGRAM": "https://instagram.com/sua_empresa",  # ?? SEU INSTAGRAM
    "WHATSAPP": "5511999999999",                       # ?? SEU WHATSAPP (com código do país)

    # ?? CONFIGURAÇÕES TÉCNICAS (PODE DEIXAR COMO ESTÁ)
    "SMTP_SERVER": "smtp.gmail.com",                   # Gmail: smtp.gmail.com | Outlook: smtp-mail.outlook.com
    "SMTP_PORT": 587                                   # Gmail: 587 | Outlook: 587
}

# ============================================================================
# ?? PASSO 2: CONFIGURAÇÕES DA CAMPANHA [EDITÁVEL - RECOMENDADO]
# ============================================================================
CAMPAIGN_SETTINGS = {
    "MAX_EMAILS_PER_BATCH": 25,
    "DELAY_BETWEEN_EMAILS": 3,
    "DELAY_BETWEEN_BATCHES": 600,

    # ?? CONFIGURAÇÕES DE DESIGN
    "ENABLE_HTML": True,               # ?? TRUE para usar o template HTML
    "ENABLE_IMAGES": True,             # ?? TRUE para incluir imagens (logo, produto)
    "ENABLE_TRACKING": True,           # ?? TRUE para rastrear abertura

    # ?? CONFIGURAÇÕES DE ANEXOS
    "ATTACH_LOGO": True,               # ?? TRUE para anexar logo (incorporar)
    "ATTACH_BROCHURE": False,          # ?? TRUE para anexar brochure.pdf (se tiver um)

    # ?? CONFIGURAÇÕES AVANÇADAS
    "PERSONALIZE_CONTENT": True,
    "SEND_CONFIRMATION": True
}

# ============================================================================
# ?? PASSO 3: CONFIGURAÇÕES DE ARQUIVOS [EDITÁVEL - OBRIGATÓRIO]
# ============================================================================
FILE_SETTINGS = {
    "LOGO_PATH": "imagens/logo_empresa.png",
    "HEADER_IMAGE": "imagens/header_campaign (1).jpg", # <-- Corrigido!
    "PRODUCT_IMAGE": "imagens/produto_destaque.jpg",   # <-- Corrigido!
    "BROCHURE_PATH": "brochure.pdf",
    "PROPOSAL_TEMPLATE": "proposta.pdf",
    "CONTACTS_FILE": "contatos_campanhas.xlsx",
    "BACKUP_FOLDER": "backup_campanhas"
}

# ============================================================================
# ?? PASSO 5: ASSUNTOS DOS EMAILS [EDITÁVEL - CRIATIVO]
# ============================================================================
EMAIL_SUBJECTS = {
    "ALTA": ["Oportunidade para {empresa}!"],
    "MEDIA": ["Novidades para {empresa}!"],
    "BAIXA": ["Contato comercial - {nome}"]
}

# ============================================================================
# ?? PASSO 6: DESIGN DO EMAIL [EDITÁVEL - VISUAL]
# ============================================================================
DESIGN_CONFIG = {
    "PRIMARY_COLOR": "#667eea",
    "SECONDARY_COLOR": "#764ba2",
    "ACCENT_COLOR": "#f093fb",
    "TEXT_COLOR": "#333333",
    "BACKGROUND_COLOR": "#ffffff",
    "EMAIL_WIDTH": "600px",
    "BORDER_RADIUS": "15px",
    "PADDING": "30px",
    "LOGO_MAX_WIDTH": "180px",
    "IMAGE_QUALITY": "85%",
    "FONT_FAMILY": "'Segoe UI', Arial, sans-serif",
    "TITLE_SIZE": "28px",
    "TEXT_SIZE": "16px",
    "SMALL_TEXT_SIZE": "14px"
}

# ============================================================================
# ?? PASSO 7: CONTEÚDO PERSONALIZADO [EDITÁVEL - CONTEÚDO]
# ============================================================================
EMAIL_CONTENT = {
    "MAIN_TITLES": ["Transforme sua empresa hoje mesmo!", "O futuro do seu negócio começa aqui!"],
    "VALUE_PROPOSITIONS": ["como podemos ajudar seu negócio a crescer.", "aumentar sua produtividade em 300% com nossa solução de IA."],
    "SPECIAL_OFFERS": ["uma consultoria gratuita.", "um desconto de 40% no primeiro projeto."],
    "STATISTICS": {
        "clients_served": "500+",
        "success_rate": "98%",
        "average_roi": "300%",
        "implementation_time": "30 dias",
        "support_hours": "24/7"
    },
    "MAIN_BENEFITS": [
        "Automação completa de processos",
        "Redução de custos operacionais",
        "Aumento da produtividade",
        "Análise de dados em tempo real",
        "Suporte técnico especializado"
    ]
}