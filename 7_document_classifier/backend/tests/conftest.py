import os
import pytest
import numpy as np
from fastapi.testclient import TestClient
from api.main import api
from agent.vector_store import VectorStore
from agent.embedder import Embedder
from agent.document_agent import DocumentAgent
from agent.prompt_engine import PromptEngine
from services.file_parser import parse_file

@pytest.fixture(scope="function")
def reset_app_state():
    """
    Fixture to reset the application state before each test
    """
    # Reset all state components
    api.state.embedder = Embedder()
    api.state.vector_store = VectorStore()
    api.state.prompt_engine = PromptEngine()
    api.state.document_agent = DocumentAgent()

    # Populate vector store with real document embeddings
    def populate_vector_store():
        doc_dirs = {
            'resumes': '../dataset/resumes',
            'invoices': '../dataset/invoices', 
            'contracts': '../dataset/contracts'
        }

        class_embeddings = {
            'resumes': [],
            'invoices': [],
            'contracts': []
        }

        for class_name, dir_path in doc_dirs.items():
            full_path = os.path.join(os.path.dirname(__file__), dir_path)
            
            for filename in os.listdir(full_path):
                file_path = os.path.join(full_path, filename)
                
                if not filename.lower().endswith(('.pdf', '.docx')):
                    continue
                
                try:
                    text = parse_file(file_path)
                    embedding = api.state.embedder.generate_embeddings(text)
                    class_embeddings[class_name].append(embedding)
                
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

        # Add embeddings to vector store
        for class_name, embeddings in class_embeddings.items():
            if embeddings:
                # Use mean embedding for each class
                mean_embedding = np.mean(embeddings, axis=0).tolist()
                api.state.vector_store.add(mean_embedding, {"class_label": class_name})

    populate_vector_store()
    return api.state

@pytest.fixture(scope="function")
def client(reset_app_state):
    """
    Fixture to create a test client with reset state
    """
    return TestClient(api)