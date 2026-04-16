import os
import threading
import time
import json
import random
import requests
import websocket
from flask import Flask

# 1. Configuración de la Web (Obligatorio para Render Free)
app = Flask(__name__)

@app.route('/')
def health():
    return "MintBot Status: Online", 200

def run_web():
    # Render usa el puerto 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Configuración del Bot (Leído de tus Variables de Entorno)
TOKEN = os.environ.get("TOKEN")
ROOM_ID = os.environ.get("ROOM_ID", "01K86SQJMYWK2NN9WF3KC8WXCC")
WS_URL = f"wss://stoat.chat/api/events?version=1&format=json&token={TOKEN}"

def enviar_mensaje(texto):
    url = "https://stoat.chat/api/messages" 
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"content": texto, "room_id": ROOM_ID}
    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
    except:
        pass

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "Message":
            user = data.get("author", {}).get("username", "").lower()
            content = data.get("content", "").lower()
            
            # Evitar que el bot se responda a sí mismo
            if "mintbot" not in user:
                if "!hola" in content:
                    enviar_mensaje(f"¡Hola! MintBot reportándose desde Render 🚀")
                elif "!dado" in content:
                    enviar_mensaje(f"🎲 Salió un: {random.randint(1, 6)}")
    except:
        pass

def run_bot():
    while True:
        try:
            # Usamos el WS_URL que ya tiene el token inyectado
            ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except:
            time.sleep(10)

if __name__ == "__main__":
    # Iniciamos la web en un segundo plano
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Iniciamos el bot en el hilo principal
    run_bot()
