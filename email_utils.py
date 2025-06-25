# email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os
import base64
import random
from datetime import datetime

# Importa as configurações do arquivo config.py
from config import EMAIL_CREDENTIALS, CAMPAIGN_SETTINGS, FILE_SETTINGS, DESIGN_CONFIG, EMAIL_CONTENT, EMAIL_SUBJECTS

def attach_file(msg, filepath):
    """Anexa um arquivo ao email."""
    if os.path.exists(filepath):
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)
        print(f"   -> Anexado: {filename}")
    else:
        print(f"   -> ERRO: Arquivo não encontrado para anexar: {filepath}")

def embed_image(msg, filepath, cid):
    """Incorpora uma imagem no email HTML."""
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', f'<{cid}>')
            msg.attach(img)
        print(f"   -> Imagem incorporada: {os.path.basename(filepath)} (CID: {cid})")
        return f"cid:{cid}"
    else:
        print(f"   -> ERRO: Imagem não encontrada para incorporar: {filepath}")
        return ""

def get_random_element(list_of_elements):
    """Retorna um elemento aleatório de uma lista."""
    if list_of_elements:
        return random.choice(list_of_elements)
    return ""

def generate_html_template():
    """Gera o template HTML profissional com todas as configurações."""
    css_styles = f"""
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: {DESIGN_CONFIG['FONT_FAMILY']};
            background: linear-gradient(135deg, {DESIGN_CONFIG['PRIMARY_COLOR']} 0%, {DESIGN_CONFIG['SECONDARY_COLOR']} 100%);
            padding: 20px;
        }}
        .email-container {{
            max-width: {DESIGN_CONFIG['EMAIL_WIDTH']};
            margin: 0 auto;
            background: {DESIGN_CONFIG['BACKGROUND_COLOR']};
            border-radius: {DESIGN_CONFIG['BORDER_RADIUS']};
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        .header {{
            background: linear-gradient(135deg, {DESIGN_CONFIG['PRIMARY_COLOR']} 0%, {DESIGN_CONFIG['SECONDARY_COLOR']} 100%);
            padding: {DESIGN_CONFIG['PADDING']};
            text-align: center;
            color: white;
        }}
        .logo {{
            max-width: {DESIGN_CONFIG['LOGO_MAX_WIDTH']};
            height: auto;
            margin-bottom: 20px;
            border-radius: 10px;
        }}
        .header h1 {{
            font-size: {DESIGN_CONFIG['TITLE_SIZE']};
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: {DESIGN_CONFIG['TEXT_SIZE']};
            opacity: 0.9;
        }}
        .content {{
            padding: {DESIGN_CONFIG['PADDING']};
        }}
        .greeting {{
            font-size: 24px;
            color: {DESIGN_CONFIG['TEXT_COLOR']};
            margin-bottom: 20px;
        }}
        .highlight {{
            color: {DESIGN_CONFIG['PRIMARY_COLOR']};
            font-weight: bold;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h3 {{
            color: {DESIGN_CONFIG['TEXT_COLOR']};
            font-size: 20px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, {DESIGN_CONFIG['PRIMARY_COLOR']} 0%, {DESIGN_CONFIG['SECONDARY_COLOR']} 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin: 20px 0;
            transition: transform 0.3s ease;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }}
        .cta-button:hover {{
            transform: translateY(-2px);
        }}
        .benefits {{
            background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%);
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
        }}
        .benefits ul {{
            list-style: none;
        }}
        .benefits li {{
            padding: 10px 0;
            position: relative;
            padding-left: 30px;
            font-size: {DESIGN_CONFIG['TEXT_SIZE']};
        }}
        .benefits li:before {{
            content: "?";
            position: absolute;
            left: 0;
            font-size: 18px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            background: linear-gradient(135deg, {DESIGN_CONFIG['PRIMARY_COLOR']} 0%, {DESIGN_CONFIG['SECONDARY_COLOR']} 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: {DESIGN_CONFIG['SMALL_TEXT_SIZE']};
            opacity: 0.9;
        }}
        .offer-box {{
            background: linear-gradient(135deg, {DESIGN_CONFIG['ACCENT_COLOR']} 0%, {DESIGN_CONFIG['PRIMARY_COLOR']} 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin: 25px 0;
            text-align: center;
        }}
        .offer-box h3 {{
            color: white;
            margin-bottom: 15px;
            font-size: 22px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: {DESIGN_CONFIG['PADDING']};
            text-align: center;
        }}
        .footer-info {{
            font-size: {DESIGN_CONFIG['SMALL_TEXT_SIZE']};
            color: #666;
            line-height: 1.8;
        }}
        .social-links {{
            margin: 20px 0;
        }}
        .social-links a {{
            display: inline-block;
            margin: 0 10px;
            padding: 12px;
            background: {DESIGN_CONFIG['PRIMARY_COLOR']};
            color: white;
            border-radius: 50%;
            text-decoration: none;
            width: 45px;
            height: 45px;
            line-height: 21px;
            text-align: center;
            font-weight: bold;
        }}
        .tracking-pixel {{
            width: 1px;
            height: 1px;
        }}
        .personalized-section {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 5px solid {DESIGN_CONFIG['PRIMARY_COLOR']};
        }}
        @media (max-width: 600px) {{
            .email-container {{ margin: 10px; }}
            .header, .content, .footer {{ padding: 20px; }}
            .stats {{ flex-direction: column; gap: 15px; }}
            .stat {{ margin-bottom: 10px; }}
        }}
    </style>
    """

    # HTML Template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{email_title}}</title>
        {css_styles}
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                {{logo_section}}
                <h1>{{company_name}}</h1>
                <p>{{company_slogan}}</p>
            </div>

            <div class="content">
                <div class="greeting">
                    Olá, <span class="highlight">{{nome}}</span>! ??
                </div>

                <div class="personalized-section">
                    <p>É um prazer entrar em contato com você! Vejo que você é <strong>{{cargo}}</strong> na <strong>{{empresa}}</strong> em {{cidade}}, e acredito que nossa solução pode transformar os resultados da sua empresa no setor de <strong>{{setor}}</strong>.</p>
                </div>

                <div class="section">
                    <h2 style="text-align: center; color: {DESIGN_CONFIG['PRIMARY_COLOR']}; font-size: 26px;">
                        {{main_title}}
                    </h2>
                </div>

                <div class="section">
                    <h3>?? Por que escolher a {{company_name}}?</h3>
                    <div class="benefits">
                        <ul>
                            {{benefits_list}}
                        </ul>
                    </div>
                </div>

                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{{clients_served}}</div>
                        <div class="stat-label">Clientes Atendidos</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{{success_rate}}</div>
                        <div class="stat-label">Taxa de Sucesso</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{{average_roi}}</div>
                        <div class="stat-label">ROI Médio</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{{implementation_time}}</div>
                        <div class="stat-label">Tempo de Implementação</div>
                    </div>
                </div>

                <div class="offer-box">
                    <h3>?? Oferta Exclusiva para {{empresa}}</h3>
                    <p>Como você demonstra interesse em <strong>{{interesse}}</strong>, preparamos uma proposta especial:</p>
                    <div style="margin: 20px 0;">
                        {{special_offers}}
                    </div>
                </div>

                <div class="section">
                    <h3>?? Solução Personalizada para {{setor}}</h3>
                    <p>{{value_proposition}}</p>
                    <p>Especificamente para empresas como a <strong>{{empresa}}</strong>, nossa solução pode:</p>
                    <ul style="padding-left: 20px; margin: 15px 0;">
                        <li>?? Aumentar a eficiência operacional em até 300%</li>
                        <li>?? Reduzir custos operacionais em até 40%</li>
                        <li>?? Melhorar a precisão dos processos em 95%</li>
                        <li>? Acelerar a tomada de decisões em 70%</li>
                        <li>?? Automatizar 80% das tarefas repetitivas</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 40px 0;">
                    <a href="{{website}}?utm_source=email&utm_campaign=contato&utm_content={{nome}}&utm_term={{interesse}}" class="cta-button">
                        ?? Agendar Consultoria Gratuita
                    </a>
                    <p style="margin-top: 15px; font-size: 14px; color: #666;">
                        Clique aqui para agendar uma conversa de 30 minutos sem compromisso
                    </p>
                </div>

                <div class="section" style="text-align: center; background: #fff3cd; padding: 20px; border-radius: 10px; border: 2px dashed #ffc107;">
                    <h3 style="color: #856404;">? Oferta por Tempo Limitado!</h3>
                    <p style="color: #856404; font-weight: bold;">Esta proposta é válida apenas até o final do mês. Não perca essa oportunidade!</p>
                </div>

                <div class="section" style="background: #f8f9fa; padding: 20px; border-radius: 10px; font-style: italic; text-align: center;">
                    <p>"A {{company_name}} transformou completamente nossa operação. Em 3 meses, aumentamos nossa produtividade em 250% e reduzimos custos em 35%."</p>
                    <p style="margin-top: 10px; font-weight: bold;">- Cliente Satisfeito, Setor de {{setor}}</p>
                </div>

                <div class="section">
                    <h3>?? Vamos Conversar?</h3>
                    <p>{{nome}}, estou à disposição para uma conversa rápida sobre como podemos ajudar a {{empresa}}. Responda este email ou me chame no WhatsApp!</p>
                    <p style="margin-top: 15px;">
                        <a href="https://wa.me/{{whatsapp_number}}" style="color: {DESIGN_CONFIG['PRIMARY_COLOR']}; text-decoration: none; font-weight: bold;">
                            ?? Chamar no WhatsApp: {{phone}}
                        </a>
                    </p>
                </div>

                {{product_image_section}}

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{{website}}" class="cta-button" style="background: {DESIGN_CONFIG['ACCENT_COLOR']};">
                        ?? Visitar Nosso Site
                    </a>
                </div>

            </div>

            <div class="footer">
                <div class="social-links">
                    {{social_links}}
                </div>
                <p class="footer-info">
                    © {{current_year}} {{company_name}}. Todos os direitos reservados.
                    <br>
                    {{address}} | Telefone: {{phone}} | Site: <a href="{{website}}" style="color: #666; text-decoration: underline;">{{website}}</a>
                    <br>
                    Você recebeu este email porque faz parte da nossa base de contatos ou manifestou interesse em nossos serviços.
                    <br>
                    Se não deseja mais receber nossos emails, por favor, <a href="#" style="color: #666; text-decoration: underline;">clique aqui para descadastrar.</a>
                </p>
            </div>

            {{tracking_pixel_section}}
        </div>
    </body>
    </html>
    """
    return html_template

def send_email(contact):
    """
    Envia um email personalizado para o contato fornecido.
    O assunto é pego diretamente da chave 'Assunto Personalizado' do dicionário contact.
    """
    sender_email = EMAIL_CREDENTIALS["SENDER_EMAIL"]
    sender_password = EMAIL_CREDENTIALS["SENDER_PASSWORD"]
    sender_name = EMAIL_CREDENTIALS["SENDER_NAME"]

    receiver_email = contact["Email"]
    receiver_name = contact["Nome"]

    # 1. Preparar o Assunto do Email (AGORA É DINÂMICO DO EXCEL!)
    subject = contact.get("Assunto Personalizado", f"Olá {receiver_name} - Contato da {EMAIL_CREDENTIALS['COMPANY_NAME']}").strip()

    # 2. Criar a Mensagem
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # 3. Gerar o Conteúdo
    if CAMPAIGN_SETTINGS["ENABLE_HTML"]:
        # Personalização de conteúdo dinâmico
        main_title = get_random_element(EMAIL_CONTENT["MAIN_TITLES"])
        value_proposition = get_random_element(EMAIL_CONTENT["VALUE_PROPOSITIONS"])
        special_offer = get_random_element(EMAIL_CONTENT["SPECIAL_OFFERS"])
        benefits_html = "".join([f"<li>{benefit}</li>" for benefit in EMAIL_CONTENT["MAIN_BENEFITS"]])

        # Seções opcionais (logo, imagem de produto, social links, tracking pixel)
        logo_section = ""
        if CAMPAIGN_SETTINGS["ATTACH_LOGO"] and os.path.exists(FILE_SETTINGS["LOGO_PATH"]):
            logo_cid = "logo_cid_" + base64.urlsafe_b64encode(FILE_SETTINGS["LOGO_PATH"].encode()).decode().replace('=', '')[:10]
            logo_section = f'<img src="cid:{logo_cid}" alt="{EMAIL_CREDENTIALS["COMPANY_NAME"]} Logo" class="logo">'
            embed_image(msg, FILE_SETTINGS["LOGO_PATH"], logo_cid)
        elif CAMPAIGN_SETTINGS["ATTACH_LOGO"] and not os.path.exists(FILE_SETTINGS["LOGO_PATH"]):
            print(f"   ?? Aviso: LOGO_PATH '{FILE_SETTINGS['LOGO_PATH']}' não encontrado. Logo não será incorporada.")


        product_image_section = ""
        if CAMPAIGN_SETTINGS["ENABLE_IMAGES"] and os.path.exists(FILE_SETTINGS["PRODUCT_IMAGE"]):
            product_cid = "product_cid_" + base64.urlsafe_b64encode(FILE_SETTINGS["PRODUCT_IMAGE"].encode()).decode().replace('=', '')[:10]
            product_image_section = f'''
            <div class="section" style="text-align: center; margin: 30px 0;">
                <img src="cid:{product_cid}" alt="Imagem do Produto" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);">
                <p style="margin-top: 15px; font-size: 14px; color: #666;">
                    Conheça mais sobre nossa solução em {EMAIL_CREDENTIALS['WEBSITE']}
                </p>
            </div>
            '''
            embed_image(msg, FILE_SETTINGS["PRODUCT_IMAGE"], product_cid)
        elif CAMPAIGN_SETTINGS["ENABLE_IMAGES"] and not os.path.exists(FILE_SETTINGS["PRODUCT_IMAGE"]):
            print(f"   ?? Aviso: PRODUCT_IMAGE '{FILE_SETTINGS['PRODUCT_IMAGE']}' não encontrado. Imagem do produto não será incorporada.")


        social_links_html = ""
        if EMAIL_CREDENTIALS.get("LINKEDIN"):
            social_links_html += f'<a href="{EMAIL_CREDENTIALS["LINKEDIN"]}" target="_blank" style="font-size: 24px; color: white;">in</a>'
        if EMAIL_CREDENTIALS.get("INSTAGRAM"):
            social_links_html += f'<a href="{EMAIL_CREDENTIALS["INSTAGRAM"]}" target="_blank" style="font-size: 24px; color: white;">ig</a>'
        if EMAIL_CREDENTIALS.get("WHATSAPP"):
             social_links_html += f'<a href="https://wa.me/{EMAIL_CREDENTIALS["WHATSAPP"]}" target="_blank" style="font-size: 24px; color: white;">wa</a>'

        tracking_pixel_section = ""
        if CAMPAIGN_SETTINGS["ENABLE_TRACKING"]:
            tracking_pixel_section = f'<img src="https://www.google-analytics.com/collect?v=1&tid=UA-XXXXX-Y&cid={receiver_email}&t=event&ec=email&ea=open&el={subject}&cs=email&cm=campaign&cn={datetime.now().strftime("%Y%m%d")}" class="tracking-pixel" alt="">'


        html_content = html_template.format(
            email_title=subject,
            nome=receiver_name,
            empresa=contact.get("Empresa", "sua empresa"),
            cargo=contact.get("Cargo", "nosso valioso contato"),
            cidade=contact.get("Cidade", "sua cidade"),
            setor=contact.get("Setor", "seu setor"),
            interesse=contact.get("Interesse", "nossas soluções"),
            main_title=main_title,
            value_proposition=value_proposition,
            special_offers=special_offer,
            benefits_list=benefits_html,
            company_name=EMAIL_CREDENTIALS["COMPANY_NAME"],
            company_slogan=EMAIL_CREDENTIALS["COMPANY_SLOGAN"],
            website=EMAIL_CREDENTIALS["WEBSITE"],
            phone=EMAIL_CREDENTIALS["PHONE"],
            address=EMAIL_CREDENTIALS["ADDRESS"],
            current_year=datetime.now().year,
            whatsapp_number=EMAIL_CREDENTIALS["WHATSAPP"],
            clients_served=EMAIL_CONTENT["STATISTICS"]["clients_served"],
            success_rate=EMAIL_CONTENT["STATISTICS"]["success_rate"],
            average_roi=EMAIL_CONTENT["STATISTICS"]["average_roi"],
            implementation_time=EMAIL_CONTENT["STATISTICS"]["implementation_time"],
            logo_section=logo_section,
            product_image_section=product_image_section,
            social_links=social_links_html,
            tracking_pixel_section=tracking_pixel_section
        )
        part2 = MIMEText(html_content, "html")
        msg.attach(part2)
    else:
        text_content = f"""
