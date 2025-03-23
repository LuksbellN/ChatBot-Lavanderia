from flask import Flask, request, session
import json
import re
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.secret_key = os.getenv('FLASK_SECRET_KEY')
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# User states
WELCOME = 'welcome'
MAIN_MENU = 'main_menu'
SERVICE_INFO = 'service_info'
QUOTE_REQUEST = 'quote_request'

# Store user states and data in memory (in production, use a proper database)
user_states = {}
user_data = {}

def send_whatsapp_message(phone_number, message):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

def generate_welcome_message():
    return """
    👋 Olá! Bem-vindo(a) à Lavanderia Lavatudo!
    
    Como posso ajudar você hoje?
    
    🧺 *Menu Principal*
    
    Escolha uma opção:
    1. Horário de atendimento
    2. Tabela de preços
    3. Prazo de entrega
    4. Serviço de busca e entrega
    5. Agendar horário de busca/entrega
    6. Verificar se a roupa está pronta
    7. Como funciona o serviço?
    8. Solicitar orçamento
    9. Lavagem de tênis
    10. Qual o endereço?
    11. Lavagem de vestido de festa/noiva
    12. Faz tingimento?
    13. Lavagem de sofá/tapete
    
    Para voltar ao menu principal, digite *menu* ou *0*.
    """

def generate_menu():
    return """
    🧺 *Menu Principal*
    
    Como posso ajudar você hoje?
    
    Escolha uma opção:
    1. Horário de atendimento
    2. Tabela de preços
    3. Prazo de entrega
    4. Serviço de busca e entrega
    5. Agendar horário de busca/entrega
    6. Verificar se a roupa está pronta
    7. Como funciona o serviço?
    8. Solicitar orçamento
    9. Lavagem de tênis
    10. Qual o endereço?
    11. Lavagem de vestido de festa/noiva
    12. Faz tingimento?
    13. Lavagem de sofá/tapete
    
    Para voltar ao menu principal, digite *menu* ou *0*.
    """

def generate_service_menu():
    return """
    🧺 *Como funciona o serviço?*
    
    Qual tipo de serviço você precisa?
    
    Escolha uma opção:
    1. Roupas do dia a dia
    2. Itens especiais
    3. Enxoval
    
    Para voltar ao menu principal, digite *menu* ou *0*.
    """

def process_service_option(option):
    responses = {
        '1': "Roupas do dia a dia:\n- Serviço por kg\n- Lavagem e secagem\n- Passadoria básica\n- Prazo: 24-48h",
        '2': "Itens especiais:\n- Lavagem individual\n- Tratamento especial\n- Passadoria especial\n- Prazo: 48-72h",
        '3': "Enxoval:\n- Lavagem especial\n- Embalagem individual\n- Prazo: 72-96h"
    }
    return responses.get(option, "Opção inválida. Por favor, escolha uma opção válida.")

def process_main_option(option):
    responses = {
        '1': "🕒 *Horário de atendimento*\nSeg a Sex: 8h às 19h\nSábado: 9h às 13h",
        '2': "💰 *Tabela de preços*\nPor favor, verifique o documento anexado com nossa tabela de preços.",
        '3': "⏱️ *Prazo de entrega*\nPor favor, verifique o documento anexado com nossos prazos.",
        '4': "🚚 *Serviço de busca e entrega*\nValor: R$ 10 a R$ 30 (dependendo da distância)",
        '5': "📅 *Agendamento*\nPara agendar, entre em contato com nosso atendente.",
        '6': "🔍 *Verificação de roupas*\nUm atendente verificará se sua roupa está pronta.",
        '7': generate_service_menu(),
        '8': "📝 *Solicitar orçamento*\nPrecisamos das seguintes informações:\n- Nome\n- CNPJ (se empresa)\n- Endereço\n- Tipo de peça\n- Quantidade\n- Manchas\n- Prazo necessário\n\nPor favor, envie esses detalhes.",
        '9': "👟 *Lavagem de tênis*\nOferecemos lavagem especial para tênis com produtos específicos.",
        '10': "📍 *Endereço*\nAvenida Lazaro de Sousa Campos, 544 - Bairro São José",
        '11': "👗 *Lavagem de vestidos*\n- Vestido de festa: a partir de R$ 80,00\n- Vestido de noiva: a partir de R$ 250,00",
        '12': "🎨 *Tingimento*\nNão trabalhamos com tingimento.\nRecomendamos:\n- Tchau Varal\n- Restaura Jeans",
        '13': "🛋️ *Lavagem de sofá/tapete*\nNão oferecemos este serviço.\nRecomendamos: Carlos da Personal Clean\nTel: (16) 999994727"
    }
    return responses.get(option, "Opção inválida. Por favor, escolha uma opção válida.")

def get_user_state(phone_number):
    return user_states.get(phone_number, WELCOME)

def set_user_state(phone_number, state):
    user_states[phone_number] = state

def get_user_data(phone_number):
    return user_data.get(phone_number, {})

def set_user_data(phone_number, data):
    user_data[phone_number] = data

def is_natural_language_menu_request(message):
    menu_keywords = ['menu', 'opções', 'opcoes', 'ajuda', 'help', 'início', 'inicio', 'começar', 'comecar']
    return any(keyword in message.lower() for keyword in menu_keywords)

