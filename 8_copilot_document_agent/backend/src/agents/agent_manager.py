from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from openai import OpenAI  # cliente oficial SDK
from src.retrieval.retriever import Retriever
from src.core.logger import log_info
from src.agents.tools import build_tools

class AgentManager:
    """
    Gerenciador do agente com raciocínio multi-hop e uso eficiente de ferramentas.
    - Reutiliza o mesmo client LLM (evita recriar conexões).
    - Configurável para diferentes modos de raciocínio (multi-step / compact).
    """

    def __init__(self, retriever: Retriever, model_name: str = "gpt-4o-mini"):
        self.retriever = retriever
        self.model_name = model_name

        # Cria o cliente LlamaIndex LLM (usado pelo agente principal)
        log_info("🧠 Criando instância do cliente OpenAI (LlamaIndex) para o agente.")
        self.llm = LlamaOpenAI(model=model_name)

        # Cria o cliente oficial da OpenAI (SDK) para as tools
        log_info("⚙️ Criando cliente OpenAI (SDK oficial) para uso interno das tools.")
        self.openai_client = OpenAI()

        # Carrega as ferramentas, compartilhando o cliente
        self.tools = build_tools(self.retriever, shared_client=self.openai_client)

        # Cria o agente com raciocínio ReAct e ferramentas disponíveis
        self.agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )
    

    def ask(self, question: str):
        """
        Envia uma pergunta para o agente e retorna a resposta final.
        """
        log_info(f"🤖 Pergunta recebida pelo agente: {question}")
        response = self.agent.chat(question)
        return response.response