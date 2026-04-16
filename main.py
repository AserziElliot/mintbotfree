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

if not TOKEN or not ROOM_ID:
    raise Exception("Faltan variables de entorno: TOKEN o ROOM_ID")

if not ANTHROPIC_API_KEY:
    print("ADVERTENCIA: ANTHROPIC_API_KEY no está configurada. El comando !ai no funcionará.")

WS_URL = f"wss://api.stoat.xyz/ws?token={TOKEN}"
API_URL = "https://api.stoat.xyz/messages"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

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
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
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
        return "❌ La API de Claude no está configurada (falta ANTHROPIC_API_KEY)."

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "system": "Eres un bot simpático en un chat llamado Stoat. Responde de forma breve, clara y amigable. Máximo 2-3 oraciones.",
        "messages": [
            {"role": "user", "content": pregunta}
        ]
    }
    try:
        r = requests.post(ANTHROPIC_URL, json=payload, headers=headers, timeout=20)
        data = r.json()
        if "content" in data and len(data["content"]) > 0:
            return data["content"][0]["text"]
        else:
            print("Respuesta inesperada de Claude:", data)
            return "🤖 No pude obtener una respuesta de Claude."
    except Exception as e:
        print(f"Error llamando a Claude: {e}")
        return "❌ Error al conectar con Claude AI."

# ============================
# MANEJO DE MENSAJES
# ============================
def on_message(ws, message):
    try:
        data = json.loads(message)

        # Solo procesar mensajes de tipo "Message"
        if data.get("type") != "Message":
            return

        autor = data["author"]["username"]
        contenido = data["content"].strip()

        print(f"[{autor}] dijo: {contenido}")

        # Evitar responderse a sí mismo
        if autor.lower() == BOT_USERNAME:
            return

        # ---- Comandos ----

        if contenido.startswith("!hola"):
            enviar_mensaje(f"¡Hola, {autor}! Soy un bot con IA integrada 😎🤖")

        elif contenido.startswith("!dado"):
            enviar_mensaje(f"🎲 {autor}, tu número es: {random.randint(1, 6)}")

        elif contenido.startswith("!ping"):
            enviar_mensaje("Pong 🏓")

        elif contenido.startswith("!ayuda"):
            enviar_mensaje(
                "📖 Comandos disponibles:\n"
                "!hola - Saludo\n"
                "!dado - Tira un dado\n"
                "!ping - Comprueba si estoy activo\n"
                "!ai <pregunta> - Pregúntame cualquier cosa con IA\n"
                "!ayuda - Esta lista"
            )

        elif contenido.startswith("!ai "):
            pregunta = contenido[4:].strip()
            if not pregunta:
                enviar_mensaje("❓ Escribe una pregunta después de !ai")
                return
            enviar_mensaje("⏳ Consultando a Claude AI...")
            # Llamar a Claude en un hilo para no bloquear el WebSocket
            threading.Thread(
                target=lambda: enviar_mensaje(f"🤖 {preguntar_claude(pregunta)}"),
                daemon=True
            ).start()

        elif contenido.startswith("!ai"):
            enviar_mensaje("❓ Uso correcto: !ai <tu pregunta>")

    except Exception as e:
        print(f"Error procesando mensaje: {e}")

# ============================
# CALLBACKS DEL WEBSOCKET
# ============================
def on_error(ws, error):
    print(f"Error WS: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Conexión cerrada (código: {close_status_code}): {close_msg}")

def on_open(ws):
    print("✅ Conectado al WebSocket de Stoat")

# ============================
# LOOP DE RECONEXIÓN
# ============================
def iniciar_ws():
    while True:
        try:
            ws = WebSocketApp(
                WS_URL,
                header={"Authorization": TOKEN},  # Header extra por si la API lo requiere
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever(
                ping_interval=30,   # Envía ping cada 30s para mantener la conexión viva
                ping_timeout=10     # Si no responde en 10s, reconecta
            )
        except Exception as e:
            print(f"Error crítico en WS: {e}")

        print("🔄 Reintentando conexión en 5 segundos...")
        time.sleep(5)

# ============================
# INICIO DEL BOT
# ============================
if __name__ == "__main__":
    print("🚀 Iniciando bot...")
    threading.Thread(target=run_web, daemon=True).start()
    iniciar_ws()
