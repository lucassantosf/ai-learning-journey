import os
import re
import httpx
from dotenv import load_dotenv
import ollama
import google.generativeai as genai
from openai import OpenAI
import concurrent.futures
import signal
import threading
import time

from src.utils.agent_prompt import get_agent_prompt
from src.agent import tools
from src.agent.memory import Memory
from src.utils.logger import setup_logger, log_execution_time

class APICallTracker:
    def __init__(self, max_calls=15, reset_time=900):  # 15 calls per 15 minutes
        self.calls = 0
        self.last_reset = time.time()
        self.max_calls = max_calls
        self.reset_time = reset_time
        self.conversation_calls = 0
        self.max_conversation_calls = 10  # Max calls within a single conversation

    def can_make_call(self, is_new_conversation=False):
        current_time = time.time()
        
        # Reset overall calls if reset time has passed
        if current_time - self.last_reset > self.reset_time:
            self.calls = 0
            self.last_reset = current_time
        
        # Reset conversation calls if it's a new conversation
        if is_new_conversation:
            self.conversation_calls = 0

        # Check overall calls limit
        if self.calls >= self.max_calls:
            return False
        
        # Check conversation calls limit
        if self.conversation_calls >= self.max_conversation_calls:
            return False

        # Increment calls
        self.calls += 1
        self.conversation_calls += 1
        return True

class TimeoutException(Exception):
    """Exception raised when a function call times out."""
    pass

