from typing import Optional
from llama_index.core.tools import FunctionTool
from src.core.logger import log_info
from src.retrieval.retriever import Retriever

def build_tools(retriever: Retriever, shared_client=None):
    """
    Retorna a lista de ferramentas (tools) disponíveis para o agente.

    Parâmetros:
    - retriever: instância de Retriever para buscas vetoriais
    - shared_client: cliente OpenAI compartilhado (reutilizado para evitar overhead)
    """

    # -----------------------------
    # Inicialização do cliente LLM compartilhado
    # -----------------------------
    if shared_client:
        log_info("♻️ Usando cliente OpenAI compartilhado para tools.")
        from openai import OpenAI
        client = shared_client
    else:
        log_info("🧠 Criando nova instância local do cliente OpenAI para tools.")
        from openai import OpenAI
        client = OpenAI()

    # -----------------------------
    # Tool 1: Busca em documentos
    # -----------------------------
    def document_search(query: str, top_k: int = 2):
        """Busca informações relevantes nos documentos indexados."""
        log_info(f"🧠 [Tool] document_search: query='{query}', top_k={top_k}")
        results = retriever.search(query, top_k=top_k)
        contexts = [r["text"] for r in results]
        return "\n\n".join(contexts) if contexts else "Nenhum resultado encontrado."

    tool_search = FunctionTool.from_defaults(
        fn=document_search,
        name="document_search",
        description="Busca informações relevantes nos documentos indexados."
    )

    # -----------------------------
    # Tool 2: Resumir documento
    # -----------------------------
    def summarize_document(content: str):
        """Gera um resumo jurídico objetivo do conteúdo."""
        log_info("🧠 [Tool] summarize_document chamada")
        prompt = (
            "Resuma o conteúdo abaixo de forma objetiva e jurídica:\n\n"
            f"{content}"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return completion.choices[0].message.content.strip()

    tool_summarize = FunctionTool.from_defaults(
        fn=summarize_document,
        name="summarize_document",
        description="Gera um resumo jurídico a partir do texto de um documento."
    )

    # -----------------------------
    # Tool 3: Extrair cláusulas legais
    # -----------------------------
    def extract_legal_clauses(content: str):
        """Extrai as cláusulas legais mais relevantes de um contrato."""
        log_info("🧠 [Tool] extract_legal_clauses chamada")
        prompt = (
            "Extraia as cláusulas legais mais relevantes do contrato abaixo "
            "(como pagamento, prazo, rescisão, foro, confidencialidade, etc.):\n\n"
            f"{content}"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return completion.choices[0].message.content.strip()

    tool_extract = FunctionTool.from_defaults(
        fn=extract_legal_clauses,
        name="extract_legal_clauses",
        description="Extrai cláusulas legais importantes de um documento jurídico."
    )

    # -----------------------------
    # Tool 4: Comparar dois documentos
    # -----------------------------
    def compare_documents(doc_a: str, doc_b: Optional[str] = None) -> str:
        """Compara dois documentos jurídicos e destaca diferenças principais."""
        log_info("🧠 [Tool] compare_documents chamada")

        if not doc_b:   
            return "❌ Comparação inválida — segundo documento ausente."
    
        prompt = (
            "Compare os dois documentos abaixo e descreva as principais diferenças "
            "entre suas cláusulas e obrigações:\n\n"
            f"--- Documento A ---\n{doc_a}\n\n--- Documento B ---\n{doc_b}"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return completion.choices[0].message.content.strip()

    tool_compare = FunctionTool.from_defaults(
        fn=compare_documents,
        name="compare_documents",
        description="Compara dois documentos jurídicos e destaca diferenças principais."
    )

    # -----------------------------
    # Retorna todas as tools registradas
    # -----------------------------
    return {
        "document_search": tool_search,
        "summarize_document": tool_summarize,
        "extract_legal_clauses": tool_extract,
        "compare_documents": tool_compare,
    }
