import requests
import websocket
import json
import time
import os
import random

# --- CONFIGURACIÓN (Render usa Variables de Entorno) ---
# En Render ve a Settings -> Environment -> Add Environment Variable
TOKEN = os.getenv("TOKEN", "dxKL7PEztCoPMy-1aBTb-TO7Ciam3SOg3NWEvJEAOzeNV7ZKTLaZuDV4TsKT-HMe")
ROOM_ID = os.getenv("ROOM_ID", "01K86SQJMYWK2NN9WF3KC8WXCC") # ID actualizado de tu captura de red
WS_URL = f"wss://stoat.chat/api/events?version=1&format=json&token={TOKEN}"

def enviar_mensaje(texto):
    url = "https://stoat.chat/api/messages" 
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MintBot/1.0 (Render Hosting)"
    }
    payload = {"content": texto, "room_id": ROOM_ID}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"📡 Mensaje enviado: {r.status_code}")
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")

def on_message(ws, message):
    try:
        data = json.loads(message)
        # Filtro de eventos de mensaje según la API de Stoat
        if data.get("type") == "Message":
            contenido = data.get("content", "").lower().strip()
            usuario = data.get("author", {}).get("username", "")
            
            # Evitar que el bot se responda a sí mismo
            if usuario.lower() != "mintbot":
                print(f"💬 {usuario}: {contenido}")
                
                # --- COMANDOS ---
                if contenido == "!hola":
                    enviar_mensaje(f"¡Hola @{usuario}! Estoy corriendo desde Render 🚀")
                
                elif contenido == "!dado":
                    enviar_mensaje(f"🎲 @{usuario} lanzó: {random.randint(1, 6)}")
                
                elif contenido == "!ping":
                    enviar_mensaje("🏓 ¡Pong! El bot está vivo.")

    except Exception as e:
        print(f"⚠️ Error procesando mensaje: {e}")

def on_error(ws, error):
    print(f"🔴 Error de WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    print("🔄 Conexión perdida. Reiniciando en 10 segundos...")
    time.sleep(10)

def on_open(ws):
    print("✅ MintBot conectado correctamente a Stoat.")
    # Mensaje opcional al conectar
    # enviar_mensaje("🤖 MintBot ha vuelto online.")

if __name__ == "__main__":
    print("启动 MintBot...") # Log de inicio
    while True:
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            # El ping_interval es CLAVE en Render para que no maten el proceso
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as e:
            print(f"💥 Crash crítico: {e}. Reiniciando...")
            time.sleep(5)
