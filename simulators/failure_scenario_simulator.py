import paho.mqtt.client as mqtt
import time
import json
import random
import math
from datetime import datetime, timezone

# Configurações do Broker MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_SENSOR_TOPIC = "iot/plant_01/motor_123/sensor_data"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado ao Broker MQTT!")
    else:
        print(f"Falha na conexão, código de retorno {rc}\n")

def simulate_failure_scenario(step):
    """Simula um cenário de falha iminente do motor com corrente senoidal."""
    # Parâmetros da senoide para a corrente em modo de falha
    amplitude = 0.8
    frequency = 0.1
    offset = 6.0
    noise = random.uniform(-0.2, 0.2)
    
    corrente = amplitude * math.sin(frequency * step) + offset + noise
    corrente = round(corrente, 2)
    
    vibracao = round(random.uniform(0.5, 0.9), 4) # Mantém vibração alta
    
    # Gera o timestamp no formato ISO 8601 com fuso horário UTC
    timestamp = datetime.now(timezone.utc).isoformat()
    
    return {"corrente": corrente, "vibracao": vibracao, "timestamp": timestamp}

def run():
    client = mqtt.Client(client_id="simulator_failure")
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_start()
    step = 0
    try:
        while True:
            data = simulate_failure_scenario(step)
            payload = json.dumps(data)
            result = client.publish(MQTT_SENSOR_TOPIC, payload)
            status = result[0]
            if status == 0:
                print(f"Enviado `{payload}` para o tópico `{MQTT_SENSOR_TOPIC}`")
            else:
                print(f"Falha ao enviar mensagem para o tópico `{MQTT_SENSOR_TOPIC}`")
            time.sleep(0.05)
            step += 1
    except KeyboardInterrupt:
        print("Simulação interrompida.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    run()
