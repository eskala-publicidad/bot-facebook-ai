from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ==========================================
# TUS CREDENCIALES (Reemplaza los textos entre comillas)
# ==========================================
VERIFY_TOKEN = "MiBoot2535"
PAGE_ACCESS_TOKEN = "EAA9ay7m42GcBQ876uBW0d7fFZAWLayA73sQZAuliEyuW03PaNtZA9TYsdyk2ZCQZCZAMgPUqG5mTIlZCV8gcHS3d0xx5FqQtQKl3L65PhKeI4ZBHpqVqCgfbO4hMjWaYXzv5yTdjAHh3tanuWsEXZC5RLZA93PQQtREVZCfAZAsq52Q2k8wnku4ZCg4cFZAf70SSlVooXZALvjZA5h2EBOsyHVGOjUXbQ7FKnwZDZD"
WIT_TOKEN = "VXGG4WWPHAMJTSJXRBKL5Y24Z5E7FLGO"
# ==========================================

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Prohibido', 403
    return 'Hola, el servidor está funcionando', 200

@app.route('/webhook', methods=['POST'])
def process_webhook():
    data = request.json
    
    if data.get('object') in ['page', 'instagram']:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message']['text']
                    
                    # Le enviamos el texto y el ID del usuario al Composer
                    respuesta_ia = consultar_wit_composer(user_text, sender_id)
                    
                    if respuesta_ia:
                        enviar_mensaje(sender_id, respuesta_ia)
                        
    return 'EVENT_RECEIVED', 200

# 3. FUNCIÓN CONECTADA AL COMPOSER DE WIT.AI
def consultar_wit_composer(texto, sender_id):
    # Usamos la ruta /event que es la exclusiva para leer tus lienzos
    url = f"https://api.wit.ai/event?v=20260312&session_id={sender_id}"
    headers = {
        "Authorization": f"Bearer {WIT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "message",
        "message": texto
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload).json()
        print("RESPUESTA DE COMPOSER:", response)
        
        # Extraemos el mensaje exacto que dibujaste en tu lienzo
        if 'messages' in response and len(response['messages']) > 0:
            return response['messages'][0]['text']
            
        # Si Wit.ai no encuentra un lienzo para responder:
        return "Lo siento, soy el asistente de Calzado Caribu y aún estoy aprendiendo."
            
    except Exception as e:
        print("Error con Wit.ai Composer:", e)
        return "Disculpa, tengo un pequeño problema técnico en este momento."

def enviar_mensaje(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)