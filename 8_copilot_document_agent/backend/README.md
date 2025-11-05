
# 🔍 Visão geral das classes principais e responsabilidades

Here's the updated backend file tree for you to copy:

backend
├── .env
├── .env.example
├── main.py
├── pytest.ini
├── README.md
├── requirements.txt
├── data/
│   ├── faiss_index.bin
│   └── faiss_index.bin.meta.json
├── src
│   ├── __init__.py
│   ├── agents
│   │   ├── __init__.py
│   │   ├── agent_manager.py
│   │   ├── rag_agent.py
│   │   ├── tools.py
│   │   └── prompts
│   │       ├── classify_prompt.py
│   │       ├── final_prompt.py
│   │       └── tool_execution_prompt.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── models.py
│   ├── data
│   │   ├── __init__.py
│   │   └── embedding.py
│   ├── ingestion
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── docx_parser.py
│   │   ├── embedding_generator.py
│   │   ├── ingestion_pipeline.py
│   │   ├── parser_base.py
│   │   ├── pdf_parser.py
│   │   └── text_cleaner.py
│   ├── interfaces
│   │   ├── __init__.py
│   │   └── api_controller.py
│   ├── retrieval
│   │   ├── __init__.py
│   │   ├── faiss_vector_store.py
│   │   └── retriever.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── agents
│   │   │   ├── __init__.py
│   │   │   ├── test_rag_agent.py
│   │   │   └── test_rag_agent_quality.py
│   │   ├── errors
│   │   │   └── test_errors_and_edge_cases.py
│   │   ├── fixtures
│   │   │   ├── __init__.py
│   │   │   ├── test_document.docx
│   │   │   └── test_document.pdf
│   │   ├── ingestion
│   │   │   ├── __init__.py
│   │   │   ├── test_chunker.py
│   │   │   ├── test_document_parser.py
│   │   │   ├── test_docx_parser.py
│   │   │   ├── test_embedding_generator.py
│   │   │   ├── test_ingestion_pipeline.py
│   │   │   ├── test_pdf_parser.py
│   │   │   └── test_text_cleaner.py
│   │   ├── integration
│   │   │   ├── __init__.py
│   │   │   └── test_full_pipeline.py
│   │   └── retrieval
│   │       ├── __init__.py
│   │       ├── test_faiss_retrieval.py
│   │       └── test_retriever.py
│   └── tools
│       └── __init__.py
└── tests
    └── fixtures
        ├── test_document.docx
        └── test_document.pdf

# 🔄 Fluxo geral entre classes

Usuário → APIController.upload()
        → IngestionPipeline.process()
            → PDFParser → TextCleaner → Chunker → EmbeddingGenerator → FaissVectorStore

Usuário → APIController.query()
        → QueryProcessor
            → Retriever (FAISS)
            → LLM (OpenAI)
            → retorna resposta + trechos

Usuário → APIController.agent()
        → AgentExecutor
            → MultiHopAgent
                → Usa Tools (SummarizeTool, CompareDocumentsTool, etc.)

# 🧩 1. Core

Camada base que define entidades e serviços genéricos usados por todo o sistema.

| Classe              | Responsabilidade                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------- |
| **Document**        | Representa um documento carregado (id, nome, tipo, texto limpo, metadados, data de upload). |
| **Chunk**           | Representa um trecho (chunk) do documento que será transformado em embedding.               |
| **EmbeddingVector** | Representa um vetor e seus metadados (texto original, doc_id, posição, embedding).          |
| **Config**          | Lê variáveis do `.env` e mantém as configurações globais (chaves API, caminhos, etc.).      |
| **Logger**          | Wrapper do `rich` para logs coloridos, com níveis (INFO, DEBUG, ERROR).                     |

# 📥 2. Ingestion

Responsável por ler, extrair e preparar documentos para indexação.

| Classe                 | Responsabilidade                                                                                    |
| ---------------------- | --------------------------------------------------------------------------------------------------- |
| **DocumentParser**     | Interface base para parsers (PDF, DOCX, etc.).                                                      |
| **PDFParser**          | Extrai texto e metadados de arquivos PDF (usando `pdfplumber`).                                     |
| **DocxParser**         | Extrai texto e metadados de arquivos DOCX (usando `docx2txt`).                                      |
| **TextCleaner**        | Faz limpeza do texto (remove quebras, espaços duplicados, símbolos).                                |
| **Chunker**            | Divide o texto em blocos com sobreposição de contexto (para embeddings).                            |
| **EmbeddingGenerator** | Converte cada chunk em um embedding (usando modelo OpenAI).                                         |
| **IngestionPipeline**  | Classe orquestradora: recebe o arquivo → chama parser → limpa → chunk → embedding → salva no FAISS. |

# 🧠 3. Retrieval

Responsável por buscar os trechos mais relevantes a partir de uma consulta.

| Classe               | Responsabilidade                                                                              |
| -------------------- | --------------------------------------------------------------------------------------------- |
| **VectorStore**      | Interface para o armazenamento vetorial (inserção, busca, deleção).                           |
| **FaissVectorStore** | Implementação concreta usando FAISS local.                                                    |
| **Retriever**        | Busca os embeddings mais semelhantes (cosine similarity) e retorna chunks relevantes.         |
| **QueryProcessor**   | Coordena a consulta: recebe a pergunta, busca no vetor, formata o contexto e envia ao modelo. |

# 🤖 4. Agents

Responsável por raciocínio multi-etapas e ferramentas inteligentes.

| Classe            | Responsabilidade                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------- |
| **BaseAgent**     | Classe genérica que define interface de raciocínio, ferramenta e execução.                        |
| **RAGAgent**      | Usa o retriever como ferramenta e combina respostas do LLM com citações.                          |
| **MultiHopAgent** | Extende o RAGAgent permitindo múltiplas consultas e combinações (multi-hop QA).                   |
| **AgentExecutor** | Coordena o fluxo: identifica a pergunta → escolhe ferramentas → executa → retorna resposta final. |

# 🛠️ 5. Tools

Ferramentas específicas que o agente pode usar.

| Classe                      | Responsabilidade                                      |
| --------------------------- | ----------------------------------------------------- |
| **SummarizeTool**           | Resume um documento ou conjunto de chunks.            |
| **ExtractLegalClausesTool** | Identifica e extrai cláusulas jurídicas específicas.  |
| **CompareDocumentsTool**    | Compara dois documentos e gera resumo das diferenças. |
| **SearchTool**              | Busca direta em texto bruto ou metadados.             |

# 🌐 6. Interfaces

Camada de entrada/saída (APIs, UI, etc.).

| Classe              | Responsabilidade                                                                 |
| ------------------- | -------------------------------------------------------------------------------- |
| **APIController**   | Define rotas e endpoints (upload, query, agent, feedback).                       |
| **RequestSchemas**  | Define os modelos Pydantic das requisições (UploadRequest, QueryRequest, etc.).  |
| **ResponseSchemas** | Define os modelos das respostas (SuccessResponse, QueryResponse, AgentResponse). |
| **ErrorHandler**    | Middleware para erros e logs padronizados na API.                                |

# 🗃️ 7. Data

Camada de persistência (banco de dados e armazenamento local).

| Classe                  | Responsabilidade                                   |
| ----------------------- | -------------------------------------------------- |
| **Database**            | Inicializa e gerencia conexão com SQLite/Postgres. |
| **DocumentRepository**  | CRUD de documentos.                                |
| **EmbeddingRepository** | CRUD de embeddings.                                |
| **FeedbackRepository**  | Salva e consulta feedbacks de respostas.           |