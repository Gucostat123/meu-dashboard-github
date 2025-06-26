# sentiment_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import torch
from transformers import pipeline

# ============================================================================
# 🎯 PASSO 1: CONFIGURAÇÕES DO DASHBOARD [EDITÁVEL]
# ============================================================================

st.set_page_config(layout="centered", page_title="Analisador de Sentimento de Texto (Granular)")

# Nome do modelo de sentimento da Hugging Face
SENTIMENT_MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"

# Chave de API da Hugging Face (para download do modelo, se necessário)
# Lida da variável de ambiente HF_API_TOKEN_ENV
HF_API_TOKEN = os.environ.get("HF_API_TOKEN_ENV") 

# ============================================================================
# ⚙️ PASSO 2: PREPARAÇÃO DO MODELO DE SENTIMENTO (TRANSFORMERS)
# ============================================================================

@st.cache_resource # Cacheia o modelo para que não seja carregado a cada interação
def load_sentiment_pipeline():
    """Carrega o pipeline de análise de sentimento da Hugging Face."""
    if not HF_API_TOKEN:
        st.error("❌ ERRO: Variável de ambiente 'HF_API_TOKEN_ENV' não configurada.")
        st.info("Por favor, defina seu token Hugging Face antes de rodar o Streamlit.")
        st.stop() # Para o aplicativo Streamlit

    try:
        with st.spinner(f'Carregando modelo de sentimento "{SENTIMENT_MODEL_NAME}" (primeira vez, pode levar alguns minutos e MBs)...'):
            sentiment_pipeline = pipeline("sentiment-analysis", model=SENTIMENT_MODEL_NAME, tokenizer=SENTIMENT_MODEL_NAME, device=-1, token=HF_API_TOKEN)
        st.success("Modelo de sentimento carregado com sucesso!")
        return sentiment_pipeline
    except Exception as e:
        st.error(f"❌ ERRO ao carregar o modelo de sentimento: {e}")
        st.info("Verifique sua conexão, espaço em disco e as dependências (transformers, torch/tensorflow).")
        st.info("Certifique-se de que seu token Hugging Face está correto e tem permissão para baixar este modelo.")
        st.stop()

analyzer_pipeline = load_sentiment_pipeline()

# ============================================================================
# 🚀 PASSO 3: FUNÇÃO DE ANÁLISE E EXIBIÇÃO GRANULAR
# ============================================================================

def analyze_and_display_granular_sentiment(text, pipeline_model, thresholds):
    """
    Analisa e exibe o sentimento de forma mais granular com base em thresholds customizáveis.
    """
    raw_sentiment_result = pipeline_model(text)
    sentiment_info = raw_sentiment_result[0] # Ex: {'label': '5 stars', 'score': 0.999}
    
    label_raw = sentiment_info['label']
    score = sentiment_info['score']

    # Mapeamento para um score numérico de 0 a 1 (ou -1 a 1) para o termômetro
    # O modelo NLPTown usa 1-5 estrelas. Vamos converter para uma escala de -1 a 1.
    star_rating = int(label_raw.split(' ')[0]) # Pega o número da estrela (ex: 5 de '5 stars')
    
    # Mapeamento de 1-5 estrelas para -1 a 1:
    # 1 estrela -> -1.0 (muito negativo)
    # 2 estrelas -> -0.5 (negativo)
    # 3 estrelas -> 0.0 (neutro)
    # 4 estrelas -> 0.5 (positivo)
    # 5 estrelas -> 1.0 (muito positivo)
    sentiment_value = (star_rating - 3) / 2.0 

    # --- Classificação Granular ---
    main_sentiment_desc = "Desconhecido"
    emoji = "❓"
    
    # Usando os thresholds customizáveis
    if sentiment_value <= thresholds['muito_negativo']:
        main_sentiment_desc = "Muito Negativo"
        emoji = "😡"
        # color_box = "darkred" # Streamlit não usa color_box diretamente para subheader
    elif sentiment_value <= thresholds['negativo']:
        main_sentiment_desc = "Negativo"
        emoji = "😠"
        # color_box = "red"
    elif sentiment_value <= thresholds['levemente_negativo']:
        main_sentiment_desc = "Levemente Negativo"
        emoji = "😞"
        # color_box = "orange"
    elif sentiment_value >= thresholds['muito_positivo']:
        main_sentiment_desc = "Muito Positivo"
        emoji = "🤩"
        # color_box = "green"
    elif sentiment_value >= thresholds['positivo']:
        main_sentiment_desc = "Positivo"
        emoji = "😊"
        # color_box = "lightgreen"
    elif sentiment_value >= thresholds['levemente_positivo']:
        main_sentiment_desc = "Levemente Positivo"
        emoji = "🙂"
        # color_box = "lightgray"
    else: # Entre levemente positivo e levemente negativo
        main_sentiment_desc = "Neutro"
        emoji = "😐"
        # color_box = "gray"

    st.subheader(f"Sentimento Geral: **{main_sentiment_desc}** {emoji}")
    st.markdown(f"**Confiança do Modelo (para {star_rating} estrelas):** `{score:.2f}`")
    st.markdown(f"**Score Interno do Modelo (Escala -1 a 1):** `{sentiment_value:.2f}`")

    # --- Termômetro de Interpretação ---
    st.subheader("Termômetro de Sentimento")
    # Usa st.progress para criar um termômetro de -1 a 1
    # Normaliza o valor para uma barra de 0 a 100%
    progress_value = (sentiment_value + 1) / 2 # Converte escala -1 a 1 para 0 a 1
    st.progress(progress_value)

    st.write(f"") # Espaçamento
    col_temp1, col_temp2, col_temp3 = st.columns(3)
    col_temp1.write("😡 Muito Negativo (-1.0)")
    col_temp2.write("😐 Neutro (0.0)")
    col_temp3.write("🤩 Muito Positivo (1.0)")
    st.write("") # Espaçamento

    # --- Pontuações Detalhadas (para todas as estrelas) ---
    st.subheader("Pontuações Detalhadas por Estrela")
    
    # O modelo retorna apenas o label dominante. Para mostrar todos, podemos simular.
    # Para o gráfico, vamos mostrar a confiança do dominante e os outros como 0
    all_labels_scores = []
    labels_map_for_chart = {
        '1 star': '1 Estrela (Neg.)', '2 stars': '2 Estrelas (Neg.)',
        '3 stars': '3 Estrelas (Neutro)', '4 stars': '4 Estrelas (Pos.)',
        '5 stars': '5 Estrelas (Pos.)'
    }
    
    for label_code_chart in ['1 star', '2 stars', '3 stars', '4 stars', '5 stars']: # Corrigido '4 star', '5 star' para '4 stars', '5 stars'
        current_score_chart = sentiment_info['score'] if label_code_chart == sentiment_info['label'] else 0.0
        all_labels_scores.append({"Estrelas": labels_map_for_chart[label_code_chart], "Confiança": current_score_chart})
    
    scores_df = pd.DataFrame(all_labels_scores)
    
    fig = px.bar(scores_df, 
                 x='Estrelas', 
                 y='Confiança', 
                 title='Confiança do Modelo por Nível de Estrelas',
                 color='Estrelas',
                 color_discrete_map={
                     '1 Estrela (Neg.)': 'darkred', '2 Estrelas (Neg.)': 'red', 
                     '3 Estrelas (Neutro)': 'grey', 
                     '4 Estrelas (Pos.)': 'lightgreen', '5 Estrelas (Pos.)': 'green'
                 })
    fig.update_layout(yaxis_range=[0,1]) # Garante que o eixo Y vá de 0 a 1
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.write("📈 **Como interpretar os Scores de Estrela:**")
    st.write("- O modelo classifica o texto com uma pontuação de 1 a 5 estrelas.")
    st.write("- Um 'Nível de Confiança' alto para 1 estrela indica que o texto é muito negativo.")
    st.write("- Um 'Nível de Confiança' alto para 5 estrelas indica que o texto é muito positivo.")
    st.write("---")

