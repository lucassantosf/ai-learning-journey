# Execute project with Docker

sudo docker compose up -d

# Execute only frontend 

cd frontend/

npm run dev

# Execute only backend

cd backend/

uvicorn api.main:api --host 0.0.0.0 --port 8000 --reload