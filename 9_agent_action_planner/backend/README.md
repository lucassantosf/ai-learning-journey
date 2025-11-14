backend/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes_health.py       # Healthcheck e rotas iniciais
│   │   
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Configurações gerais (env, paths, etc)
│   │   └── logging_config.py          # Setup de logs
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py                    # Base para modelos SQLAlchemy (ex: memória)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── agent_service.py           # Onde o agente será implementado futuramente
│   │
│   ├── __init__.py
│   └── main.py                        # Ponto de entrada FastAPI
│
├── tests/
│   ├── __init__.py
│   └── test_health.py                 # Teste inicial de healthcheck
│
├── .env.example                       # Exemplo de variáveis de ambiente
├── Dockerfile                         # Configurações de build do Docker
├── requirements.txt                   # Dependências do projeto
└── README.md