# ============================================================================
# 🚀 PASSO 4: EXECUÇÃO PRINCIPAL DO DASHBOARD
# ============================================================================

if __name__ == '__main__':
    st.title("Analisador de Sentimento de Texto Avançado")
    st.write("Use esta ferramenta para obter uma análise mais rigorosa do sentimento de textos.")

    # --- Configurações Customizáveis (Na Barra Lateral) ---
    st.sidebar.header("⚙️ Configurações de Interpretação")
    st.sidebar.write("Ajuste os limites do termômetro de sentimento (escala -1 a 1, onde 1 estrela = -1.0, 5 estrelas = 1.0).")

    # Sliders para definir os thresholds
    # Recomendo usar valores padrão que façam sentido
    thresholds = {
        'muito_negativo': st.sidebar.slider("Muito Negativo (até -0.6):", -1.0, 0.0, -0.6, 0.05),
        'negativo': st.sidebar.slider("Negativo (até -0.2):", -1.0, 0.0, -0.2, 0.05),
        'levemente_negativo': st.sidebar.slider("Levemente Negativo (até -0.05):", -1.0, 0.0, -0.05, 0.05),
        # Neutro é entre levemente_negativo e levemente_positivo
        'levemente_positivo': st.sidebar.slider("Levemente Positivo (a partir de 0.05):", 0.0, 1.0, 0.05, 0.05),
        'positivo': st.sidebar.slider("Positivo (a partir de 0.2):", 0.0, 1.0, 0.2, 0.05),
        'muito_positivo': st.sidebar.slider("Muito Positivo (a partir de 0.6):", 0.0, 1.0, 0.6, 0.05),
    }

    # Validação para garantir que os thresholds estão em ordem
    # A lógica granular precisa desses limites para funcionar corretamente.
    # A ordem deve ser: muito_negativo < negativo < levemente_negativo < neutro < levemente_positivo < positivo < muito_positivo
    if not (thresholds['muito_negativo'] < thresholds['negativo'] and
            thresholds['negativo'] < thresholds['levemente_negativo'] and
            thresholds['levemente_negativo'] < thresholds['levemente_positivo'] and
            thresholds['levemente_positivo'] < thresholds['positivo'] and
            thresholds['positivo'] < thresholds['muito_positivo']):
        st.sidebar.error("⚠️ Erro: Os limites de sentimento devem estar em ordem crescente.")
        st.stop()


    user_input_text = st.text_area("Cole seu texto aqui:", height=150, help="Ideal para avaliações de clientes, comentários online, etc.")

    if user_input_text:
        if not analyzer_pipeline:
            st.error("O modelo de análise de sentimento não está disponível. Não é possível analisar.")
        else:
            analyze_and_display_granular_sentiment(user_input_text, analyzer_pipeline, thresholds)
    else:
        st.info("Digite um texto acima para ver a análise de sentimento!")