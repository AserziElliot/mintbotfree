import os
import time
import json
import random
import threading
import requests
import websocket
from flask import Flask

# Servidor web para que Render mantenga el servicio activo
app = Flask(__name__)

@app.route('/')
def health():
    return "MintBot is Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURACIÓN ---
TOKEN = os.getenv("TOKEN")
ROOM_ID = os.getenv("ROOM_ID")
WS_URL = f"wss://stoat.chat/api/events?version=1&format=json&token={TOKEN}"

def enviar_mensaje(texto):
    url = "https://stoat.chat/api/messages" 
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": texto, "room_id": ROOM_ID}
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"Error al enviar: {e}")

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "Message":
            contenido = data.get("content", "").lower().strip()
            # Obtenemos el nombre de usuario de forma segura
            usuario_obj = data.get("author", {})
            usuario_nombre = usuario_obj.get("username", "").lower()
            
            # Solo respondemos si el mensaje NO viene de nuestro bot
            if "mintbot" not in usuario_nombre:
                if contenido == "!hola":
                    enviar_mensaje(f"¡Hola! MintBot reportándose 🚀")
                elif contenido == "!dado":
                    enviar_mensaje(f"🎲 Salió un: {random.randint(1, 6)}")
    except Exception as e:
        print(f"Error en mensaje: {e}")

def bot_loop():
    while True:
        try:
            print("🚀 Intentando conectar al chat...")
            ws = websocket.WebSocketApp(
                WS_URL, 
                on_message=on_message,
                on_open=lambda ws: print("✅ ¡CONECTADO!")
            )
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except:
            time.sleep(10)

if __name__ == "__main__":
    # Iniciar servidor web en segundo plano
    threading.Thread(target=run_flask, daemon=True).start()
    # Iniciar bot
    bot_loop()import os
import time
import json
import random
import threading
import requests
import websocket
from flask import Flask

# Servidor web para que Render mantenga el servicio activo
app = Flask(__name__)

@app.route('/')
def health():
    return "MintBot is Online", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURACIÓN ---
TOKEN = os.getenv("TOKEN")
ROOM_ID = os.getenv("ROOM_ID")
WS_URL = f"wss://stoat.chat/api/events?version=1&format=json&token={TOKEN}"

def enviar_mensaje(texto):
    url = "https://stoat.chat/api/messages" 
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": texto, "room_id": ROOM_ID}
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"Error al enviar: {e}")

def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") == "Message":
            contenido = data.get("content", "").lower().strip()
            # Obtenemos el nombre de usuario de forma segura
            usuario_obj = data.get("author", {})
            usuario_nombre = usuario_obj.get("username", "").lower()
            
            # Solo respondemos si el mensaje NO viene de nuestro bot
            if "mintbot" not in usuario_nombre:
                if contenido == "!hola":
                    enviar_mensaje(f"¡Hola! MintBot reportándose 🚀")
                elif contenido == "!dado":
                    enviar_mensaje(f"🎲 Salió un: {random.randint(1, 6)}")
    except Exception as e:
        print(f"Error en mensaje: {e}")

def bot_loop():
    while True:
        try:
            print("🚀 Intentando conectar al chat...")
            ws = websocket.WebSocketApp(
                WS_URL, 
                on_message=on_message,
                on_open=lambda ws: print("✅ ¡CONECTADO!")
            )
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except:
            time.sleep(10)

if __name__ == "__main__":
    # Iniciar servidor web en segundo plano
    threading.Thread(target=run_flask, daemon=True).start()
    # Iniciar bot
    bot_loop()
