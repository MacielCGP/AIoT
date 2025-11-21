    // esp8266_mqtt.ino
// Script para ESP8266 (Arduino C++) para simular e enviar dados de motor via MQTT.

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <math.h>


// --- Configurações de Rede ---
// ATENÇÃO: As informações abaixo (SSID, senha, IP do broker) estão fixas no código
// apenas para fins de demonstração. Em um ambiente de produção, utilize métodos
// seguros para armazenar e carregar essas credenciais, como um portal de configuração
// ou armazenamento em memória não volátil.
const char* WIFI_SSID = "CAT S41_6550";
const char* WIFI_PASSWORD = "12345678";

// --- Configurações do Broker MQTT ---
const char* MQTT_BROKER = "192.168.43.116";
const int MQTT_PORT = 1883;
// Este sketch de exemplo publica no tópico de dados de sensores de alta frequência.
const char* MQTT_TOPIC = "iot/plant_01/motor_123/sensor_data";
const char* CLIENT_ID = "esp8266_motor_simulator_arduino";

// --- Variáveis Globais ---
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
float t = 0.0; // Variável de tempo para a simulação

// --- Conexão Wi-Fi ---
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros()); // Inicializa o gerador de números aleatórios

  Serial.println("");
  Serial.println("WiFi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

// --- Simulação de Dados ---
void get_motor_data(float time_val, float* corrente, float* vibracao) {
  float amplitude = 5.0;
  float frequencia = 0.5;
  // Gera um ruído entre -0.3 e 0.3
  float ruido = (float)random(0, 60) / 100.0 - 0.3; 
  
  *corrente = amplitude * sin(2 * PI * frequencia * time_val) + ruido;

  // Gera uma vibração entre 0.1 e 0.25 com um pequeno ruído adicional
  float vibracao_base = (float)random(1000, 2500) / 10000.0;
  float vibracao_ruido = ((float)random(0, 50) / 1000.0) - 0.025;
  *vibracao = vibracao_base + vibracao_ruido;
}


// --- Reconexão MQTT ---
void reconnect() {
  // Loop até reconectar
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT...");
    // Tenta conectar
    if (client.connect(CLIENT_ID)) {
      Serial.println("conectado!");
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      // Espera 5 segundos antes de tentar novamente
      delay(5000);
    }
  }
}

// --- Setup ---
void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(MQTT_BROKER, MQTT_PORT);
}

// --- Loop Principal ---
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  // Publica a cada 2 segundos (2000 ms)
  if (now - lastMsg > 25) {
    lastMsg = now;
    
    // Atualiza a variável de tempo (dividido por 1000 para converter ms para s)
    t = (float)millis() / 1000.0;

    // Gera os dados do motor
    float corrente, vibracao;
    get_motor_data(t, &corrente, &vibracao);

    // Cria o documento JSON
    StaticJsonDocument<128> doc;
    doc["corrente"] = round(corrente * 100) / 100.0; // Arredonda para 2 casas decimais
    doc["vibracao"] = round(vibracao * 10000) / 10000.0; // Arredonda para 4 casas decimais

    // Serializa o JSON para uma string
    char payload[128];
    serializeJson(doc, payload);

    // Publica a mensagem
    Serial.print("Publicando mensagem: ");
    Serial.println(payload);
    client.publish(MQTT_TOPIC, payload);
  }
}
