from typing import Dict, List
from langchain_openai import ChatOpenAI


class Planner:
    """
    Usa um modelo LLM (OpenAI) para transformar um prompt do usuário
    em um plano estruturado com passos claros.
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.2
        )

    async def generate_plan(self, prompt: str) -> Dict[str, List[str]]:
        """
        Gera um plano com steps detalhados.
        Retorna estrutura:
        {
            "steps": ["Passo 1 ...", "Passo 2 ..."]
        }
        """

        system_prompt = (
            "Você é um planejador profissional. "
            "Dado um objetivo, você deve gerar um plano curto, claro, objetivo, "
            "composto por uma lista de etapas numeradas. "
            "Cada etapa deve ser direta e começar com um verbo no infinitivo."
        )

        user_prompt = f"Objetivo do usuário: {prompt}\n\nGere um plano com passos curtos e claros."

        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        content = response.content.strip()

        # -------------------------------
        # Extrair steps — simples e robusto
        # -------------------------------
        extracted_steps = []
        for line in content.split("\n"):
            clean = line.strip()

            if not clean:
                continue

            # Aceita:
            # 1. Fazer X
            # 2) Fazer Y
            # - Fazer Z
            # Passo 1: ...
            if (
                clean[0].isdigit()
                or clean.startswith("-")
                or clean.lower().startswith("passo")
            ):
                # Remove prefixos
                clean = clean.lstrip("-").strip()
                clean = clean.replace("Passo", "").replace(":", "").strip()
                # Remove "1." ou "1)" ou "1 -"
                while clean and (clean[0].isdigit() or clean[0] in [".", ")", "-"]):
                    clean = clean[1:].strip()

            extracted_steps.append(clean)

        # Garantir que haja pelo menos um passo
        if not extracted_steps:
            extracted_steps = ["Analisar objetivo.", "Criar passos apropriados.", "Executar plano."]

        return {"steps": extracted_steps}