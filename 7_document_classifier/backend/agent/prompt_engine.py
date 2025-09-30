import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PromptEngine:
    def __init__(self, model_name="gpt-4o-mini"):
        self.client = OpenAI()
        self.model_name = model_name
        
        # Prompts por categoria com few-shot examples
        self.prompts = {
            "resumes": """
                Você é um extrator de informações de currículos.
                Sempre responda em JSON válido.

                Exemplo:
                Texto: "Maria Silva - Email: maria@email.com - Tel: (11) 99999-0000
                Experiência: Desenvolvedora Backend na Yetz (2020-2023).
                Habilidades: Python, SQL, Docker."
                
                Saída esperada:
                {{
                    "nome_completo": "Maria Silva",
                    "email": "maria@email.com",
                    "telefone": "(11) 99999-0000",
                    "habilidades": ["Python", "SQL", "Docker"],
                    "ultima_experiencia_profissional": "Desenvolvedora Backend na Yetz (2020-2023)"
                }}

                Agora extraia do seguinte texto real:
                {text}
            """,

            "invoices": """
                Você é um extrator de informações de notas fiscais.
                Sempre responda em JSON válido.

                Exemplo:
                Texto: "Nota Fiscal nº 12345 emitida por Empresa ABC LTDA - CNPJ 12.345.678/0001-99,
                no valor total de R$ 4.500,00, em 05/09/2023."
                
                Saída esperada:
                {{
                    "numero_nota": "12345",
                    "cnpj": "12.345.678/0001-99",
                    "valor_total": "4500.00",
                    "data_emissao": "2023-09-05"
                }}

                Agora extraia do seguinte texto real:
                {text}
            """,

            "contracts": """
                Você é um extrator de informações de contratos.
                Sempre responda em JSON válido.

                Exemplo:
                Texto: "Contrato firmado entre João Pereira e a Empresa XYZ em 10/01/2022,
                no valor de R$ 100.000,00 com vigência de 24 meses."
                
                Saída esperada:
                {{
                    "partes_envolvidas": ["João Pereira", "Empresa XYZ"],
                    "data_assinatura": "2022-01-10",
                    "valor": "100000.00",
                    "vigencia": "24 meses"
                }}

                Agora extraia do seguinte texto real:
                {text}
            """
        }

    def _clean_json_output(self, raw: str) -> str:
        """
        Remove blocos de markdown (```json ... ```).
        Mantém só o conteúdo interno.
        """
        cleaned = re.sub(r"^```(?:json)?", "", raw.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"```$", "", cleaned.strip())
        return cleaned.strip()

    def extract(self, category: str, text: str) -> dict:
        if category not in self.prompts:
            raise ValueError(f"Categoria não suportada: {category}")

        prompt = self.prompts[category].format(text=text)

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )

        raw_output = response.choices[0].message.content

        # Remove blocos markdown ```json ... ```
        cleaned = re.sub(r"^```json|```$", "", raw_output.strip(), flags=re.MULTILINE).strip()

        # Tenta converter para JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return {"error": "Falha ao converter saída para JSON", "raw_output": raw_output}

        # Valida os dados extraídos
        validated_data = self._validate_extracted(data, category)

        return validated_data
    
    def _validate_extracted(self, data: dict, category: str) -> dict:
        """
        Valida campos específicos por categoria.
        """
        validated = data.copy()

        if category == "resume":
            email = validated.get("email")
            if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                validated["email"] = None

            telefone = validated.get("telefone")
            if telefone and not re.match(r"[\d\s\-\(\)]+", telefone):
                validated["telefone"] = None

        elif category == "invoice":
            cnpj = validated.get("cnpj")
            if cnpj and not re.match(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", cnpj):
                validated["cnpj"] = None

            data_emissao = validated.get("data_emissao")
            if data_emissao:
                try:
                    datetime.strptime(data_emissao, "%Y-%m-%d")
                except ValueError:
                    validated["data_emissao"] = None

            valor_total = validated.get("valor_total")
            if valor_total is not None:
                try:
                    validated["valor_total"] = float(valor_total)
                except ValueError:
                    validated["valor_total"] = None

        elif category == "contract":
            data_assinatura = validated.get("data_assinatura")
            if data_assinatura:
                try:
                    datetime.strptime(data_assinatura, "%Y-%m-%d")
                except ValueError:
                    validated["data_assinatura"] = None

            valor = validated.get("valor")
            if valor is not None:
                try:
                    validated["valor"] = float(valor)
                except ValueError:
                    validated["valor"] = None

        return validated