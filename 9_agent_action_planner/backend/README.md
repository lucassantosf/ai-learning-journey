# Backend Project Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes_health.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging_config.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py
│   │
│   └── services/
│       ├── __init__.py
│       └── agent_service.py
│
├── tests/
│   ├── __init__.py
│   └── test_health.py
│
├── tests_playground/
│   └── langgraph/
│       ├── __init__.py
│       ├── agent_tools_router_09.py
│       ├── final_agent_12.py
│       ├── human_in_loop_11.py
│       ├── langgraph_basic_03.py
│       ├── memory_sqlite_01.py
│       ├── model_router_08.py
│       ├── multipass_subgraph_10.py
│       ├── node_sharing_state_06.py
│       ├── planner_executor_basic_02.py
│       ├── planner_executor_with_memory_04.py
│       ├── planner_executor_with_memory_05.py
│       └── router_07.py
│
├── .env
├── .env.example
├── Dockerfile
├── memory.db
├── requirements.txt
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
