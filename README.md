# Projeto Dashboard de Saúde do Motor v2.0

Este projeto monitora a saúde de um motor de indução em tempo real, apresentando os dados em um dashboard web interativo. A arquitetura foi refatorada para maior robustez, modularidade e realismo na simulação de dados.

## Funcionalidades

-   **Monitoramento em Tempo Real:** Acompanhe o status e os dados do motor instantaneamente.
-   **Dashboard Interativo:** Visualize gráficos de corrente e vibração, e indicadores de status para os componentes do motor.
-   **Simulação Realista:** Dois cenários de simulação: operação normal e falha, para testar a robustez do sistema.
-   **Arquitetura desacoplada:** Utiliza MQTT para comunicação entre o simulador e o backend, e WebSockets para comunicação entre o backend e o frontend.

## Tecnologias Utilizadas

-   **Frontend:** HTML5, CSS3, JavaScript (com Chart.js para gráficos)
-   **Backend:** Python, Flask, Flask-SocketIO, Paho-MQTT
-   **Broker de Mensagens:** MQTT (recomenda-se Mosquitto)
-   **Servidor de Produção:** Gunicorn, Eventlet

## Estrutura do Projeto

```
.
├── backend/
│   ├── app.py                # Servidor principal (gateway MQTT para WebSocket)
│   ├── config.py             # Configurações do backend
│   ├── requirements.txt      # Dependências Python
│   └── .env.example          # Exemplo de arquivo de ambiente
├── frontend/
│   ├── index.html            # Estrutura do dashboard
│   ├── style.css             # Estilos do dashboard
│   └── script.js             # Lógica do cliente (WebSocket, gráficos)
├── simulators/
│   ├── normal_operation_simulator.py # Simulador de operação normal
│   └── failure_scenario_simulator.py # Simulador de cenário de falha
├── sketch_oct28a/
│   └── sketch_oct28a.ino     # Código de exemplo para microcontrolador (ESP8266)
├── .gitignore
└── README.md
```

## Como Executar

### 1. Pré-requisitos

-   Python 3.x
-   Um broker MQTT (como o [Mosquitto](https://mosquitto.org/)) rodando em `localhost:1883`.
-   Navegador web moderno.

### 2. Configuração do Ambiente

Antes de executar, é necessário configurar as variáveis de ambiente para o backend.

1.  Navegue até a pasta `backend`.
2.  Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.
    ```bash
    cp .env.example .env
    ```
3.  Revise o arquivo `.env` e ajuste as configurações (como o endereço do broker MQTT ou a porta do servidor), se necessário.

### 3. Backend

Abra um terminal, navegue até a pasta `backend` e instale as dependências:

```bash
pip install -r requirements.txt
```

**Para desenvolvimento:**

Inicie o servidor de desenvolvimento:

```bash
python app.py
```

O servidor estará rodando em `http://localhost:5000`.

**Para produção:**

É recomendado usar um servidor WSGI robusto como o Gunicorn.

1.  Instale o Gunicorn e o Eventlet:
    ```bash
    pip install gunicorn eventlet
    ```
2.  No arquivo `.env`, ajuste `FLASK_DEBUG=False`.
3.  Inicie o servidor com Gunicorn:
    ```bash
    gunicorn --workers 3 --bind 0.0.0.0:5000 "app:app" --worker-class eventlet -w 1
    ```

### 4. Simulador

Abra um **novo terminal** e execute um dos simuladores:

**Operação Normal:**

```bash
python simulators/normal_operation_simulator.py
```

**Cenário de Falha:**

```bash
python simulators/failure_scenario_simulator.py
```

O simulador começará a publicar dados no broker MQTT, que serão recebidos pelo backend.

### 5. Frontend

Abra o arquivo `frontend/index.html` em seu navegador. O dashboard se conectará automaticamente ao backend e começará a exibir os dados em tempo real.

## Estrutura de Dados MQTT

O simulador publica em dois tópicos para separar os dados de alta frequência dos de baixa frequência.

### Tópico de Saúde (Baixa Frequência)

-   **Tópico:** `iot/plant_01/motor_123/health_status`
-   **Descrição:** Envia uma análise completa do estado de saúde do motor a cada segundo.
-   **Exemplo de Payload:**
    ```json
    {
        "motor_id": "MOT-123-XYZ",
        "timestamp": "2025-11-17T14:30:00Z",
        "overall_status": "Atenção",
        "health_indicators": {
            "rolling_bearing": {
                "gamma_degradation_percent": 25.5,
                "status": "Falha Incipiente"
            },
            "stator_winding": {
                "alpha_degradation_percent": 15.2,
                "status": "Falha Incipiente"
            },
            "rotor_bars": {
                "broken_bars_count": 1,
                "status": "Falha Incipiente"
            }
        }
    }
    ```

### Tópico de Sensores (Alta Frequência)

-   **Tópico:** `iot/plant_01/motor_123/sensor_data`
-   **Descrição:** Envia dados brutos de sensores em alta frequência (10x por segundo).
-   **Exemplo de Payload:**
    ```json
    {
        "motor_id": "MOT-123-XYZ",
        "timestamp": "2025-11-17T14:30:00.100Z",
        "corrente": 4.85,
        "vibracao": 0.3512
    }
    ```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

1.  Faça um *fork* do projeto.
2.  Crie uma nova *branch* (`git checkout -b feature/nova-funcionalidade`).
3.  Faça suas alterações e *commits* (`git commit -m 'Adiciona nova funcionalidade'`).
4.  Envie para a sua *branch* (`git push origin feature/nova-funcionalidade`).
5.  Abra um *Pull Request*.

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.