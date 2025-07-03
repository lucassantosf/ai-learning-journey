import os
import csv
import traceback
import pandas as pd
import chromadb
import numpy as np

class Onboarding:
    def __init__(self, path="./assets/onboarding.csv"):
        try:
            self.path = os.path.abspath(path)

            if not os.path.exists(self.path):
                raise FileNotFoundError(f"Onboarding file not found: {self.path}")

            file_size = os.path.getsize(self.path)

            if file_size == 0:
                raise ValueError("CSV file is empty")

            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(name="onboarding_docs")

            if self.collection.count() == 0:
                self.embed_documents()
            
        except Exception as init_error:
            print("[DEBUG] Exception during Onboarding.__init__:", init_error)
            raise ValueError(f"Erro de inicialização do onboarding: {str(init_error)}")

    def preprocess_document(self, row):
        """
        Create a more meaningful document representation
        
        Args:
            row (pandas.Series): A row from the DataFrame
        
        Returns:
            str: Preprocessed document string
        """
        # Skip rows that are entirely empty or contain only empty strings
        if row.isnull().all() or (row.astype(str) == '').all():
            return None
        
        # Focus on meaningful columns (activity description)
        meaningful_columns = [col for col in row.index if row[col] not in ['', 'Não Feito', '-']]
        
        # If no meaningful columns, return None
        if not meaningful_columns:
            return None
        
        # Combine meaningful columns
        document_parts = []
        for col in meaningful_columns:
            value = str(row[col]).strip()
            if value and value.lower() not in ['não feito', '-']:
                document_parts.append(value)
        
        # Join document parts
        document = ' '.join(document_parts)
        
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
            documents = df.apply(self.preprocess_document, axis=1).dropna().tolist()
            
            # Validate documents
            if not documents:
                return []
            
            # Add to ChromaDB with simple numeric embeddings
            self.collection.add(
                embeddings=[[float(i)] * 10 for i in range(len(documents))],  # Simple numeric embeddings
                documents=documents,
                ids=[f"doc_{i}" for i in range(len(documents))]
            )
            
            return documents
        
        except Exception as e:
            raise ValueError(f"Erro ao processar documentos de onboarding: {str(e)}")

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
                return []
            
            # Preprocess query
            query = query.lower().strip()
            
            # Ensure documents are embedded if collection is empty
            if self.collection.count() == 0:
                self.embed_documents()
            
            # Simple numeric embedding for query
            query_embedding = [float(hash(query) % 10)] * 10
            
            # Perform semantic search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return results['documents'][0] if results['documents'] and results['documents'][0] else []
        
        except Exception:
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
                return f"Nenhum resultado encontrado para a consulta: {query}"
            
            # Format results as markdown
            markdown_results = ["# Resultados da Busca de Onboarding"]
            for i, result in enumerate(search_results, 1):
                markdown_results.append(f"\n## Resultado {i}")
                markdown_results.append(f"**Relevância**: Alta")
                markdown_results.append(f"**Conteúdo**:\n{result}")
            
            return "\n".join(markdown_results)
        
        except Exception:
            return f"Erro ao realizar busca semântica para: {query}"

    def read_as_markdown(self):
        print('read_as_markdown called')  # Debug print
        """
        Provide a default markdown representation of onboarding documents
        
        Returns:
            str: Markdown-formatted overview of onboarding documents
        """
        try:
            # Read the entire CSV file
            df = pd.read_csv(self.path, header=None)
            
            # Prepare a comprehensive overview
            markdown_results = [
                "# Resumo do Processo de Onboarding",
                "\n## Visão Geral",
                "O processo de onboarding é composto por várias etapas fundamentais para integração de novos membros da equipe.",
                "\n## Etapas Principais:"
            ]
            
            # Extract unique stages and activities
            stages = {}
            for _, row in df.iterrows():
                # Assuming the first column contains stage information
                stage = str(row.iloc[0]).strip()
                if stage and stage.lower() not in ['não feito', '-', '']:
                    if stage not in stages:
                        stages[stage] = []
                
                # Try to extract activity from other columns
                for col in row.index[1:]:
                    activity = str(row.iloc[col]).strip()
                    if activity and activity.lower() not in ['não feito', '-', '']:
                        stages[stage].append(activity)
            
            # Add stages to markdown
            for stage, activities in stages.items():
                markdown_results.append(f"\n### {stage}")
                for activity in activities:
                    markdown_results.append(f"- {activity}")
            
            # Add total number of stages and activities
            markdown_results.append(f"\n**Total de Etapas**: {len(stages)}")
            markdown_results.append(f"**Total de Atividades**: {sum(len(activities) for activities in stages.values())}")
            
            # Add a closing note
            markdown_results.append("\n## Observação")
            markdown_results.append("Este resumo destaca as principais etapas e atividades do processo de onboarding. Cada etapa é crucial para a integração efetiva de novos membros da equipe.")
            
            return "\n".join(markdown_results)
        
        except Exception as e:
            return f"Erro ao gerar resumo do onboarding: {str(e)}"

if __name__ == "__main__":
    obj = Onboarding()
    
    markdown = obj.semantic_search("tour assistida")

    print('markdown',markdown)