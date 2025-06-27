from openai import OpenAI
import httpx
import os
import sys
from dotenv import load_dotenv
from utils.google_calendar import GoogleCalendar

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
 
# Ferramenta: Consulta Google Calendar
def calendar():
    calendar = GoogleCalendar()
    events = calendar.consult() 
    return events

# Ferramenta: Consulta manual
def emails():
    manuais = {
        "reset senha": "Para resetar sua senha, acesse Configurações > Segurança > Redefinir senha.",
        "ligar dispositivo": "Para ligar o dispositivo, pressione o botão de energia por 3 segundos."
    }
    return manuais.get(topico.lower(), "Manual não encontrado para esse tópico.")

# Ferramenta: Consulta documentação interna
def onboarding():
    docs = {
        "processo de onboarding": "O processo de onboarding dura 7 dias e inclui integração com o time e treinamentos.",
        "política de férias": "A política de férias permite até 30 dias por ano, com aviso prévio de 30 dias."
    }
    return docs.get(topico.lower(), "Documentação não encontrada para esse tópico.")

# Ferramenta: Consulta documentação interna
def weather():
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
        {"role": "system", "content": """Você é um agente que pode acessar quatro ferramentas:
            1. Calendário pessoal: use 'ACTION: CALENDAR'
            2. Ler Emails: use 'ACTION: EMAILS 
            3. Ler Onboarding: use 'ACTION: ONBOARDING
            4. Ler Weather: use 'ACTION: WEATHER 
            Quando tiver a resposta final, responda com 'FINAL: <resposta>'."""},
        {"role": "user", "content": user_question}
    ]

    while True:
        response = call_gpt(messages)
        # print("\nAgent:", response)
        messages.append({"role": "assistant", "content": response})

        if response.startswith("FINAL:"):
            print("\nAgent:", response.replace("FINAL:", "").strip())
            break
        elif response.startswith("ACTION: CALENDAR"):
            data = response.replace("ACTION: CALENDAR", "").strip()
            resultado = calendar()
            messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
        elif response.startswith("ACTION: EMAILS"):
            topico = response.replace("ACTION: EMAILS", "").strip()
            resultado = consultar_manual(topico)
            print("Manual consultado:", resultado)
            messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
        elif response.startswith("ACTION: ONBOARDING"):
            topico = response.replace("ACTION: ONBOARDING", "").strip()
            resultado = consultar_documentacao(topico)
            print("Documentação consultada:", resultado)
            messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
        elif response.startswith("ACTION: WEATHER"):
            topico = response.replace("ACTION: WEATHER", "").strip()
            resultado = consultar_documentacao(topico)
            print("Documentação consultada:", resultado)
            messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
        else:
            print("O agente não sabe o que fazer. Encerrando.")
            break

# Exemplo de uso0
agent("Quais são meus proximos compromissos?")
# Você pode testar também:
# agent("Como faço para resetar a senha?")
# agent("Qual é a política de férias da empresa?")
