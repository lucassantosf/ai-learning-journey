import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMModel:
    def __init__(self, use_openai=False):
        """
        Initialize the LLM model client.
        
        Args:
            use_openai (bool): Whether to use OpenAI API instead of local Ollama.
        """
        self.use_openai = use_openai
        
        if use_openai:
            # Use OpenAI API
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAI API key is required when use_openai=True")
            
            self.client = OpenAI(api_key=self.api_key)
            self.model_name = "gpt-4o"
        else:
            # Use local Ollama
            self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            self.model_name = "llama3.2:1b"
        
    def generate_completion(self, messages, temperature=0.7):
        """
        Generate a completion using the configured LLM.
        
        Args:
            messages (list): List of message dictionaries with 'role' and 'content' keys.
            temperature (float, optional): Temperature for response generation. Defaults to 0.7.
            
        Returns:
            str: The generated completion text.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content 
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)  # Log the error
            return error_msg
