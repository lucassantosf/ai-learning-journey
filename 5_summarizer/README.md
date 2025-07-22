# Summarizer AI Project

## Overview
This is an AI-powered summarization tool that can process PDFs, text inputs, and audio recordings to generate summaries and study questions.

## Prerequisites
- Docker
- Docker Compose
- OpenAI API Key (optional, can use Ollama)

## Setup and Installation

1. Clone the repository
```bash
git clone <repository-url>
cd 5_summarizer
```

2. Create .env file
```bash
cp .env.example .env
```

3. Edit .env file
- Replace `your_openai_api_key_here` with your actual OpenAI API key
- Set `USE_OPENAI` to `true` or `false` based on your preference

## Running the Application

### Using Docker
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8501`

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuration Options
- Use OpenAI's GPT models by setting `USE_OPENAI=true`
- Use local Ollama models by setting `USE_OPENAI=false`

## Features
- PDF Upload and Processing
- Manual Text Input
- Audio Recording and Transcription
- AI-Generated Summaries
- Study Question Generation

## Troubleshooting
- Ensure you have a valid API key
- Check Docker and Docker Compose are correctly installed
- Verify network connectivity
