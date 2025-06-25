# data_scheduler.py

import time
import os
import subprocess
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import sys
import logging

# --- Adições para Notificação por E-mail ---
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# --- Fim Adições ---

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES DO AGENDADOR [EDITÁVEL]
# ============================================================================

# Caminho completo para o script que coleta e insere dados no DB
GITHUB_TO_DB_SCRIPT = os.path.join(os.path.dirname(__file__), "github_to_db.py")

# Intervalo de atualização (em horas)
UPDATE_INTERVAL_HOURS = 24 
# Para teste, você pode usar um valor menor (ex: minutes=1)
# UPDATE_INTERVAL_HOURS = 0
# TEST_INTERVAL_MINUTES = 1 # Descomente para testar a cada 1 minuto

# Configurações do arquivo de log
LOG_FILENAME = "scheduler_log.log"
LOG_LEVEL = logging.INFO

# ============================================================================
# ⚙️ PASSO 2: CONFIGURAÇÃO DO LOGGER
# ============================================================================

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ============================================================================
# 🔔 PASSO 3: CONFIGURAÇÕES DE NOTIFICAÇÃO POR E-MAIL [EDITÁVEL - OBRIGATÓRIO]
# ============================================================================
NOTIFICATION_EMAIL_SETTINGS = {
    "SENDER_EMAIL": "gucostat2468@gmail.com",    # ✏️ SEU EMAIL REMETENTE
    "SENDER_PASSWORD": "opjr sghx coul sdyh", # ✏️ SENHA DE APLICATIVO GMAIL
    "RECEIVER_EMAIL": "gucostat2468@gmail.com",    # ✏️ EMAIL PARA ONDE AS NOTIFICAÇÕES SERÃO ENVIADAS
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587
}
# ============================================================================
# ⚙️ PASSO 4: FUNÇÃO PARA ENVIAR NOTIFICAÇÃO POR E-MAIL
# ============================================================================

def send_notification_email(subject, body):
    """Envia um e-mail de notificação usando as configurações."""
    try:
        msg = MIMEMultipart()
        msg['From'] = NOTIFICATION_EMAIL_SETTINGS["SENDER_EMAIL"]
        msg['To'] = NOTIFICATION_EMAIL_SETTINGS["RECEIVER_EMAIL"]
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8')) # Usar utf-8 na codificação do texto

        with smtplib.SMTP(NOTIFICATION_EMAIL_SETTINGS["SMTP_SERVER"], NOTIFICATION_EMAIL_SETTINGS["SMTP_PORT"]) as server:
            server.starttls()
            server.login(NOTIFICATION_EMAIL_SETTINGS["SENDER_EMAIL"], NOTIFICATION_EMAIL_SETTINGS["SENDER_PASSWORD"])
            server.sendmail(NOTIFICATION_EMAIL_SETTINGS["SENDER_EMAIL"], NOTIFICATION_EMAIL_SETTINGS["RECEIVER_EMAIL"], msg.as_string())
        logger.info(f"Notificação por e-mail enviada com sucesso para {NOTIFICATION_EMAIL_SETTINGS['RECEIVER_EMAIL']}.")
    except Exception as e:
        logger.error(f"❌ ERRO ao enviar e-mail de notificação: {e}")

# ============================================================================
# ⚙️ PASSO 5: FUNÇÃO PARA EXECUTAR A TAREFA DE ATUALIZAÇÃO
# ============================================================================

def run_data_update():
    """
    Executa o script 'github_to_db.py' para coletar e atualizar os dados no banco.
    Registra os resultados no arquivo de log e envia notificação em caso de erro.
    """
    logger.info(f"Iniciando a atualização de dados do GitHub...")
    
    try:
        python_executable = sys.executable 
        
        result = subprocess.run(
            [python_executable, GITHUB_TO_DB_SCRIPT], 
            capture_output=True, 
            text=True, 
            check=True,
            encoding='cp1252', # Decodificar saída do subprocesso como CP1252
            errors='replace'   # Substitui caracteres que não puderem ser decodificados
        )
        
        logger.info("--- Saída do github_to_db.py ---")
        if result.stdout:
            logger.info(result.stdout.strip())
        if result.stderr:
            logger.error("--- Erros do github_to_db.py ---")
            logger.error(result.stderr.strip())
        logger.info("--- Fim da Saída ---")
        logger.info("Atualização de dados concluída com sucesso.")
        
    except subprocess.CalledProcessError as e:
        error_message = f"ERRO: O script github_to_db.py falhou com código de saída {e.returncode}."
        logger.error(error_message)
        logger.error(f"Erro de Saída Padrão (stderr):\n{e.stderr.strip()}")
        logger.error(f"Saída Padrão (stdout):\n{e.stdout.strip()}")
        send_notification_email("ALERTA DE ERRO: Atualização de Dados GitHub Falhou!", 
                                f"{error_message}\n\nDetalhes do Erro:\n{e.stderr.strip()}")
    except FileNotFoundError:
        error_message = f"ERRO: Script '{GITHUB_TO_DB_SCRIPT}' não encontrado. Verifique o caminho."
        logger.error(error_message)
        send_notification_email("ALERTA DE ERRO: Script de Coleta Não Encontrado!", error_message)
    except Exception as e:
        error_message = f"ERRO CRÍTICO inesperado ao agendar a atualização: {e}"
        logger.critical(error_message)
        send_notification_email("ALERTA DE ERRO: Falha Crítica no Agendador!", error_message)

# ============================================================================
# 🚀 PASSO 6: CONFIGURAÇÃO E INÍCIO DO AGENDADOR
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Iniciando o Agendador de Atualização de Dados do GitHub...")
    logger.info(f"O script '{GITHUB_TO_DB_SCRIPT}' será executado a cada {UPDATE_INTERVAL_HOURS} horas.")
    logger.info(f"Os logs serão salvos em '{LOG_FILENAME}'.")
    logger.info("Pressione Ctrl+C para parar o agendador.")

    scheduler = BlockingScheduler()

    # Executa uma vez ao iniciar
    logger.info("Executando a primeira atualização agora...")
    run_data_update() 

    # Adiciona a tarefa para rodar em intervalos
    scheduler.add_job(run_data_update, IntervalTrigger(hours=UPDATE_INTERVAL_HOURS))
    # Para testar a cada minuto, descomente a linha abaixo e comente a linha acima:
    # scheduler.add_job(run_data_update, IntervalTrigger(minutes=TEST_INTERVAL_MINUTES))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Agendador parado.")
    except Exception as e:
        logger.critical(f"Erro fatal no agendador principal: {e}")