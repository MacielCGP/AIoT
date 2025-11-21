# backend/app.py

import json
import threading
import logging
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import paho.mqtt.client as mqtt

# --- Módulos locais ---
import config

# --- Inicialização do Servidor Web e SocketIO ---
app = Flask(__name__)
# Configurar o nível de log do app Flask
app.logger.setLevel(logging.INFO)
CORS(app, resources={r"/*": {"origins": config.CORS_ALLOWED_ORIGINS}})
socketio = SocketIO(app, cors_allowed_origins=config.CORS_ALLOWED_ORIGINS)

# --- Lógica do Cliente MQTT ---
def on_connect(client, userdata, flags, rc):
    """Callback executado ao conectar ao broker MQTT."""
    if rc == 0:
        app.logger.info("Conectado ao Broker MQTT!")
        try:
            client.subscribe(config.MQTT_HEALTH_TOPIC)
            client.subscribe(config.MQTT_SENSOR_TOPIC)
            app.logger.info(f"Inscrito no tópico de saúde: {config.MQTT_HEALTH_TOPIC}")
            app.logger.info(f"Inscrito no tópico de sensores: {config.MQTT_SENSOR_TOPIC}")
        except Exception as e:
            app.logger.error(f"Erro ao se inscrever nos tópicos: {e}")
    else:
        app.logger.error(f"Falha na conexão com o MQTT, código de retorno: {rc}")

def on_message(client, userdata, msg):
    """Processa mensagens MQTT e as emite via WebSocket."""
    try:
        payload = json.loads(msg.payload.decode())
        
        if msg.topic == config.MQTT_HEALTH_TOPIC:
            app.logger.info(f"Mensagem de saúde recebida no tópico {msg.topic}")
            # Emite o dicionário Python diretamente. A biblioteca cuidará da serialização.
            socketio.emit('health_update', payload)

            # Lógica de Alerta
            overall_status = payload.get("overall_status")
            if overall_status == "Falha":
                alert = {"type": "falha", "message": "Alerta: Falha crítica detectada no motor!"}
                socketio.emit('health_alert', alert)
                app.logger.warning(f"Alerta de falha emitido: {alert['message']}")
            elif overall_status == "Atenção":
                alert = {"type": "atenção", "message": "Atenção: Potencial problema detectado."}
                socketio.emit('health_alert', alert)
                app.logger.warning(f"Alerta de atenção emitido: {alert['message']}")

        elif msg.topic == config.MQTT_SENSOR_TOPIC:
            # Emite o dicionário Python diretamente.
            app.logger.info(f"Mensagem de sensor recebida: {payload}")
            socketio.emit('sensor_update', payload)
            
    except json.JSONDecodeError:
        app.logger.error(f"Erro ao decodificar o JSON do tópico {msg.topic}")
    except Exception as e:
        app.logger.error(f"Ocorreu um erro em on_message: {e}")

def mqtt_listener():
    """Inicia o cliente MQTT e o mantém em loop."""
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        app.logger.error(f"Não foi possível conectar ao broker MQTT em {config.MQTT_BROKER}:{config.MQTT_PORT}. Erro: {e}")

# --- Rotas e Eventos SocketIO ---
@socketio.on('connect')
def handle_connect():
    app.logger.info('Cliente conectado ao WebSocket!')

@socketio.on('disconnect')
def handle_disconnect():
    app.logger.info('Cliente desconectado do WebSocket.')

# --- Iniciação ---
if __name__ == '__main__':
    app.logger.info("Iniciando o serviço de backend...")
    
    # Inicia o listener MQTT em uma thread separada
    mqtt_thread = threading.Thread(target=mqtt_listener, daemon=True)
    mqtt_thread.start()
    
    # Inicia o servidor Flask com SocketIO
    app.logger.info(f"Servidor Flask com SocketIO rodando em http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    socketio.run(
        app,
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        log_output=False # Desativa o log padrão do Werkzeug para evitar duplicatas
    )
