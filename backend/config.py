# backend/config.py
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- Funções Auxiliares ---
def get_env_variable(name, default=None):
    """Obtém uma variável de ambiente, com um valor padrão."""
    return os.environ.get(name, default)

def get_bool_env_variable(name, default=False):
    """Obtém uma variável de ambiente booleana."""
    return get_env_variable(name, str(default)).lower() in ['true', '1', 't']

# --- Configurações do Broker MQTT ---
MQTT_BROKER = get_env_variable("MQTT_BROKER", "localhost")
MQTT_PORT = int(get_env_variable("MQTT_PORT", 1883))

# --- Tópicos MQTT ---
MQTT_HEALTH_TOPIC = get_env_variable("MQTT_HEALTH_TOPIC", "iot/plant_01/motor_123/health_status")
MQTT_SENSOR_TOPIC = get_env_variable("MQTT_SENSOR_TOPIC", "iot/plant_01/motor_123/sensor_data")

# --- Configurações do Servidor Flask ---
FLASK_HOST = get_env_variable("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(get_env_variable("FLASK_PORT", 5000))
FLASK_DEBUG = get_bool_env_variable("FLASK_DEBUG", True)

# --- Configurações do SocketIO ---
# Para CORS, é melhor ser explícito em produção, mas manter a flexibilidade
CORS_ALLOWED_ORIGINS = get_env_variable("CORS_ALLOWED_ORIGINS", "*")

