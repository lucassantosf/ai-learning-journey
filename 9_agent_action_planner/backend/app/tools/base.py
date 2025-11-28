from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class BaseTool(ABC):
    """
    Interface base para ferramentas utilizadas pelo Executor.
    Uma ferramenta recebe um texto/descrição e retorna qualquer resultado serializável.
    """

    name: str = "base_tool"
    description: str = "Ferramenta genérica sem implementação."

    @abstractmethod
    async def run(self, input_text: str) -> Any:
        """
        Executa a ferramenta.

        `input_text` é a descrição do step.
        """
        pass


class ToolRegistry:
    """
    Registry simples para armazenar ferramentas disponíveis.
    O Executor consulta este registry para descobrir e executar ferramentas.
    """

    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool):
        """Registra uma ferramenta baseada no atributo tool.name."""
        cls._tools[tool.name.lower()] = tool

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        """Retorna uma ferramenta pelo nome (case-insensitive)."""
        return cls._tools.get(name.lower())

    @classmethod
    def all(cls) -> Dict[str, BaseTool]:
        """Retorna todas as ferramentas registradas."""
        return cls._tools