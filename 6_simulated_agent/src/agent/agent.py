import os
import httpx
from dotenv import load_dotenv

# LLM Providers
from openai import OpenAI
import ollama
import google.generativeai as genai

class Agent:
    def __init__(self, provider='openai'):
        """
        Initialize the Agent with a specific language model provider.
        
        Args:
            provider (str): The language model provider to use. 
                            Options: 'openai', 'ollama', 'gemini'
        """
        load_dotenv()
        
        # Track tool usage
        self.used_tools = []
        
        # Set up the appropriate client based on the provider
        if provider == 'openai':
            self._setup_openai()
        elif provider == 'ollama':
            self._setup_ollama()
        elif provider == 'gemini':
            self._setup_gemini()
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'openai', 'ollama', or 'gemini'.")

    def _setup_openai(self):
        """Set up OpenAI client."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        
        try:
            self.client = OpenAI(
                api_key=openai_key,
                http_client=httpx.Client(
                    transport=httpx.HTTPTransport(retries=3)
                )
            )
            self.provider = 'openai'
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

    def _setup_ollama(self):
        """Set up Ollama client."""
        try:
            # Verify Ollama is running and the model is available
            ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': 'Hello'}])
            self.client = ollama
            self.provider = 'ollama'
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Ollama client: {e}")

    def _setup_gemini(self):
        """Set up Google Gemini client."""
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Gemini API key not found in environment variables.")
        
        try:
            genai.configure(api_key=gemini_key)
            self.client = genai.GenerativeModel('gemini-2.0-flash')
            self.provider = 'gemini'
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini client: {e}")

    def call(self, user_question):
        """
        Process user question using the selected language model provider.
        
        Args:
            user_question (str): The user's input query
        
        Returns:
            str: The model's response
        """
        # Prepare system message
        system_message = """You are an advanced AI agent for an E-commerce system with comprehensive tools. 
        Your goal is to assist users by leveraging the following tools:

        PRODUCT MANAGEMENT TOOLS:
        - list_products(): Returns all available products
          Response Format: "Product List: [ID: product_name, Price: X, Description: Y]"
        
        - get_product(product_id): Retrieves details of a specific product
          Response Format: "Product Details: ID, Name, Price, Description, Stock"
        
        - add_product(product): Add a new product to the catalog
          Response Format: "Product Added Successfully: [Product Details]"
        
        - update_product(product): Modify an existing product
          Response Format: "Product Updated Successfully: [New Product Details]"
        
        - delete_product(product_id): Remove a product from catalog
          Response Format: "Product Deleted Successfully: [Product ID]"

        INVENTORY MANAGEMENT TOOLS:
        - list_inventory(): Shows current stock levels
          Response Format: "Inventory Status: [Product ID: Quantity]"
        
        - update_inventory(inventory): Adjust product stock
          Response Format: "Inventory Updated Successfully: [Product ID, New Quantity]"

        ORDER MANAGEMENT TOOLS:
        - generate_order(items): Create a new order
          Response Format: "Order Created: [Order ID, Total Items, Total Price]"
        
        - get_order(order_id): Retrieve order details
          Response Format: "Order Details: [ID, Items, Total, Date, Status]"
        
        - list_orders(): Show all existing orders
          Response Format: "Order List: [Order ID, Date, Total]"
        
        - rate_order(order_id, rating): Provide order feedback
          Response Format: "Order Rated Successfully: [Order ID, Rating]"

        IMPORTANT GUIDELINES:
        1. Always use the exact function names provided
        2. For function calls, provide clear, concise parameters
        3. If unsure about a request, ask for clarification
        4. Prioritize user intent and provide helpful responses
        5. Handle errors gracefully and suggest alternatives
        6. You can communicate in English or Portuguese

        Example Interaction:
        User: "List all products"
        AI: Calls list_products() and formats the response
        
        User: "Create an order for product ABC"
        AI: Validates product, checks inventory, calls generate_order()"""

        # Handle different providers' chat/completion methods
        if self.provider == 'openai':
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_question}
            ]
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            ).choices[0].message.content
        
        elif self.provider == 'ollama':
            response = self.client.chat(
                model='llama3.2:1b', 
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_question}
                ]
            )['message']['content']
        
        elif self.provider == 'gemini':
            response = self.client.generate_content(
                f"{system_message}\n\nUser query: {user_question}"
            ).text
        
        return response
