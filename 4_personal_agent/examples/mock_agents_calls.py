from openai import OpenAI
import httpx
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API key with error checking
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    print("Error: OPENAI_API_KEY not found in .env file.")
    print("Please set the OPENAI_API_KEY in your .env file.")
    sys.exit(1)

# Create a custom httpx client without proxies
try:
    http_client = httpx.Client(
        transport=httpx.HTTPTransport(
            retries=3,  # Optional: add retry mechanism
        )
    )

    # Initialize OpenAI client with error handling
    try:
        client = OpenAI(
            api_key=openai_key,
            http_client=http_client
        )
        
        # Perform a quick test to validate the client
        try:
            client.models.list()
            print("OpenAI client successfully initialized and authenticated.")
        except Exception as auth_error:
            print(f"Authentication error: {auth_error}")
            print("Please check your API key and network connection.")
            sys.exit(1)
    
    except Exception as init_error:
        print(f"Error initializing OpenAI client: {init_error}")
        sys.exit(1)

except Exception as client_error:
    print(f"Error creating HTTP client: {client_error}")
    sys.exit(1)
 
# Ferramenta: Consulta agenda
def consultar_agenda(data):
    print(f"Consultando agenda para a data: {data}")
    if data == "2025-06-24":
        return "Reunião com o time de IA às 14h."
    else:
        return "Nenhum compromisso encontrado para essa data."

# Ferramenta: Consulta manual
def consultar_manual(topico):
    manuais = {
        "reset senha": "Para resetar sua senha, acesse Configurações > Segurança > Redefinir senha.",
        "ligar dispositivo": "Para ligar o dispositivo, pressione o botão de energia por 3 segundos."
    }
    return manuais.get(topico.lower(), "Manual não encontrado para esse tópico.")

# Ferramenta: Consulta documentação interna
def consultar_documentacao(topico):
    docs = {
        "processo de onboarding": "O processo de onboarding dura 7 dias e inclui integração com o time e treinamentos.",
        "política de férias": "A política de férias permite até 30 dias por ano, com aviso prévio de 30 dias."
    }
    return docs.get(topico.lower(), "Documentação não encontrada para esse tópico.")

def call_gpt(messages):
    response = client.chat.completions.create(
        model="gpt-4o",  # ou gpt-4-turbo ou outro modelo
        messages=messages
    )
    return response.choices[0].message.content

def agent(user_question):
    messages = [
        {"role": "system", "content": """Você é um agente que pode acessar três ferramentas:
            1. Agenda pessoal: use 'ACTION: AGENDA <data>'
            e.g. ACTION: AGENDA 2025-06-24 para consultar compromissos.
            2. Manuais: use 'ACTION: MANUAL <tópico>
            e.g. ACTION: MANUAL reset senha para consultar o manual de reset de senha.'
            3. Documentação interna: use 'ACTION: DOCUMENTACAO <tópico>
            e.g. ACTION: DOCUMENTACAO politica de ferias para consultar a documentação interna.'
            Quando tiver a resposta final, responda com 'FINAL ANSWER: <resposta>'."""},
        {"role": "user", "content": user_question}
    ]

    while True:
        response = call_gpt(messages)
        print("\nAgent:", response)
        messages.append({"role": "assistant", "content": response})

        if response.startswith("FINAL ANSWER:"):
            print("\nResposta Final:", response.replace("FINAL ANSWER:", "").strip())
            break
        elif response.startswith("ACTION: AGENDA"):
            data = response.replace("ACTION: AGENDA", "").strip()
            resultado = consultar_agenda(data)
            print("Agenda consultada:", resultado)
            messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
        elif response.startswith("ACTION: MANUAL"):
            topico = response.replace("ACTION: MANUAL", "").strip()
            resultado = consultar_manual(topico)
            print("Manual consultado:", resultado)
            messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
        elif response.startswith("ACTION: DOCUMENTACAO"):
            topico = response.replace("ACTION: DOCUMENTACAO", "").strip()
            resultado = consultar_documentacao(topico)
            print("Documentação consultada:", resultado)
            messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
        else:
            print("O agente não sabe o que fazer. Encerrando.")
            break

# Exemplo de uso0
agent("Tenho algum compromisso hoje? 2025-06-24")
# Você pode testar também:
# agent("Como faço para resetar a senha?")
# agent("Qual é a política de férias da empresa?")
