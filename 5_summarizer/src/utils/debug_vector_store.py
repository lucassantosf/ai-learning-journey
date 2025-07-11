from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from src.config import CHROMA_PERSIST_PATH, VECTOR_STORE_COLLECTION

def debug_vector_store(query: str, n_results: int = 3):
    try: 
        # Inicializa o client
        client = PersistentClient(path=CHROMA_PERSIST_PATH)

        # Usa o mesmo nome de coleção que seu sistema
        collection = client.get_collection(
            name=VECTOR_STORE_COLLECTION,
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )

        # Faz uma busca simples
        results = collection.query(query_texts=[query], n_results=n_results)

        print("\nResultados da busca:")
        for i, doc in enumerate(results["documents"][0]):
            print(f"\n--- Resultado #{i+1} ---")
            print("Texto:", doc)
            print("Metadata:", results["metadatas"][0][i])
            print("Distância:", results["distances"][0][i])
    except Exception as e:
        print(f"\nErro ao consultar o vector store: {e}")

if __name__ == "__main__":
    print("Verificando dados no vector store...")
    query = input("Digite um termo ou pergunta para buscar: ")
    debug_vector_store(query)
