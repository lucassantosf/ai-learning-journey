def build_classify_prompt(question: str) -> str:
    """
    Prompt de classificação com few-shot examples.
    O modelo decide quais ferramentas devem ser usadas com base no tipo de pergunta.
    """
    return f"""
Você é um agente jurídico que decide quais ferramentas usar para responder perguntas sobre contratos.

Ferramentas disponíveis:
- summarize_document → resumir um ou mais contratos
- extract_legal_clauses → extrair cláusulas específicas (ex: prazos, pagamento, rescisão)
- compare_documents → comparar contratos ou cláusulas entre eles
- basic_rag → perguntas gerais que não exigem comparação ou extração

Veja exemplos de classificação:

### Exemplo 1
Pergunta: "Resuma o contrato da Inovação Digital com a Agência Alpha."
Resposta esperada:
{{
  "tools": ["summarize_document"],
  "rationale": "A pergunta pede apenas um resumo geral do contrato."
}}

### Exemplo 2
Pergunta: "Quais são as cláusulas sobre rescisão no contrato da Inovação Digital?"
Resposta esperada:
{{
  "tools": ["extract_legal_clauses"],
  "rationale": "O usuário quer informações específicas de cláusulas."
}}

### Exemplo 3
Pergunta: "Compare os prazos e pagamentos entre o contrato A e B."
Resposta esperada:
{{
  "tools": ["extract_legal_clauses", "compare_documents"],
  "rationale": "É preciso extrair cláusulas e depois comparar contratos."
}}

### Exemplo 4
Pergunta: "Qual contrato tem mais garantias ao contratante?"
Resposta esperada:
{{
  "tools": ["extract_legal_clauses", "compare_documents"],
  "rationale": "A pergunta requer comparar contratos e analisar cláusulas."
}}

Agora, classifique a seguinte pergunta:
{question}

Responda apenas em JSON no formato:
{{"tools": [...], "rationale": "..."}}
"""