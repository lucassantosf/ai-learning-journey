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
        Estrutura:
        {
            "steps": ["Passo 1 ...", "Passo 2 ..."]
        }
        """

        system_prompt = (
            "Você é um planejador extremamente objetivo. "
            "Transforme o objetivo do usuário em uma lista de passos numerados, "
            "curtos, claros e sempre iniciados com um verbo no infinitivo. "
            "Responda apenas com a lista de etapas, uma por linha."
        )

        user_prompt = (
            f"Objetivo do usuário: {prompt}\n\n"
            "Gere um plano estruturado, com etapas claras, diretas e no infinitivo. "
            "Uma etapa por linha."
        )

        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])

        content = (response.content or "").strip()

        # ---------------------------------------
        # Extração robusta de steps
        # ---------------------------------------
        extracted_steps: List[str] = []

        for raw in content.split("\n"):
            line = raw.strip()
            if not line:
                continue

            # Detecta linhas de passo válidas
            is_step = (
                line[0].isdigit() or
                line.startswith("-") or
                line.lower().startswith("passo")
            )

            # Se o modelo gerou algo fora do padrão, ainda assim tentamos aproveitar
            if not is_step:
                # Se não parece passo, mas contém verbo no infinitivo → aceita
                if " " in line and line.split()[0].endswith("r"):
                    extracted_steps.append(line)
                continue

            # Remove prefixos comuns
            clean = line
            clean = clean.lstrip("-").strip()
            clean = clean.replace("Passo", "").replace("passo", "")
            clean = clean.replace(":", "").strip()

            # Remove padrões como "1.", "1)", "1-" etc
            while clean and (
                clean[0].isdigit() or clean[0] in [".", ")", "-", ":"]
            ):
                clean = clean[1:].strip()

            # Final sanitização
            if clean:
                extracted_steps.append(clean)

        # ---------------------------------------
        # Garantia absoluta de que sempre haverá passos
        # ---------------------------------------
        if not extracted_steps:
            extracted_steps = [
                "Analisar objetivo.",
                "Criar etapas apropriadas.",
                "Executar plano."
            ]

        # Remover duplicatas mantendo ordem
        final_steps = []
        seen = set()
        for s in extracted_steps:
            if s not in seen:
                seen.add(s)
                final_steps.append(s)

        return {"steps": final_steps}