from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional


class BaseTool(ABC):
    """
    Interface para ferramentas utilizadas pelo Executor.
    Cada ferramenta deve implementar um método run().
    """

    name: str = "base_tool"
    description: str = "Ferramenta genérica sem implementação."

    @abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Executa a ferramenta."""
        pass


class ToolRegistry:
    """
    Registry simples para armazenar ferramentas disponíveis.
    O Executor consulta este registry para executar ferramentas.
    """

    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool):
        """Registra uma ferramenta baseada no seu atributo name."""
        cls._tools[tool.name] = tool

    @classmethod
    def get(cls, name: str) -> Optional[BaseTool]:
        """Retorna uma ferramenta pelo nome."""
        return cls._tools.get(name)

    @classmethod
    def all(cls) -> Dict[str, BaseTool]:
        """Retorna todas as ferramentas registradas."""
        return cls._tools