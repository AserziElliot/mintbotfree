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
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME", "mintbot").lower()

print(f"TOKEN configurado: {'Sí' if TOKEN else 'NO'}")
print(f"ROOM_ID configurado: {'Sí' if ROOM_ID else 'NO'}")
print(f"BOT_USERNAME: {BOT_USERNAME}")

if not TOKEN or not ROOM_ID:
    raise Exception("Faltan variables de entorno: TOKEN o ROOM_ID")

WS_URL = f"wss://api.stoat.xyz/ws?token={TOKEN}"
API_URL = "https://api.stoat.xyz/messages"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

print("WS_URL generada correctamente")

# ============================
# SERVIDOR FLASK (RENDER)
# ============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Stoat Bot Online", 200

@app.route("/health")
def health():
    return {"status": "ok", "bot": BOT_USERNAME}, 200

# ============================
# ENVIAR MENSAJES
# ============================
def enviar_mensaje(texto):
    payload = {"content": texto, "room_id": ROOM_ID}
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print(f"Mensaje enviado ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

# ============================
# CLAUDE AI
# ============================
def preguntar_claude(pregunta):
    if not ANTHROPIC_API_KEY:
        return "❌ Falta ANTHROPIC_API_KEY."
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "system": "Eres un bot simpático en un chat llamado Stoat. Responde breve y amigable. Máximo 2-3 oraciones.",
        "messages": [{"role": "user", "content": pregunta}]
    }
    try:
        r = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=20)
        data = r.json()
        if "content" in data and data["content"]:
            return data["content"][0]["text"]
        print("Respuesta inesperada de Claude:", data)
        return "🤖 Sin respuesta de Claude."
    except Exception as e:
        print(f"Error llamando a Claude: {e}")
        return "❌ Error al conectar con Claude AI."

# ============================
# MANEJO DE MENSAJES
# ============================
def on_message(ws, message):
    try:
        data = json.loads(message)
        if data.get("type") != "Message":
            return

        autor = data["author"]["username"]
        contenido = data["content"].strip()
        print(f"[{autor}] dijo: {contenido}")

        if autor.lower() == BOT_USERNAME:
            return

        if contenido.startswith("!hola"):
            enviar_mensaje(f"¡Hola, {autor}! 😎🤖")
        elif contenido.startswith("!dado"):
            enviar_mensaje(f"🎲 {autor}, tu número es: {random.randint(1, 6)}")
        elif contenido.startswith("!ping"):
            enviar_mensaje("Pong 🏓")
        elif contenido.startswith("!ayuda"):
            enviar_mensaje("📖 Comandos: !hola, !dado, !ping, !ai <pregunta>, !ayuda")
        elif contenido.startswith("!ai "):
            pregunta = contenido[4:].strip()
            enviar_mensaje("⏳ Consultando a Claude AI...")
            threading.Thread(
                target=lambda: enviar_mensaje(f"🤖 {preguntar_claude(pregunta)}"),
                daemon=True
            ).start()
        elif contenido.startswith("!ai"):
            enviar_mensaje("❓ Uso: !ai <tu pregunta>")

    except Exception as e:
        print(f"Error procesando mensaje: {e}")

def on_error(ws, error):
    print(f"❌ Error WS: {error} | Tipo: {type(error)}")

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 WS cerrado - código: {close_status_code}, msg: {close_msg}")

def on_open(ws):
    print("✅ Conectado al WebSocket de Stoat")

# ============================
# LOOP DE RECONEXIÓN (en hilo secundario)
# ============================
def iniciar_ws():
    intento = 0
    while True:
        intento += 1
        print(f"🔄 Intento de conexión #{intento}")
        try:
            ws = WebSocketApp(
                WS_URL,
                header={"Authorization": TOKEN},
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as e:
            print(f"💥 Error crítico en WS: {e} | Tipo: {type(e)}")
        print("⏳ Reintentando en 5 segundos...")
        time.sleep(5)

# ============================
# INICIO DEL BOT
# ============================
if __name__ == "__main__":
    print("🚀 Iniciando bot...")
    # WS en hilo secundario, Flask en el principal (así Render detecta el puerto)
    threading.Thread(target=iniciar_ws, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
