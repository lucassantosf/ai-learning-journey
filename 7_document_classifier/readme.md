# Execute project with Docker

sudo docker compose up -d

# Execute only frontend 

cd frontend/

npm run dev

# Execute only backend

cd backend/

uvicorn api.main:api --host 0.0.0.0 --port 8000 --reload

# To predict the correct classification for the files types (invoice, resume, contract), necessary run the embedder script

python -m backend.services.build_dataset

# Execute tests

cd backend/

python -m pytest