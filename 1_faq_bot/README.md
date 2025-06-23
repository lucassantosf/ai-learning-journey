# FAQ Bot

A simple FAQ chatbot built with Streamlit and RAG (Retrieval-Augmented Generation) that answers questions based on a predefined set of FAQs.

## Overview

This application demonstrates how to build a simple FAQ chatbot using:
- Streamlit for the web interface
- ChromaDB for vector storage and retrieval
- Ollama for local LLM inference

The bot uses a RAG (Retrieval-Augmented Generation) approach to find the most relevant FAQ entries to a user's question and then generates a response based on those entries.

## Features

- Simple and intuitive chat interface
- Predefined set of FAQ entries
- Vector-based semantic search for finding relevant information
- Local LLM inference using Ollama

## Requirements

- Python 3.8+
- Streamlit
- ChromaDB
- OpenAI Python library (for API compatibility with Ollama)
- Ollama running locally with the llama3.2:1b model

## Installation

1. Make sure you have Python installed
2. Install the required packages:
   ```
   pip install streamlit chromadb openai
   ```
3. Install and run Ollama with the llama3.2:1b model:
   ```
   # Follow instructions at https://ollama.com/ to install Ollama
   ollama pull llama3.2:1b
   ollama serve
   ```

## Usage

1. Run the application:
   ```
   streamlit run 1_faq_bot.py
   ```
2. Open your browser at the URL provided by Streamlit (typically http://localhost:8501)
3. Type your question in the text input field and press Enter
4. The bot will respond with the most relevant answer from the FAQ database

## How It Works

1. The application loads a predefined set of FAQ entries (questions and answers)
2. It creates embeddings for these entries and stores them in ChromaDB
3. When a user asks a question:
   - The question is converted to an embedding
   - ChromaDB finds the most similar FAQ entries
   - The relevant entries are used to augment a prompt sent to the LLM
   - The LLM generates a response based on the retrieved information
   - The response is displayed to the user

## Customization

You can customize the FAQ entries by modifying the `load_questions()` function in the code. Each entry should have:
- `id`: A unique identifier
- `question`: The FAQ question
- `answer`: The corresponding answer

## Limitations

- The bot can only answer questions related to the predefined FAQs
- The quality of responses depends on the quality of the LLM model being used
- Currently uses a local Ollama model, which may have limitations compared to cloud-based models

## Future Improvements

- Add the ability to add new FAQ entries through the UI
- Implement feedback mechanism to improve responses
- Add support for multiple languages
- Integrate with external knowledge bases