def is_numeric_input(message):
    return message.isdigit()

def handle_quote_request(phone_number, message):
    user_data_dict = get_user_data(phone_number)
    
    # If this is the first message in quote request
    if not user_data_dict:
        user_data_dict = {
            'step': 'name',
            'data': {}
        }
        set_user_data(phone_number, user_data_dict)
        return "Por favor, me diga seu nome:"
    
    # Handle the current step
    if user_data_dict['step'] == 'name':
        user_data_dict['data']['name'] = message
        user_data_dict['step'] = 'cnpj'
        set_user_data(phone_number, user_data_dict)
        return "Você é pessoa física ou jurídica? (Digite 'PF' ou 'PJ')"
    
    elif user_data_dict['step'] == 'cnpj':
        if message.upper() in ['PJ', 'JURIDICA', 'JURÍDICA']:
            user_data_dict['step'] = 'cnpj_number'
            set_user_data(phone_number, user_data_dict)
            return "Por favor, digite seu CNPJ:"
        else:
            user_data_dict['step'] = 'address'
            set_user_data(phone_number, user_data_dict)
            return "Por favor, digite seu endereço:"
    
    elif user_data_dict['step'] == 'cnpj_number':
        user_data_dict['data']['cnpj'] = message
        user_data_dict['step'] = 'address'
        set_user_data(phone_number, user_data_dict)
        return "Por favor, digite seu endereço:"
    
    elif user_data_dict['step'] == 'address':
        user_data_dict['data']['address'] = message
        user_data_dict['step'] = 'type'
        set_user_data(phone_number, user_data_dict)
        return "Qual o tipo de peça que você precisa lavar?"
    
    elif user_data_dict['step'] == 'type':
        user_data_dict['data']['type'] = message
        user_data_dict['step'] = 'quantity'
        set_user_data(phone_number, user_data_dict)
        return "Qual a quantidade?"
    
    elif user_data_dict['step'] == 'quantity':
        user_data_dict['data']['quantity'] = message
        user_data_dict['step'] = 'stains'
        set_user_data(phone_number, user_data_dict)
        return "Possui manchas? (Sim/Não)"
    
    elif user_data_dict['step'] == 'stains':
        user_data_dict['data']['stains'] = message
        user_data_dict['step'] = 'deadline'
        set_user_data(phone_number, user_data_dict)
        return "Qual o prazo necessário?"
    
    elif user_data_dict['step'] == 'deadline':
        user_data_dict['data']['deadline'] = message
        # Quote request completed
        set_user_state(phone_number, MAIN_MENU)
        set_user_data(phone_number, {})
        return "✅ Obrigado! Recebemos sua solicitação de orçamento. Entraremos em contato em breve."

@app.route("/webhook", methods=["POST"])
def webhook():
    # Verify webhook
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args.get("hub.verify_token") == os.getenv("WHATSAPP_VERIFY_TOKEN"):
            return request.args["hub.challenge"]
        return "Invalid verification token"
    
    # Handle incoming messages
    data = request.get_json()
    
    if data.get("object") == "whatsapp_business_account":
        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("value", {}).get("messages"):
                        for message in change["value"]["messages"]:
                            phone_number = message["from"]
                            incoming_msg = message["text"]["body"].strip()
                            
                            # Get current user state
                            current_state = get_user_state(phone_number)
                            
                            # Handle menu requests
                            if is_natural_language_menu_request(incoming_msg) or incoming_msg == '0':
                                set_user_state(phone_number, MAIN_MENU)
                                set_user_data(phone_number, {})
                                send_whatsapp_message(phone_number, generate_menu())
                                return "OK"
                            
                            # Handle welcome state
                            if current_state == WELCOME:
                                set_user_state(phone_number, MAIN_MENU)
                                send_whatsapp_message(phone_number, generate_welcome_message())
                                return "OK"
                            
                            # Process message based on current state
                            if current_state == MAIN_MENU:
                                if is_numeric_input(incoming_msg) and 1 <= int(incoming_msg) <= 13:
                                    if incoming_msg == '7':
                                        set_user_state(phone_number, SERVICE_INFO)
                                    elif incoming_msg == '8':
                                        set_user_state(phone_number, QUOTE_REQUEST)
                                    send_whatsapp_message(phone_number, process_main_option(incoming_msg))
                                else:
                                    send_whatsapp_message(phone_number, "❌ Desculpe, não entendi. Por favor, escolha uma opção válida ou digite *menu* para ver as opções disponíveis.")
                            
                            elif current_state == SERVICE_INFO:
                                if is_numeric_input(incoming_msg) and 1 <= int(incoming_msg) <= 3:
                                    send_whatsapp_message(phone_number, process_service_option(incoming_msg))
                                else:
                                    send_whatsapp_message(phone_number, "❌ Desculpe, não entendi. Por favor, escolha uma opção válida ou digite *menu* para voltar ao menu principal.")
                            
                            elif current_state == QUOTE_REQUEST:
                                send_whatsapp_message(phone_number, handle_quote_request(phone_number, incoming_msg))
                            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return "Error", 500
    
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)