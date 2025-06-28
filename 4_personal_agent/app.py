from openai import OpenAI
import httpx
import os
import sys
from dotenv import load_dotenv
from utils.google_calendar import GoogleCalendar
from utils.google_gmail import GoogleGmail
from utils.onboarding import Onboarding
from utils.weather import Weather

def main():
    """Main function to initialize the OpenAI client and define the agent's behavior. """

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
    
    # Tool: Google Calendar
    def calendar():
        calendar = GoogleCalendar()
        events = calendar.consult() 
        return events

    # Tool: Google gmail
    def emails():
        reader = GoogleGmail() 
        emails = reader.read_emails(max_results=10, query='is:unread')
        return emails

    # Tool: Onboarding Document
    def onboarding():
        obj = Onboarding()
        # text = obj.read() # Read as plain text
        return obj.read_as_markdown() # Read as markdown

    # Tool: Weather API 
    def weather():
        weather = Weather()
        forecast = weather.get_forecast()
        return weather.process_forecast(forecast, hours=24)

    # Function to call GPT model with messages
    def call_gpt(messages):
        response = client.chat.completions.create(
            model="gpt-4o",   
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
                resultado = emails()
                messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
            elif response.startswith("ACTION: ONBOARDING"):
                topico = response.replace("ACTION: ONBOARDING", "").strip()
                resultado = onboarding()
                messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
            elif response.startswith("ACTION: WEATHER"):
                topico = response.replace("ACTION: WEATHER", "").strip()
                resultado = weather()
                messages.append({"role": "user", "content": f"RESULTADO: {resultado}"})
            else:
                print("O agente não sabe o que fazer. Encerrando.")
                break

    # Exemplo de uso
    # agent("Quais são meus proximos compromissos?")
    # agent("Quais são os ultimos emails recebidos?")
    # agent("Como funciona o processo de onboarding na empresa?")
    # agent("Qual a previsão do tempo?")

if __name__ == "__main__":
    main()