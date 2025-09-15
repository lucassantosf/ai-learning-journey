# AI Learning Journey E-Commerce Project

## Project Overview
This is an AI-powered e-commerce project that demonstrates an intelligent agent-based system for managing product inventory, orders, and checkout processes.

## Prerequisites
- Python 3.8+
- pip (Python package manager)

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/lucassantosf/ai-learning-journey.git
cd ai-learning-journey/6_simulated_agent
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
. venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Streamlit UI
To launch the Streamlit user interface:
```bash
streamlit run src/ui/streamlit_app.py
```

### Running the Main Application
```bash
python app.py
```

## Database Setup and Seeding

### Initialize Database
The project uses SQLite as its database. To set up the initial database with seed data:
```bash
python -c "from src.utils.sqlite_seeder import seed_database; seed_database()"
```

## Running Tests
To run the project's test suite: (e.g)
```bash
python -m tests/agent.py
```

### Test Coverage
The test suite includes the following test modules:

1. `tests/agent.py`: 
   - Tests the AI agent's core functionality
   - Verifies agent behavior in different scenarios
   - Checks agent's decision-making processes

2. `tests/memory_summarizer.py`:
   - Tests memory management and summarization techniques
   - Validates memory storage and retrieval mechanisms
   - Ensures accurate memory processing

3. `tests/repositories.py`:
   - Tests database repository implementations
   - Validates CRUD operations for products, inventory, and orders
   - Checks data consistency and repository interfaces

## Project Structure
```
6_simulated_agent/
│
├── src/
│   ├── agent/         # AI agent implementation
│   ├── models/        # Data models
│   ├── repository/    # Database repositories
│   ├── ui/            # User interface
│   └── utils/         # Utility functions
│
├── tests/             # Test suite
├── logs/              # Log files
├── app.py             # Main application entry point
└── requirements.txt   # Project dependencies
```

## Environment Variables
Copy `.env.example` to `.env` and configure any necessary environment-specific settings.

## Logging
Logs are stored in the `logs/` directory. Check `logs/agent.log` for runtime information and debugging.