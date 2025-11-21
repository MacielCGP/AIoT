# Projeto Dashboard de Saúde do Motor v2.0

Este projeto monitora a saúde de um motor de indução em tempo real, apresentando os dados em um dashboard web interativo. A arquitetura foi refatorada para maior robustez, modularidade e realismo na simulação de dados.

## Arquitetura

O sistema é composto por três partes principais:

1.  **Simulador de Motor (`motor_simulator.py`):** Um script Python que gera dados realistas sobre a saúde e operação de um motor. Ele simula diferentes estados (Saudável, Atenção, Falha) e publica os dados em um broker MQTT em dois tópicos distintos.
2.  **Backend (`backend/`):** Uma aplicação Flask que atua como um gateway. Ele se inscreve nos tópicos MQTT, processa os dados recebidos e os transmite em tempo real para o frontend via WebSockets.
3.  **Frontend (`frontend/`):** Uma aplicação web de página única (SPA) construída com HTML, CSS e JavaScript. Ela se conecta ao backend via WebSocket, recebe os dados do motor e os exibe em um dashboard com gráficos e indicadores de status.

## Estrutura do Projeto

-   `motor_simulator.py`: Simulador  de dados do motor.
-   `backend/`: Contém a aplicação Flask.
    -   `app.py`: O servidor principal (gateway MQTT para WebSocket).
    -   `config.py`: Arquivo de configuração para o backend (portas, tópicos MQTT, etc.).
    -   `requirements.txt`: Dependências Python do backend.
-   `frontend/`: Contém os arquivos do dashboard.
    -   `index.html`: Estrutura da página.
    -   `style.css`: Estilização do dashboard.
    -   `script.js`: Lógica do cliente (WebSocket, atualização da UI, gráficos).
-   `sketch_oct28a/`: Contém um código de exemplo para um microcontrolador (ESP8266) que pode atuar como um sensor físico, publicando dados no mesmo formato do simulador.

## Como Executar

### 1. Pré-requisitos

-   Python 3.x
-   Um broker MQTT (como o Mosquitto) rodando em `localhost:1883`.
-   Navegador web moderno.

### 2. Configuração de Ambiente

Antes de executar, é necessário configurar as variáveis de ambiente.

1.  Navegue até a pasta `backend`.
2.  Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.
    ```bash
    cp .env.example .env
    ```
3.  Revise o arquivo `.env` e ajuste as configurações (como o endereço do broker MQTT ou a porta do servidor), se necessário.

### 3. Backend (Desenvolvimento)

Abra um terminal, navegue até a pasta `backend` e instale as dependências usando o arquivo de lock para garantir consistência:

```bash
pip install -r requirements.lock.txt
```

Em seguida, inicie o servidor de desenvolvimento:

```bash
python app.py
```

O servidor estará rodando em `http://localhost:5000`.

### 4. Backend (Produção)

Para um ambiente de produção, é recomendado usar um servidor WSGI robusto como o Gunicorn.

1.  Certifique-se de que as dependências estão instaladas com `pip install -r requirements.lock.txt`.
2.  No arquivo `.env`, ajuste `FLASK_DEBUG=False`.
3.  Inicie o servidor com Gunicorn, apontando para o objeto `app` dentro do seu arquivo `app.py`:
    ```bash
    gunicorn --workers 3 --bind 0.0.0.0:5000 "app:app" --worker-class eventlet -w 1
    ```

### 5. Simulador

Abra um **novo terminal**, navegue até a pasta raiz do projeto e execute o simulador:

```bash
python simulators/normal_operation_simulator.py
```

O simulador começará a publicar dados no broker MQTT, que serão recebidos pelo backend.

### 6. Frontend

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
