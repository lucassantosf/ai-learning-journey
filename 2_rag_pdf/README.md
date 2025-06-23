# PDF RAG Chat

A Streamlit application that allows you to chat with your PDF documents using RAG (Retrieval-Augmented Generation) technology.

## Overview

This application demonstrates how to build a document question-answering system using:
- Streamlit for the web interface
- ChromaDB for vector storage and retrieval
- PyPDF2 for PDF text extraction
- Ollama for local LLM inference

The application uses a RAG (Retrieval-Augmented Generation) approach to find the most relevant passages from uploaded PDF documents and then generates responses to user questions based on those passages.

## Features

- Upload and process PDF documents
- Chunk documents into manageable pieces
- Store document chunks as vector embeddings
- Ask questions about the content of your documents
- View source passages that informed the answer

## Requirements

- Python 3.8+
- Streamlit
- ChromaDB
- PyPDF2
- OpenAI Python library (for API compatibility with Ollama)
- python-dotenv
- Ollama running locally with the llama3.2:1b model

## Installation

1. Make sure you have Python installed
2. Install the required packages:
   ```
   pip install streamlit chromadb pypdf2 openai python-dotenv
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
   streamlit run 2_rag_pdf.py
   ```
2. Open your browser at the URL provided by Streamlit (typically http://localhost:8501)
3. Upload a PDF document using the file uploader
4. Wait for the document to be processed
5. Type your question in the text input field and press Enter
6. The application will display an answer based on the content of your documents
7. You can view the source passages that informed the answer by expanding the "View Source Passages" section

## How It Works

1. PDF Processing:
   - The application reads the uploaded PDF and extracts text
   - The text is split into chunks with some overlap to maintain context
   - Each chunk is assigned a unique ID and metadata

2. Vector Storage:
   - The application uses ChromaDB to store document chunks as vector embeddings
   - The embeddings are created using the default embedding function

3. Question Answering:
   - When a user asks a question, it's converted to an embedding
   - ChromaDB finds the most similar document chunks
   - The relevant chunks are used to augment a prompt sent to the LLM
   - The LLM generates a response based on the retrieved information
   - The response and source passages are displayed to the user

## Customization

You can customize the application by modifying the following parameters:
- `CHUNK_SIZE`: The size of document chunks (default: 1000)
- `CHUNK_OVERLAP`: The overlap between chunks (default: 200)
- Change the LLM model by modifying the model name in the `generate_response` method

## Limitations

- The application can only process text-based PDFs (not scanned documents)
- Large PDFs may take time to process
- The quality of responses depends on the quality of the LLM model being used
- Currently uses a local Ollama model, which may have limitations compared to cloud-based models

## Future Improvements

- Add support for more document types (DOCX, TXT, etc.)
- Implement OCR for scanned documents
- Add document management features (delete, list all documents)
- Implement conversation history
- Add support for multiple embedding models
- Improve chunking strategy for better context preservation
