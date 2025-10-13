# Document Classifier - AI Learning Journey

## 📋 Project Overview

This is an intelligent document classifier that uses artificial intelligence techniques to automatically categorize different types of documents, such as contracts, invoices, and resumes.

### 🚀 Main Technologies
- Backend: Python, FastAPI
- Frontend: React, Next.js
- Infrastructure: Docker
- Machine Learning: Embedding, Document Classification

## 🖥️ Prerequisites

Before starting, make sure you have installed:
- Docker (version 20.10 or higher)
- Python 3.9+
- Node.js 16+
- npm or yarn

## 🔧 Installation and Configuration

### Clone the Repository
```bash
git clone https://github.com/your-username/document-classifier.git
cd document-classifier
```

### Environment Setup

1. Create virtual environment (optional, but recommended)
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

2. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd ../frontend
npm install
```

## 🐳 Running the Project

### Run Complete Project with Docker
```bash
sudo docker compose up -d
```

### Run Only Frontend
```bash
cd frontend/
npm run dev
```

### Run Only Backend API
```bash
cd backend/
source .venv/bin/activate
uvicorn api.main:api --host 0.0.0.0 --port 8000 --reload
```

## 🔍 Dataset Preparation

To prepare the dataset and train the classification model:
```bash
python -m backend.services.build_dataset
```

## 🧪 Tests

### Run All Tests
```bash
cd backend/
python -m pytest
```

### Run Specific Test
```bash
cd backend/
python -m pytest tests/test_ocr_extractor.py
```

## 📦 Additional OCR Dependencies

Install Tesseract OCR dependencies:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por
pip install pytesseract pdf2image
```

## 💾 Database Initialization

Create SQLite database:
```bash
cd backend/
python -m api.core.init_db
```

## 🏗️ Project Structure
```
document-classifier/
├── backend/
│   ├── agent/
│   ├── api/
│   ├── dataset/
│   └── services/
├── frontend/
│   ├── components/
│   ├── pages/
│   └── services/
└── docker-compose.yml
```