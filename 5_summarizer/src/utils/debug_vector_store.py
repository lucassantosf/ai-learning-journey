from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from src.config import CHROMA_PERSIST_PATH, VECTOR_STORE_COLLECTION

def debug_vector_store(query: str, n_results: int = 3):
    """
    Debug and inspect the vector store by performing a similarity search.

    This function allows you to query the vector store and display detailed
    information about the retrieved documents, including their text, metadata,
    and similarity distances.

    Args:
        query (str): The search query to find similar documents.
        n_results (int, optional): Number of results to retrieve. Defaults to 3.
    """
    try: 
        # Initialize the client
        client = PersistentClient(path=CHROMA_PERSIST_PATH)

        # Use the same collection name as the system
        collection = client.get_collection(
            name=VECTOR_STORE_COLLECTION,
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

        # Perform a simple search
        results = collection.query(query_texts=[query], n_results=n_results)

        print("\nSearch Results:")
        for i, doc in enumerate(results["documents"][0]):
            print(f"\n--- Result #{i+1} ---")
            print("Text:", doc)
            print("Metadata:", results["metadatas"][0][i])
            print("Distance:", results["distances"][0][i])
    except Exception as e:
        print(f"\nError querying vector store: {e}")

if __name__ == "__main__":
    print("Checking data in vector store...")
    query = input("Enter a term or question to search: ")
    debug_vector_store(query)
