from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ==========================================
# TUS CREDENCIALES (Reemplaza los textos entre comillas)
# ==========================================
VERIFY_TOKEN = "MiBoot2535"
PAGE_ACCESS_TOKEN = "EAA9ay7m42GcBQ85EOXyAWhfsQdoFNErvP5zdj1vQWPlPQB6lXj0Dos4dnqbb5alZCdQuCC75LfsKqSfn6QC4hX9Wfjf7eZCZBJZAR0QVPv1k9QlkqXsLzEimhnEp2pJzzCtrKBvaPWY7CTMNhZBIZALJgpn9ZAWPZAABeYAJyttnwFVIEBltv5vyfMEiSPTzQ8fCTjISq69strozlHdZAdHHndPejcgZDZD"
WIT_TOKEN = "VXGG4WWPHAMJTSJXRBKL5Y24Z5E7FLGO"
# ==========================================

# 1. RUTA PARA VERIFICAR EL WEBHOOK (Meta la usa la primera vez para conectarse)
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

# 2. RUTA PARA RECIBIR LOS MENSAJES DE LOS USUARIOS
@app.route('/webhook', methods=['POST'])
def process_webhook():
    data = request.json
    
    # Verificamos si el mensaje viene de una Página (Facebook) o Instagram
    if data.get('object') in ['page', 'instagram']:
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                # Nos aseguramos de que sea un mensaje de texto
                if 'message' in messaging_event and 'text' in messaging_event['message']:
                    sender_id = messaging_event['sender']['id']
                    user_text = messaging_event['message']['text']
                    
                    # A. Le preguntamos a Wit.ai qué significa el mensaje
                    respuesta_ia = consultar_wit_ai(user_text)
                    
                    # B. Le enviamos la respuesta al usuario en Facebook/Instagram
                    enviar_mensaje(sender_id, respuesta_ia)
                    
    return 'EVENT_RECEIVED', 200

# 3. FUNCIÓN PARA HABLAR CON WIT.AI Y RESPONDER COMO CALZADO CARIBU
def consultar_wit_ai(texto):
    url = f"https://api.wit.ai/message?v=20260312&q={texto}"
    headers = {"Authorization": f"Bearer {WIT_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers).json()
        
        if 'intents' in response and len(response['intents']) > 0:
            intencion = response['intents'][0]['name']
            
            # ==========================================
            # DICCIONARIO DE RESPUESTAS DE CALZADO CARIBU
            # ==========================================
            respuestas = {
                "saludo": "¡Hola! Bienvenido a Calzado Caribu 🥾. ¿En qué te podemos ayudar hoy?",
                
                "ubicacion": "Nuestra fábrica principal está en San Francisco del Rincón, Guanajuato. ¡Pero hacemos envíos a todo México! 📦",
                
                "comprar": "¡Excelente elección! Para hacer un pedido, compártenos el modelo que te gustó y tu código postal para revisar el envío.",
                
                "precio": "Tenemos excelentes precios de fábrica. Varían dependiendo de si buscas botas casuales o de trabajo industrial. ¿Qué estilo te interesa? 💸",
                
                "catalogo": "¡Claro que sí! Aquí puedes ver todos nuestros modelos disponibles: [Pega aquí el enlace a tu web o Facebook].",
                
                "asistente": "Soy el asistente virtual de Calzado Caribu, listo para ayudarte con tus compras."
            }
            
            # Busca la respuesta correspondiente a la intención. 
            # Si no la encuentra, da una respuesta genérica.
            return respuestas.get(intencion, f"Entendí que tu mensaje trata sobre '{intencion}', pero un humano te dará más detalles en breve.")
            
        else:
            return "Lo siento, soy el asistente virtual de Calzado Caribu y aún estoy aprendiendo. ¿Podrías escribir tu pregunta de otra forma?"
            
    except Exception as e:
        print("Error con Wit.ai:", e)
        return "Disculpa, tengo un pequeño problema técnico en este momento. Vuelvo enseguida."

# 4. FUNCIÓN PARA ENVIAR EL MENSAJE DE VUELTA POR MESSENGER
def enviar_mensaje(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

# 5. CONFIGURACIÓN PARA RENDER
if __name__ == '__main__':
    # Render asigna un puerto automáticamente, si no lo encuentra, usa el 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)