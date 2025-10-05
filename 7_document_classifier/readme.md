# Execute project with Docker

sudo docker compose up -d

# Execute only frontend 

cd frontend/

npm run dev

# Execute only backend api

First, active the .venv

cd backend/

uvicorn api.main:api --host 0.0.0.0 --port 8000 --reload

# To predict the correct classification for the files types (invoice, resume, contract), necessary run the embedder script

python -m backend.services.build_dataset

# Execute tests

cd backend/

python -m pytest

# Execute only one test class

cd backend/

python -m pytest tests/test_ocr_extractor.py

# To extract OCR, necessary install: 

sudo apt-get install tesseract-ocr
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por

pip install pytesseract pdf2image