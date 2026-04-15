import os
import time
import json
import random
import threading
import requests
import websocket
from flask import Flask

# --- MINI SERVIDOR WEB PARA RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Online", 200

def run_web_server():
    # Render asigna un puerto automáticamente en la variable PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURACIÓN DEL BOT ---
TOKEN = os.getenv("TOKEN", "dxKL7PEztCoPMy-1aBTb-TO7Ciam3SOg3NWEvJEAOzeNV7ZKTLaZuDV4TsKT-HMe")
ROOM_ID = os.getenv("ROOM_ID", "01K86SQJMYWK2NN9WF3KC8WXCC")
WS_URL = f"wss://stoat.chat/api/events?version=1&format=json&token={TOKEN}"

def enviar_mensaje(texto):
    url = "https://stoat.chat/api/messages" 
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"content": texto, "room_id": ROOM_ID}
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except:
        pass

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "Message":
            contenido = data.get("content", "").lower().strip()
            usuario = data.get("author", {}).get("username", "")
            if usuario.lower() != "mintbot":
                if contenido == "!hola":
                    enviar_mensaje(f"¡Hola @{usuario}! Reportándome desde Render Gratis 🚀")
                elif contenido == "!dado":
                    enviar_mensaje(f"🎲 @{usuario} lanzó: {random.randint(1, 6)}")
    except:
        pass

def iniciar_bot():
    while True:
        try:
            ws = websocket.WebSocketApp(WS_URL, on_message=on_message)
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except:
            time.sleep(10)

if __name__ == "__main__":
    # 1. Iniciamos el servidor web en un hilo (Thread) para que Render esté feliz
    threading.Thread(target=run_web_server).start()
    # 2. Iniciamos el bot en el hilo principal
    iniciar_bot()
