import os
import httpx
from dotenv import load_dotenv

# LLM Providers
from openai import OpenAI
import ollama
import google.generativeai as genai
import re
from src.agent import tools  # ← importa suas funções reais

class Agent:
    def __init__(self, provider='openai'): 
        load_dotenv()
        self.used_tools = []
        self._load_tools()
        
        # Set up the appropriate client based on the provider
        if provider == 'openai':
            self._setup_openai()
        elif provider == 'ollama':
            self._setup_ollama()
        elif provider == 'gemini':
            self._setup_gemini()
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'openai', 'ollama', or 'gemini'.")

    def _load_tools(self):
        """Dicionário de funções que o agente pode executar"""
        self.TOOLS = {
            "list_products": tools.list_products,
            "get_product": tools.get_product,
            "add_product": tools.add_product,
            "update_product": tools.update_product,
            "delete_product": tools.delete_product,
            "list_inventory": tools.list_inventory,
            "update_inventory": tools.update_inventory,
            "generate_order": tools.generate_order,
            "get_order": tools.get_order,
            "list_orders": tools.list_orders,
            "rate_order": tools.rate_order,
        }

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

    def _extract_action(self, response: str) -> str | None:
        match = re.search(r"ACTION:\s*(.+)", response)
        return match.group(1).strip() if match else None

    def _run_tool(self, action_str: str):
        try:
            result = eval(action_str, {}, self.TOOLS)
            self.used_tools.append(action_str)
            return result
        except Exception as e:
            return f"❌ Erro ao executar {action_str}: {str(e)}"

    def _send_to_model(self, messages):
        if self.provider == 'openai':
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            ).choices[0].message.content

        elif self.provider == 'ollama':
            return self.client.chat(
                model='llama3.2:1b',
                messages=messages
            )['message']['content']

        elif self.provider == 'gemini':
            combined_message = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
            return self.client.generate_content(combined_message).text
    
    def call(self, user_question):
        system_message = self._system_prompt()
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_question}
        ]

        while True:
            response = self._send_to_model(messages)
            action = self._extract_action(response)

            if action:
                tool_result = self._run_tool(action)
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "function",
                    "name": action,
                    "content": str(tool_result)
                })
            else:
                return response

    def _system_prompt(self):
        # Prepare system message
        return """You are an advanced AI agent for an E-commerce system with comprehensive tools. 
        Your goal is to assist users by leveraging the following tools:

        PRODUCT MANAGEMENT TOOLS:
        - list_products(): Returns all available products
          Response Format: A friendly, emoji-enhanced list of products with:
          • Product name
          • Price with "R$" prefix
          • Optional description
          • Quantity and rating information
        
        - get_product(product_id): Retrieves details of a specific product
          Response Format: "Product Details: ID, Name, Price, Quantity, Average Rating"
        
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

        Interaction Guidelines:
        - If a tool is needed, use the specific ACTION prefix
        - For Listing Products: 'ACTION: list_products()'
        - For Product Details: 'ACTION: get_product(product_id)'
        - For Adding Products: 'ACTION: add_product(product)'
        - For Updating Products: 'ACTION: update_product(product)'
        - For Deleting Products: 'ACTION: delete_product(product_id)'
        
        DETAILED TOOL INTERACTION GUIDELINES:

        1. Product Management:
           - Always validate product existence before operations
           - When adding a product, provide complete Product object
           - Use unique product IDs for identification
           - Check inventory implications when modifying products

        2. Inventory Management:
           - Before generating orders, verify inventory levels
           - Use update_inventory() to adjust stock
           - Prevent order generation if stock is insufficient
           - Track inventory changes meticulously

        3. Order Processing:
           - Generate orders with complete OrderItem details
           - Include customer_id when possible
           - Validate each item's availability before order creation
           - Use rating system to collect customer feedback

        4. Error Handling Protocols:
           - Catch and handle ValueError for inventory/product issues
           - Provide clear error messages to users
           - Suggest alternative actions when primary action fails

        5. Tool Usage Patterns:
           a) Listing Resources:
              - list_products(): Shows all available products
              - list_orders(): Displays complete order history
              - list_inventory(): Reveals current stock levels

           b) Retrieval Operations:
              - get_product(product_id): Fetch specific product details
              - get_order(order_id): Retrieve order specifics

           c) Modification Operations:
              - add_product(product): Introduce new products
              - update_product(product): Modify existing product info
              - update_inventory(inventory): Adjust stock levels
              - rate_order(order_id, rating): Provide order feedback

        6. Recommended Workflow:
           - Always check product availability
           - Validate inventory before order generation
           - Confirm order details before processing
           - Update inventory post-order
           - Collect and process order ratings

        Example Complex Interaction:
        User: "I want to order 2 units of product 'laptop', check availability first"
        AI: 
        ACTION: get_product('laptop')
        ACTION: list_inventory()
        [Validates product exists and has sufficient stock]
        ACTION: generate_order([OrderItem(product_id='laptop', quantity=2)])
        ACTION: rate_order(new_order.id, 5)  # Optional post-order rating

        Language Support: Portuguese ONLY
        Precision: Maximum accuracy in tool interactions
        Flexibility: Adapt to various user request styles"""