Olá, {receiver_name}!

Espero que este email o encontre bem.

Meu nome é {sender_name} da {EMAIL_CREDENTIALS['COMPANY_NAME']}, e estamos focados em {EMAIL_CREDENTIALS['COMPANY_SLOGAN']}.

Gostaria de apresentar como nossa solução pode ajudar a {contact.get('Empresa', 'sua empresa')} a {get_random_element(EMAIL_CONTENT['VALUE_PROPOSITIONS'])}.

Para mais informações, visite nosso site: {EMAIL_CREDENTIALS['WEBSITE']}

Ou agende uma consultoria gratuita: {EMAIL_CREDENTIALS['WEBSITE']}?utm_source=email&utm_campaign=contato&utm_content={receiver_name}

Atenciosamente,

{sender_name}
{EMAIL_CREDENTIALS['COMPANY_NAME']}
Telefone: {EMAIL_CREDENTIALS['PHONE']}
"""
        part1 = MIMEText(text_content, "plain")
        msg.attach(part1)

    # 4. Anexar arquivos
    if CAMPAIGN_SETTINGS["ATTACH_BROCHURE"]:
        attach_file(msg, FILE_SETTINGS["BROCHURE_PATH"])

    # 5. Enviar o Email
    try:
        print(f"   -> Tentando conectar a {EMAIL_CREDENTIALS['SMTP_SERVER']}:{EMAIL_CREDENTIALS['SMTP_PORT']}...")
        with smtplib.SMTP(EMAIL_CREDENTIALS["SMTP_SERVER"], EMAIL_CREDENTIALS["SMTP_PORT"]) as server:
            server.set_debuglevel(1)
            print("   -> Conexão estabelecida. Iniciando TLS...")
            server.starttls()
            print("   -> TLS iniciado. Tentando fazer login...")
            server.login(sender_email, sender_password)
            print("   ? Login bem-sucedido. Enviando email...")
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"   ? Email enviado para: {receiver_email} (Assunto: {subject})")
        return True
    except smtplib.SMTPAuthenticationError as auth_err:
        print(f"   ? ERRO DE AUTENTICAÇÃO para {receiver_email}: {auth_err}")
        print("      -> Verifique sua senha de aplicativo do Gmail.")
        print("      -> Certifique-se de que a verificação em duas etapas está ATIVADA na sua conta Google.")
        print("      -> Tente gerar uma NOVA senha de aplicativo.")
        return False
    except smtplib.SMTPConnectError as conn_err:
        print(f"   ? ERRO DE CONEXÃO SMTP para {receiver_email}: {conn_err}")
        print("      -> Verifique sua conexão com a internet.")
        print("      -> Verifique as configurações de SMTP_SERVER e SMTP_PORT em config.py.")
        print("      -> Seu firewall pode estar bloqueando a conexão.")
        return False
    except Exception as e:
        print(f"   ? ERRO GERAL ao enviar email para {receiver_email}: {e}")
        return False