class Agent:
    def __init__(self, provider='openai'): 
        load_dotenv()
        self.logger = setup_logger()
        self.logger.info(f"🔧 Initializing Agent with provider: {provider}")
        
        self.used_tools = []
        self._load_tools()
        self.memory = Memory(max_messages=30)
        
        # Initialize API call tracker
        self.api_call_tracker = APICallTracker()

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
            # Remove any trailing quotes or extra characters
            clean_action_str = action_str.strip("'\"")
            
            # Directly call the function from self.TOOLS
            if clean_action_str in self.TOOLS:
                result = self.TOOLS[clean_action_str]()
            else:
                # If it's a function call with parameters
                match = re.match(r'(\w+)\((.*)\)', clean_action_str)
                if match:
                    func_name = match.group(1)
                    params_str = match.group(2)
                    
                    # Try to parse parameters
                    try:
                        # Special handling for get_product
                        if func_name == 'get_product':
                            # Remove quotes and strip
                            product_identifier = params_str.strip("'\"")
                            params = {'product_name': product_identifier}
                        
                        # Handle generate_order with list of dictionaries
                        elif func_name == 'generate_order':
                            # More robust parsing for generate_order
                            try:
                                # Try to parse as a list of dictionaries
                                params_list = eval(params_str)
                            except Exception:
                                # If parsing fails, try to parse as a single dictionary
                                params_list = [eval(f"dict({params_str})")]
                            
                            # Prepare to collect user details
                            customer_name = None
                            user_id = None
                            order_items = []

                            # Process each item in the list
                            for item in params_list:
                                # Convert product name to product ID
                                if 'product_name' in item:
                                    product = tools.product_repo.find_by_name(item['product_name'])
                                    if not product:
                                        raise ValueError(f"Produto '{item['product_name']}' não encontrado")
                                    
                                    order_items.append(
                                        tools.OrderItem(
                                            product_id=product.id,
                                            quantity=item.get('quantity', 1)
                                        )
                                    )
                                elif 'product_id' in item:
                                    order_items.append(
                                        tools.OrderItem(
                                            product_id=item['product_id'],
                                            quantity=item.get('quantity', 1)
                                        )
                                    )
                                
                                # Collect user details (prioritize later items)
                                if 'customer_name' in item:
                                    customer_name = item['customer_name']
                                if 'user_id' in item:
                                    user_id = item['user_id']

                            # Validate user details
                            if not customer_name or not user_id:
                                # If details are missing, try to extract from the first item
                                first_item = params_list[0]
                                customer_name = first_item.get('customer_name', customer_name)
                                user_id = first_item.get('user_id', user_id)

                            # Final validation of user details
                            if not customer_name or not user_id:
                                raise ValueError("Identificação do usuário é obrigatória. Por favor, forneça nome do cliente e ID do usuário.")

                            # Prepare parameters for order generation
                            params = {
                                'items': order_items,
                                'customer_name': customer_name,
                                'user_id': user_id
                            }
                        
                        # Default parsing for other tools
                        else:
                            # Try to parse as dictionary
                            params = eval(f"dict({params_str})")
                        
                        result = self.TOOLS[func_name](**params)
                    except Exception as parse_error:
                        raise ValueError(f"Error parsing parameters for {func_name}: {parse_error}")
                else:
                    raise ValueError(f"Invalid tool action format: {clean_action_str}")
            
            self.used_tools.append(clean_action_str)
            self.logger.info(f"Tool executed successfully: {clean_action_str}")
            return result
        except Exception as e:
            error_msg = f"Error running tool {action_str}: {e}"
            self.logger.error(error_msg)
            return error_msg

    def _send_to_model(self, messages, timeout=30):
        # Check if we can make an API call
        if not self.api_call_tracker.can_make_call():
            error_msg = "⚠️ Limite de chamadas de API excedido. Por favor, aguarde alguns minutos antes de tentar novamente."
            self.logger.warning(error_msg)
            raise TimeoutException(error_msg)

        # Truncate messages to avoid logging large system prompts
        truncated_messages = []
        for msg in messages:
            # Truncate system messages more aggressively
            if msg['role'] == 'system':
                truncated_msg = {**msg, 'content': 'System Prompt (Truncated)'}
            else:
                # For other messages, keep the first 100 characters
                truncated_msg = {**msg, 'content': msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']}
            truncated_messages.append(truncated_msg)

        self.logger.debug(f"Sending messages to model: {truncated_messages}")
        
        def _call_openai():
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            ).choices[0].message.content

        def _call_ollama():
            return self.client.chat(
                model='llama3.2:1b',
                messages=messages
            )['message']['content']

        def _call_gemini():
            combined = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
            return self.client.generate_content(combined).text

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                if self.provider == 'openai':
                    future = executor.submit(_call_openai)
                elif self.provider == 'ollama':
                    future = executor.submit(_call_ollama)
                elif self.provider == 'gemini':
                    future = executor.submit(_call_gemini)
                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")

                try:
                    content = future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    self.logger.warning(f"API call to {self.provider} timed out after {timeout} seconds")
                    raise TimeoutException(f"⚠️ Desculpe, a chamada para o modelo {self.provider.upper()} excedeu o tempo limite de {timeout} segundos. Por favor, tente novamente mais tarde.")

            # Truncate the response log to prevent overwhelming logs
            truncated_content = content[:200] + '...' if len(content) > 200 else content
            self.logger.debug(f"Model response: {truncated_content}")
            return content

        except TimeoutException as te:
            self.logger.error(f"Timeout error: {te}")
            return str(te)
        except Exception as e:
            self.logger.error(f"Error sending message to model: {e}")
            return f"⚠️ Erro ao processar sua solicitação: {str(e)}"

    @log_execution_time
    def call(self, user_question):
        self.logger.info(f"User asked: {user_question}")
        self.used_tools = []  # Reset used tools for each call
        self.memory.add_message("system", self._system_prompt())
        self.memory.add_message("user", user_question)

        max_iterations = 10  # Limit iterations to prevent infinite loops
        current_iteration = 0
        action_counts = {}  # Track action frequency
        last_product = None  # Track last successfully found product
        completed_actions = set()  # Track completed actions

        while current_iteration < max_iterations:
            messages = self.memory.get_context()
            response = self._send_to_model(messages)
            self.memory.add_message("assistant", response)

            action = self._extract_action(response)
            if action:
                # Increment action count and check for excessive repetition
                action_counts[action] = action_counts.get(action, 0) + 1
                if action_counts[action] > 2:
                    self.logger.warning(f"Action {action} repeated too many times. Breaking loop.")
                    break

                # Skip already completed actions
                if action in completed_actions:
                    continue

                try:
                    # Special handling for product retrieval
                    if 'get_product' in action:
                        try:
                            tool_result = self._run_tool(action)
                            last_product = tool_result
                            self.memory.add_message("function", str(tool_result), name=action)
                            completed_actions.add(action)
                        except Exception as e:
                            # If product not found, try to add it
                            if 'não encontrado' in str(e):
                                product_name = action.split('(')[1].strip("'\")")
                                add_product_action = f"add_product(product={{'name': '{product_name}', 'price': 50.00}})"
                                tool_result = self._run_tool(add_product_action)
                                self.memory.add_message("function", str(tool_result), name=add_product_action)
                                # Retry getting the product
                                tool_result = self._run_tool(action)
                                last_product = tool_result
                                completed_actions.add(action)
                            else:
                                raise

                    # For order generation, ensure product exists and has details
                    elif 'generate_order' in action:
                        # If no product found previously, extract from action
                        if not last_product:
                            match = re.search(r"'product_name':\s*'([^']+)'", action)
                            if match:
                                product_name = match.group(1)
                                get_product_action = f"get_product('{product_name}')"
                                last_product = self._run_tool(get_product_action)

                        # Ensure product exists and has inventory
                        if last_product and last_product.quantity > 0:
                            # Modify action to include user details
                            action = action.replace('generate_order', 
                                f"generate_order(items=[{{'product_name': '{last_product.name}', 'quantity': 1, 'customer_name': 'lucas', 'user_id': '11122233344'}}])")

                            tool_result = self._run_tool(action)
                            self.memory.add_message("function", str(tool_result), name=action)
                            completed_actions.add(action)
                            return tool_result
                        else:
                            # If no inventory, suggest adding inventory
                            update_inventory_action = f"update_inventory(product_name='{last_product.name}', quantity=10)"
                            tool_result = self._run_tool(update_inventory_action)
                            self.memory.add_message("function", str(tool_result), name=update_inventory_action)

                    else:
                        tool_result = self._run_tool(action)
                        self.memory.add_message("function", str(tool_result), name=action)
                        completed_actions.add(action)

                except Exception as e:
                    self.logger.error(f"Error executing action {action}: {e}")
                    # Break the loop if we can't resolve the issue
                    break

            current_iteration += 1

        # If we exit the loop without completing the task
        self.logger.warning("Could not complete the task after multiple attempts.")
        return "Não foi possível concluir a tarefa completamente."

    # Prepare system message
    def _system_prompt(self):
        return get_agent_prompt()
