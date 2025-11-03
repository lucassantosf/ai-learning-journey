# src/agents/agent_manager.py

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from src.retrieval.retriever import Retriever
from src.core.logger import log_info
from src.agents.tools import build_tools   

class AgentManager:
    """
    Agente com ferramentas (tools) baseadas no LlamaIndex.
    Capaz de raciocinar em múltiplas etapas (multi-hop).
    """

    def __init__(self, retriever: Retriever, model_name: str = "gpt-4o-mini"):
        self.retriever = retriever
        self.model_name = model_name
        self.llm = OpenAI(model=model_name)

        # Carrega todas as tools a partir do arquivo centralizado
        self.tools = build_tools(self.retriever)

        # Cria o agente com as ferramentas registradas
        self.agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=self.llm,
            verbose=True
        )

    def ask(self, question: str):
        log_info(f"🤖 Pergunta recebida pelo agente: {question}")
        response = self.agent.chat(question)
        return response.response