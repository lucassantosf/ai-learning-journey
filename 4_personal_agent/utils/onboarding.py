import os
import csv
import traceback
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

class Onboarding:
    def __init__(self, path="./assets/onboarding.csv"):
        try:
            # Resolve absolute path
            self.path = os.path.abspath(path)
            print(f"Attempting to load CSV from: {self.path}")
            
            # Verify file exists and is readable
            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Onboarding file not found: {self.path}")
            
            # Check file size and content
            file_size = os.path.getsize(self.path)
            print(f"CSV file size: {file_size} bytes")
            
            if file_size == 0:
                raise ValueError("CSV file is empty")
            
            # Initialize embedding model
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as model_error:
                print(f"Error initializing embedding model: {model_error}")
                print(traceback.format_exc())
                raise
            
            # Initialize ChromaDB client
            try:
                self.chroma_client = chromadb.Client()
                self.collection = self.chroma_client.get_or_create_collection(name="onboarding_docs")
            except Exception as chroma_error:
                print(f"Error initializing ChromaDB: {chroma_error}")
                print(traceback.format_exc())
                raise
            
            # Load and embed documents if collection is empty
            if self.collection.count() == 0:
                self.embed_documents()
        
        except Exception as init_error:
            print(f"Critical error in Onboarding initialization: {init_error}")
            print(traceback.format_exc())
            raise

    def preprocess_document(self, row):
        """
        Create a more meaningful document representation
        
        Args:
            row (pandas.Series): A row from the DataFrame
        
        Returns:
            str: Preprocessed document string
        """
        # Remove empty or NaN values
        row = row.dropna()
        
        # Convert to string and join
        document = ' '.join(row.astype(str))
        
        # Additional preprocessing
        document = document.lower()  # Convert to lowercase
        document = ' '.join(document.split())  # Remove extra whitespaces
        
        return document

    def embed_documents(self):
        """
        Read CSV and create embeddings in ChromaDB with comprehensive error handling
        """
        try:
            # Read CSV
            df = pd.read_csv(self.path, header=None)
            
            # Preprocess documents
            documents = df.apply(self.preprocess_document, axis=1).tolist()
            
            # Validate documents
            if not documents:
                print("Warning: No documents found in the CSV file.")
                return
            
            # Generate embeddings
            try:
                embeddings = self.model.encode(documents).tolist()
            except Exception as embed_error:
                print(f"Error generating embeddings: {embed_error}")
                print(traceback.format_exc())
                return
            
            # Add to ChromaDB
            try:
                self.collection.add(
                    embeddings=embeddings,
                    documents=documents,
                    ids=[f"doc_{i}" for i in range(len(documents))]
                )
                print(f"Successfully embedded {len(documents)} documents")
                
                # Debug: Print first few documents and their embeddings
                print("First 3 documents:")
                for i in range(min(3, len(documents))):
                    print(f"Doc {i}: {documents[i]}")
                    print(f"Embedding length: {len(embeddings[i])}")
            except Exception as add_error:
                print(f"Error adding documents to ChromaDB: {add_error}")
                print(traceback.format_exc())
        
        except Exception as general_error:
            print(f"Unexpected error in embed_documents: {general_error}")
            print(traceback.format_exc())

    def search(self, query, n_results=3):
        """
        Perform semantic search on onboarding documents with comprehensive error handling
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
        
        Returns:
            List of most relevant document chunks
        """
        try:
            # Validate query
            if not query or not isinstance(query, str):
                print("Invalid query provided")
                return []
            
            # Preprocess query
            query = query.lower().strip()
            
            # Debug: Print query details
            print(f"Searching for query: '{query}'")
            print(f"Total documents in collection: {self.collection.count()}")
            
            # Embed the query
            try:
                query_embedding = self.model.encode([query])[0].tolist()
                print(f"Query embedding length: {len(query_embedding)}")
            except Exception as embed_error:
                print(f"Error embedding query: {embed_error}")
                print(traceback.format_exc())
                return []
            
            # Perform semantic search
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                
                # Debug: Print search results
                print("Search Results:")
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0], 1):
                        print(f"Result {i}: {doc}")
                else:
                    print("No results found in the search.")
                
                return results['documents'][0] if results['documents'] and results['documents'][0] else []
            except Exception as query_error:
                print(f"Error performing semantic search: {query_error}")
                print(traceback.format_exc())
                return []
        
        except Exception as general_error:
            print(f"Unexpected error in search method: {general_error}")
            print(traceback.format_exc())
            return []

    def semantic_search(self, query, n_results=3):
        """
        Perform semantic search and return formatted results
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
        
        Returns:
            Formatted search results as markdown
        """
        try:
            # Perform semantic search
            search_results = self.search(query, n_results)
            
            # Validate search results
            if not search_results:
                print(f"No results found for query: {query}")
                return f"No results found for query: {query}"
            
            # Format results as markdown
            markdown_results = ["# Onboarding Search Results"]
            for i, result in enumerate(search_results, 1):
                markdown_results.append(f"\n## Result {i}")
                markdown_results.append(f"**Relevance**: High")
                markdown_results.append(f"**Content**:\n{result}")
            
            return "\n".join(markdown_results)
        
        except Exception as e:
            print(f"Error in semantic search: {e}")
            print(traceback.format_exc())
            return f"Error performing semantic search: {str(e)}"

if __name__ == "__main__":
    obj = Onboarding()
    
    # Example usage of semantic search
    query = "tour assistida"
    print(obj.semantic_search(query))
