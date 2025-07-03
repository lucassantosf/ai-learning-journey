from openai import OpenAI
import httpx
import os
import sys
import traceback
from dotenv import load_dotenv
from utils.google_calendar import GoogleCalendar
from utils.google_gmail import GoogleGmail
from utils.onboarding import Onboarding
from utils.weather import Weather
from utils.logger import agent_logger

class Agent:
    def __init__(self):
        """Initialize the OpenAI client with minimal error handling."""
        load_dotenv()
        
        # Track tool usage
        self.used_tools = []
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            # Log initialization error
            agent_logger.log_error(
                error_type='initialization_error', 
                error_message='OpenAI API key not found',
                context={'env_check': 'OPENAI_API_KEY missing'}
            )
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env file.")

        try:
            self.client = OpenAI(
                api_key=openai_key,
                http_client=httpx.Client(
                    transport=httpx.HTTPTransport(retries=3)
                )
            )
        except Exception as e:
            # Log client initialization error
            agent_logger.log_error(
                error_type='client_initialization_error', 
                error_message=str(e),
                context={'api_key_present': bool(openai_key)}
            )
            raise
        
    # Tool: Google Calendar
    def calendar(self):
        try:
            calendar = GoogleCalendar()
            events = calendar.consult() 
            self.used_tools.append('calendar')
            return events
        except Exception as e:
            agent_logger.log_error(
                error_type='calendar_tool_error', 
                error_message=str(e)
            )
            return f"Error accessing calendar: {str(e)}"

    # Tool: Google gmail
    def emails(self):
        try:
            reader = GoogleGmail() 
            emails = reader.read_emails(max_results=10, query='is:unread')
            self.used_tools.append('emails')
            return emails
        except Exception as e:
            agent_logger.log_error(
                error_type='email_tool_error', 
                error_message=str(e)
            )
            return f"Error accessing emails: {str(e)}"

    # Tool: Onboarding Document
    def onboarding(self, query=None):
        try:
            # Preprocess query
            if query:
                query = query.strip('[]').strip().lower()

                try:
                    obj = Onboarding()
                except Exception as init_error:
                    return f"Erro de inicialização do onboarding: {str(init_error)}"

                # Attempt semantic search for specific queries
                try:
                    result = obj.semantic_search(query)
                    self.used_tools.append('onboarding_semantic_search')
                except Exception:
                    # Fallback to markdown if semantic search fails
                    result = obj.read_as_markdown()
                    self.used_tools.append('onboarding')
            
            # Ensure non-empty result
            if not result or result.strip() == "":
                result = "Resumo do processo de onboarding não disponível."
            
            return result
        
        except Exception as e:
            agent_logger.log_error(
                error_type='onboarding_error', 
                error_message=str(e)
            )
            return f"Erro inesperado ao acessar documentos de onboarding: {str(e)}"

    # Tool: Weather API 
    def weather(self):
        try:
            weather = Weather()
            forecast = weather.get_forecast()
            processed_forecast = weather.process_forecast(forecast, hours=24)
            self.used_tools.append('weather')
            return processed_forecast
        except Exception as e:
            agent_logger.log_error(
                error_type='weather_tool_error', 
                error_message=str(e)
            )
            return f"Error accessing weather information: {str(e)}"

    # Function to call GPT model with messages
    def call_gpt(self, messages):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",   
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            agent_logger.log_error(
                error_type='gpt_call_error', 
                error_message=str(e),
                context={'model': 'gpt-4o'}
            )
            raise

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
                - For Onboarding: 'ACTION: ONBOARDING <QUERY>'
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
            try:
                response = self.call_gpt(messages)
                print("\nAgent:", response)
                messages.append({"role": "assistant", "content": response})

                if response.startswith("FINAL:"):
                    return response.replace("FINAL:", "").strip()
                elif response.startswith("ACTION: CALENDAR"):
                    data = response.replace("ACTION: CALENDAR", "").strip()
                    resultado = self.calendar()
                    messages.append({"role": "user", "content": f"RESULT: {resultado}"})
                elif response.startswith("ACTION: EMAILS"):
                    topic = response.replace("ACTION: EMAILS", "").strip()
                    resultado = self.emails()
                    messages.append({"role": "user", "content": f"RESULT: {resultado}"})
                elif response.startswith("ACTION: ONBOARDING"):
                    # Extract query for semantic search
                    query = response.replace("ACTION: ONBOARDING", "").strip()
                    print(f"Extracted query: {query}")  # Debug print
                    resultado = self.onboarding(query)
                    messages.append({"role": "user", "content": f"RESULT: {resultado}"})
                elif response.startswith("ACTION: WEATHER"):
                    topic = response.replace("ACTION: WEATHER", "").strip()
                    resultado = self.weather()
                    messages.append({"role": "user", "content": f"RESULT: {resultado}"})
                else:
                    return "The agent doesn't know what to do. Ending."
            except Exception as e:
                agent_logger.log_error(
                    error_type='agent_call_error', 
                    error_message=str(e),
                    context={'user_question': user_question}
                )
                return f"An error occurred: {str(e)}"
