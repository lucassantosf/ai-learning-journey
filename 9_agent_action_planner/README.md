# AI Learning Journey

## Descrição do Projeto

Este projeto é uma jornada de aprendizado em inteligência artificial, desenvolvendo uma aplicação web que explora diferentes aspectos e implementações de tecnologias de IA. A aplicação combina um backend robusto construído com FastAPI e um frontend moderno utilizando React e TypeScript.

### Principais Características

- Backend em Python com FastAPI
- Frontend em React com TypeScript
- Containerização com Docker
- Arquitetura modular e escalável
- Foco em aprendizado e experimentação de tecnologias de IA

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- Docker
- Docker Compose
- Node.js (para desenvolvimento local do frontend)
- Python 3.8+ (para desenvolvimento local do backend)

## Executando o Projeto

### Opção 1: Executando Frontend e Backend Separadamente

#### Frontend (React)

1. Navegue para o diretório do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

4. Acesse a aplicação em: `http://localhost:5173`

#### Backend (FastAPI)

1. Navegue para o diretório do backend:
   ```bash
   cd backend
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Acesse a documentação da API em: `http://localhost:8000/docs`

### Opção 2: Executando com Docker

#### Iniciar Todos os Serviços

```bash
docker-compose up --build
```

#### Serviços Disponíveis

- Frontend: `http://localhost:80`
- Backend (API): `http://localhost:8000`
- Documentação da API: `http://localhost:8000/docs`

#### Parar os Serviços

```bash
docker-compose down
```

## Estrutura do Projeto

```
ai-learning-journey/
│
├── backend/               # Código do backend Python/FastAPI
│   ├── app/
│   │   ├── api/           # Rotas e endpoints
│   │   ├── core/          # Configurações e utilitários
│   │   ├── models/        # Modelos de dados
│   │   └── services/      # Lógica de negócio
│   └── tests/             # Testes unitários
│
├── frontend/              # Código do frontend React
│   ├── src/
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── pages/         # Páginas da aplicação
│   │   ├── routes/        # Configuração de rotas
│   │   └── services/      # Serviços de integração
│   └── ...
│
└── docker-compose.yml     # Configuração de serviços Docker
```


