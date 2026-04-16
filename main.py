import os
import json
import random
import threading
import time
import requests
from flask import Flask
from websocket import WebSocketApp

# ============================
# VARIABLES DE ENTORNO
# ============================
TOKEN = os.getenv("TOKEN")
ROOM_ID = os.getenv("ROOM_ID")

if not TOKEN or not ROOM_ID:
    raise Exception("Faltan variables de entorno: TOKEN o ROOM_ID")

WS_URL = f"wss://api.stoat.xyz/ws?token={TOKEN}"
API_URL = "https://api.stoat.xyz/messages"

# ============================
# SERVIDOR FLASK (RENDER)
# ============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Stoat Bot Online", 200

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ============================
# ENVIAR MENSAJES
# ============================
def enviar_mensaje(texto):
    payload = {
        "content": texto,
        "room_id": ROOM_ID
    }

    try:
        r = requests.post(API_URL, json=payload, headers={"Authorization": TOKEN})
        print("Mensaje enviado:", r.text)
    except Exception as e:
        print("Error enviando mensaje:", e)

# ============================
# MANEJO DE MENSAJES
# ============================
def on_message(ws, message):
    try:
        data = json.loads(message)

        if data.get("type") != "Message":
            return

        autor = data["author"]["username"]
        contenido = data["content"]

        print(f"[{autor}] dijo: {contenido}")

        # Evitar responderse a sí mismo
        if autor.lower() == "mintbot":
            return

        # Comandos
        if contenido.startswith("!hola"):
            enviar_mensaje("¡Hola! Soy un bot funcionando en Render 😎")

        elif contenido.startswith("!dado"):
            enviar_mensaje(f"🎲 Tu número es: {random.randint(1, 6)}")

        elif contenido.startswith("!ping"):
            enviar_mensaje("Pong 🏓")

    except Exception as e:
        print("Error procesando mensaje:", e)

def on_error(ws, error):
    print("Error WS:", error)

def on_close(ws, close_status_code, close_msg):
    print("Conexión cerrada, intentando reconectar...")

def on_open(ws):
    print("Conectado al WebSocket de Stoat")

# ============================
# LOOP DE RECONEXIÓN
# ============================
def iniciar_ws():
    while True:
        try:
            ws = WebSocketApp(
                WS_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as e:
            print("Error crítico:", e)

        print("Reintentando en 5 segundos...")
        time.sleep(5)

# ============================
# INICIO DEL BOT
# ============================
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    iniciar_ws()
