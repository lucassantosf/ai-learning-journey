from openai import OpenAI
from src.agent import tools, memory
from dotenv import load_dotenv

class Agent:
    def __init__(self):
        """Initialize the OpenAI client with minimal error handling."""
        load_dotenv()
        
        # Track tool usage
        self.used_tools = []
        
        openai_key = os.getenv("OPENAI_API_KEY") 

        try:
            self.client = OpenAI(
                api_key=openai_key,
                http_client=httpx.Client(
                    transport=httpx.HTTPTransport(retries=3)
                )
            )
        except Exception as e:
            raise
      
    def call(self, user_question):
        messages = [
            {"role": "system", "content": """You are an advanced AI agent with specialized tools for our Ecommerce. 
                Your primary objective is to understand the user's intent and provide the most relevant information using these tools:
                1. List Products Tool
                2. Create Order Tool
                3. Show Order Tool
                4. Evaluate Order Tool
                
                Special Instructions:
                - Be concise and direct in your responses
                - Focus on providing the most relevant information
                - If a request involves multiple tools, use them strategically
                - Always aim to fully address the user's query"""},
            {"role": "user", "content": user_question}
        ] 
