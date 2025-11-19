# Backend Project Structure


```
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── routes_health.py
│   │   └── routes_agent.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   └── dependencies.py         # <-- (NOVO: fornece agent_service, db, etc)
│   │
│   ├── models/
│   │   ├── base.py                 # Base do SQLAlchemy
│   │   └── db_models.py            # <-- (NOVO: MemoryLog, Plan, Step)
│   │
│   ├── services/
│   │   ├── agent_service.py        # Orquestrador
│   │   ├── planner.py              # <-- (NOVO)
│   │   ├── executor.py             # <-- (NOVO)
│   │   ├── memory_sqlite.py        # <-- (NOVO)
│   │   └── tool_registry.py        # <-- (NOVO: registry centralizado)
│   │
│   ├── tools/
│   │   ├── base.py                 # Interface Tool
│   │   ├── web_search.py           # Ferramenta simulada
│   │   ├── calendar.py             # Ferramenta simulada
│   │   └── compute.py              # <-- (NOVO: ferramenta de “cálculo”)
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── plan.py                 # <-- (NOVO: Request/Response models)
│       ├── step.py                 # <-- (NOVO)
│       └── memory.py               # <-- (NOVO)
│
├── tests/ (igual)
├── tests_playground/ (igual)
├── requirements.txt
├── memory.db
└── README.md
```

## Project Overview
- `app/`: Main application package
  - `api/`: API route definitions
  - `core/`: Configuration and core utilities
  - `models/`: Database models
  - `services/`: Business logic services

- `tests/`: Unit and integration tests
- `tests_playground/`: Experimental and learning-related test scripts, particularly for LangGraph explorations

## Key Files
- `Dockerfile`: Containerization configuration
- `requirements.txt`: Project dependencies
- `.env.example`: Environment variable template
