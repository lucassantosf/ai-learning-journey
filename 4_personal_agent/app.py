from openai import OpenAI
import httpx
import os
import sys
from dotenv import load_dotenv
from utils.google_calendar import GoogleCalendar
from utils.google_gmail import GoogleGmail
from utils.onboarding import Onboarding
from utils.weather import Weather

class Agent:
    def __init__(self):
        """Initialize the OpenAI client with minimal error handling."""
        load_dotenv()
        
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
                self.client = OpenAI(
                    api_key=openai_key,
                    http_client=http_client
                )
                
                # Perform a quick test to validate the client
                try:
                    self.client.models.list()
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
    def calendar(self):
        calendar = GoogleCalendar()
        events = calendar.consult() 
        return events

    # Tool: Google gmail
    def emails(self):
        reader = GoogleGmail() 
        emails = reader.read_emails(max_results=10, query='is:unread')
        return emails

    # Tool: Onboarding Document
    def onboarding(self):
        obj = Onboarding()
        # text = obj.read() # Read as plain text
        return obj.read_as_markdown() # Read as markdown

    # Tool: Weather API 
    def weather(self):
        weather = Weather()
        forecast = weather.get_forecast()
        return weather.process_forecast(forecast, hours=24)

    # Function to call GPT model with messages
    def call_gpt(self,messages):
        response = self.client.chat.completions.create(
            model="gpt-4o",   
            messages=messages
        )
        return response.choices[0].message.content

    def call(self, user_question):
        messages = [
            {"role": "system", "content": """You are an advanced AI agent with four specialized tools. 
                Your primary objective is to understand the user's intent and provide the most relevant information using these tools:
                1. Personal Calendar Tool
                - Provides comprehensive event and schedule information
                - Can retrieve past and upcoming events
                - Useful for scheduling, planning, and time management

                2. Email Reader Tool
                - Accesses and summarizes recent unread emails
                - Extracts key information from email communications
                - Helps users stay informed about their correspondence

                3. Onboarding Information Tool
                - Retrieves and presents organizational onboarding documents
                - Offers insights into company policies, procedures, and guidelines
                - Supports new team members in understanding their work environment

                4. Weather Forecasting Tool
                - Delivers current and upcoming weather information
                - Provides detailed meteorological data for planning
                - Helps users prepare for various weather conditions

                Interaction Guidelines:
                - If a tool is needed, use the specific ACTION prefix
                - For Calendar: 'ACTION: CALENDAR'
                - For Emails: 'ACTION: EMAILS'
                - For Onboarding: 'ACTION: ONBOARDING'
                - For Weather: 'ACTION: WEATHER'
                - When you have a complete answer, use 'FINAL: <answer>'

                Special Instructions:
                - Be concise and direct in your responses
                - Focus on providing the most relevant information
                - If a request involves multiple tools, use them strategically
                - Always aim to fully address the user's query"""},
            {"role": "user", "content": user_question}
        ]

        while True:
            response = self.call_gpt(messages)
            print("\nAgent:", response)
            messages.append({"role": "assistant", "content": response})

            if response.startswith("FINAL:"):
                # print("\nAgent:", response.replace("FINAL:", "").strip())
                return response.replace('FINAL:', '').strip()
                break
            elif response.startswith("ACTION: CALENDAR"):
                data = response.replace("ACTION: CALENDAR", "").strip()
                resultado = self.calendar()
                messages.append({"role": "user", "content": f"RESULT: {resultado}"})
            elif response.startswith("ACTION: EMAILS"):
                topic = response.replace("ACTION: EMAILS", "").strip()
                resultado = self.emails()
                messages.append({"role": "user", "content": f"RESULT: {resultado}"})
            elif response.startswith("ACTION: ONBOARDING"):
                topic = response.replace("ACTION: ONBOARDING", "").strip()
                resultado = self.onboarding()
                messages.append({"role": "user", "content": f"RESULT: {resultado}"})
            elif response.startswith("ACTION: WEATHER"):
                topic = response.replace("ACTION: WEATHER", "").strip()
                resultado = self.weather()
                messages.append({"role": "user", "content": f"RESULT: {resultado}"})
            else:
                return "The agent doesn't know what to do. Ending."
                break
