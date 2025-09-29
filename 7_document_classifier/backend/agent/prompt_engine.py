from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PromptEngine:
    def __init__(self, model_name="gpt-4o-mini"):
        self.client = OpenAI()
        self.model_name = model_name
        self.prompts = {
            "resume": """
                Você é um extrator de informações de currículos.
                Extraia os seguintes campos do texto e retorne em JSON:
                - nome completo
                - email
                - telefone
                - habilidades
                - última experiência profissional

                Texto: """ + "{text}"
            ,
            "invoice": """
                Você é um extrator de informações de notas fiscais.
                Extraia e retorne em JSON:
                - número da nota
                - CNPJ
                - valor total
                - data de emissão

                Texto: """ + "{text}"
            ,
            "contract": """
                Você é um extrator de informações de contratos.
                Extraia e retorne em JSON:
                - partes envolvidas
                - data de assinatura
                - valor
                - vigência

                Texto: """ + "{text}"
        }

    def extract(self, category: str, text: str) -> dict:
        if category not in self.prompts:
            raise ValueError(f"Categoria não suportada: {category}")

        prompt = self.prompts[category].format(text=text)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        raw_output = response.choices[0].message.content
        return raw_output