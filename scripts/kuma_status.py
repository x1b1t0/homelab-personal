import os
import json
from datetime import datetime
from dotenv import load_dotenv
from uptime_kuma_api import UptimeKumaApi

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

KUMA_URL = os.getenv('KUMA_URL', 'http://localhost:3001')
KUMA_USER = os.getenv('KUMA_USER')
KUMA_PASS = os.getenv('KUMA_PASS')

HISTORICO = os.path.join(os.path.dirname(__file__), 'historico.json')

def main():
    if not KUMA_USER or not KUMA_PASS:
        print("❌ Error: KUMA_USER y KUMA_PASS deben estar definidos en .env")
        return

    try:
        print("🔍 Conectando a Uptime Kuma...")
        api = UptimeKumaApi(KUMA_URL)
        api.login(KUMA_USER, KUMA_PASS)
        print("✅ Conectado!\n")
        
        monitores = api.get_monitors()
        
        print(f"{'Servicio':<20} {'Estado':<10} {'Ping':<10}")
        print("-" * 45)
        
        estado_actual = []
        ahora = datetime.now().isoformat()
        
        for m in monitores:
            nombre = m.get('name', 'Desconocido')
            monitor_id = m.get('id')
            activo = "✅ Up" if m.get('active') else "❌ Down"
            ping = "N/A"
            
            # Obtener beats de las últimas 24h
            try:
                beats = api.get_monitor_beats(monitor_id, 24)
                if beats:
                    ultimo = beats[-1]
                    ping_val = ultimo.get('ping', 0)
                    ping = f"{ping_val}ms" if ping_val else "N/A"
                    if ultimo.get('status') == 0:
                        activo = "❌ Down"
            except Exception as e:
                ping = "Error"
            
            print(f"{nombre:<20} {activo:<10} {ping:<10}")
            
            estado_actual.append({
                "nombre": nombre,
                "estado": activo,
                "ping": ping,
                "timestamp": ahora
            })
        
        # Guardar histórico
        historico = []
        if os.path.exists(HISTORICO):
            with open(HISTORICO, 'r') as f:
                historico = json.load(f)
        
        historico.append({
            "fecha": ahora,
            "servicios": estado_actual
        })
        
        historico = historico[-100:]
        
        with open(HISTORICO, 'w') as f:
            json.dump(historico, f, indent=2)
        
        print(f"\n💾 Histórico guardado en {HISTORICO}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
