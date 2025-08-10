import os
import re
import httpx
from dotenv import load_dotenv
import ollama
import google.generativeai as genai
from openai import OpenAI

from src.agent import tools
from src.agent.memory import Memory
from src.utils.logger import setup_logger, log_execution_time

class Agent:
    def __init__(self, provider='openai'): 
        load_dotenv()
        self.logger = setup_logger()
        self.logger.info(f"🔧 Initializing Agent with provider: {provider}")
        
        self.used_tools = []
        self._load_tools()
        self.memory = Memory(max_messages=30)

        if provider == 'openai':
            self._setup_openai()
        elif provider == 'ollama':
            self._setup_ollama()
        elif provider == 'gemini':
            self._setup_gemini()
        else:
            raise ValueError(f"Unsupported provider: {provider}. Choose 'openai', 'ollama', or 'gemini'.")

    def _load_tools(self):
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
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        
        try:
            self.client = OpenAI(
                api_key=openai_key,
                http_client=httpx.Client(transport=httpx.HTTPTransport(retries=3))
            )
            self.provider = 'openai'
            self.logger.info("OpenAI client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def _setup_ollama(self):
        try:
            ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': 'Hello'}])
            self.client = ollama
            self.provider = 'ollama'
            self.logger.info("Ollama client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama client: {e}")
            raise

    def _setup_gemini(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("Gemini API key not found in environment variables.")
        
        try:
            genai.configure(api_key=gemini_key)
            self.client = genai.GenerativeModel('gemini-2.0-flash')
            self.provider = 'gemini'
            self.logger.info("Gemini client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")
            raise

    def _extract_action(self, response: str) -> str | None:
        match = re.search(r"ACTION:\s*(.+)", response)
        if match:
            action = match.group(1).strip()
            self.logger.info(f"Action detected: {action}")
            return action
        self.logger.debug("No action detected")
        return None

    def _run_tool(self, action_str: str):
        self.logger.info(f"⚙️ Executing tool: {action_str}")
        try:
            result = eval(action_str, {}, self.TOOLS)
            self.used_tools.append(action_str)
            self.logger.info(f"Tool executed successfully: {action_str}")
            return result
        except Exception as e:
            error_msg = f"Error running tool {action_str}: {e}"
            self.logger.error(error_msg)
            return error_msg

    def _send_to_model(self, messages):
        self.logger.debug(f"Sending messages to model: {messages}")
        try:
            if self.provider == 'openai':
                content = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                ).choices[0].message.content
            elif self.provider == 'ollama':
                content = self.client.chat(
                    model='llama3.2:1b',
                    messages=messages
                )['message']['content']
            elif self.provider == 'gemini':
                combined = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
                content = self.client.generate_content(combined).text

            self.logger.debug(f"Model response: {content}")
            return content

        except Exception as e:
            self.logger.error(f"Error sending message to model: {e}")
            raise

    @log_execution_time
    def call(self, user_question):
        self.logger.info(f"User asked: {user_question}")
        self.used_tools = []  # Reset used tools for each call
        self.memory.add_message("system", self._system_prompt())
        self.memory.add_message("user", user_question)

        max_iterations = 3  # Limit iterations to prevent infinite loops
        current_iteration = 0

        while current_iteration < max_iterations:
            messages = self.memory.get_context()
            response = self._send_to_model(messages)
            self.memory.add_message("assistant", response)

            action = self._extract_action(response)
            if action:
                # Check if this exact action has not been used before
                if action not in self.used_tools:
                    tool_result = self._run_tool(action)
                    self.memory.add_message("function", str(tool_result), name=action)
                else:
                    self.logger.info(f"Skipping repeated action: {action}")
                    break
            else:
                self.logger.info(f"Final response to user: {response}")
                return response

            current_iteration += 1

        if current_iteration == max_iterations:
            self.logger.warning("Maximum iterations reached. Stopping execution.")
            return "Não foi possível concluir a tarefa completamente."

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
          IMPORTANT: Do NOT ask for a product ID. The system automatically generates a unique ID.
        
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
           - When adding a product, focus on essential details:
             * Name (mandatory)
             * Price (mandatory)
           - Stock quantity is NOT required during initial product registration
             * Inventory will be managed separately through dedicated tools
             * Initial stock can be zero or left unspecified
           - Use unique product IDs for identification
           - Check inventory implications when modifying products later

        2. Inventory Management:
           - Before generating orders, verify inventory levels
           - Use update_inventory() to adjust stock
           - Prevent order generation if stock is insufficient
           - Track inventory changes meticulously

        3. Order Processing:
           - MANDATORY: Collect user identification BEFORE generating any order
             * Require full name (customer_name)
             * Require unique identifier (user_id: CPF, email, or phone)
           - Generate orders ONLY after user identification is confirmed
           - Validate each item's availability before order creation
           - Include customer_name and user_id in order generation
           - Use rating system to collect customer feedback
           - Reject order generation if user identification is incomplete

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

        SPECIAL INSTRUCTIONS FOR PRODUCT UPDATE:
        - When updating a product, first list all products
        - Find the product by its name
        - Use the found product's ID for updating
        - Do NOT ask the user for the product ID
        - Automatically handle product updates based on the product name

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
