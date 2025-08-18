import os
import httpx
from dotenv import load_dotenv
import ollama
import google.generativeai as genai
from openai import OpenAI
import concurrent.futures
import time
import json

from src.utils.agent_prompt import get_agent_prompt
from src.agent import tools
from src.agent.memory import Memory
from src.utils.logger import setup_logger, log_execution_time

class APICallTracker:
    def __init__(self, max_calls=15, reset_time=900, max_conversation_calls=10):
        self.calls = 0
        self.last_reset = time.time()
        self.max_calls = max_calls
        self.reset_time = reset_time
        self.conversation_calls = 0
        self.max_conversation_calls = max_conversation_calls

    def can_make_call(self, is_new_conversation=False):
        current_time = time.time()
        if current_time - self.last_reset > self.reset_time:
            self.calls = 0
            self.last_reset = current_time
        if is_new_conversation:
            self.conversation_calls = 0
        if self.calls >= self.max_calls or self.conversation_calls >= self.max_conversation_calls:
            return False
        self.calls += 1
        self.conversation_calls += 1
        return True

class TimeoutException(Exception):
    pass

class Agent:
    def __init__(self, provider='openai'):
        load_dotenv()
        self.logger = setup_logger()
        self.logger.info(f"🔧 Initializing Agent with provider: {provider}")

        self.used_tools = []
        self._load_tools()
        self.memory = Memory(max_messages=30)
        self.api_call_tracker = APICallTracker()

        if provider == 'openai':
            self._setup_openai()
        elif provider == 'ollama':
            self._setup_ollama()
        elif provider == 'gemini':
            self._setup_gemini()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

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
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key not found.")
        self.client = OpenAI(api_key=key, http_client=httpx.Client(transport=httpx.HTTPTransport(retries=3)))
        self.provider = 'openai'
        self.logger.info("OpenAI client initialized")

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
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("Gemini API key not found.")
        genai.configure(api_key=key)
        self.client = genai.GenerativeModel('gemini-2.0-flash')
        self.provider = 'gemini'
        self.logger.info("Gemini client initialized")

    def _extract_action(self, response: str) -> str | None:
        prefix = "ACTION:"
        idx = response.find(prefix)
        if idx != -1:
            idx += len(prefix)
            end = response.find('\n', idx)
            if end == -1:
                end = len(response)
            action = response[idx:end].strip()
            self.logger.info(f"Action detected: {action}")
            return action
        self.logger.debug("No action detected")
        return None

    def _run_tool(self, action_str: str):
        self.logger.info(f"⚙️ Executing tool: {action_str}")
        try:
            clean_action = action_str.strip("'\"")
            if clean_action in self.TOOLS:
                result = self.TOOLS[clean_action]()
            else:
                # Parse function calls with parameters
                func_name, params_str = clean_action.split('(', 1)
                params_str = params_str.rstrip(')').strip()
                if func_name == 'get_product':
                    product_name = params_str.strip("'\"")
                    result = self.TOOLS[func_name](product_name=product_name)
                elif func_name == 'generate_order':
                    items_str = params_str[6:].strip() if params_str.startswith('items=') else params_str
                    items_list = json.loads(items_str.replace("'", '"'))
                    if not isinstance(items_list, list):
                        items_list = [items_list]
                    order_items = []
                    customer_name = None
                    user_id = None
                    for item in items_list:
                        if 'customer_name' in item and not customer_name:
                            customer_name = item.pop('customer_name')
                        if 'user_id' in item and not user_id:
                            user_id = item.pop('user_id')
                        if 'product_name' in item:
                            product = tools.get_product(product_name=item['product_name'])
                            order_items.append(tools.OrderItem(product_id=product.id, quantity=item.get('quantity', 1)))
                        elif 'product_id' in item:
                            order_items.append(tools.OrderItem(product_id=item['product_id'], quantity=item.get('quantity', 1)))
                        else:
                            raise ValueError("Each item must have 'product_name' or 'product_id'")
                    params = {'items': order_items, 'customer_name': customer_name or 'lucas', 'user_id': user_id or '11122233344'}
                    result = self.TOOLS[func_name](**params)
                else:
                    params = json.loads(f"{{{params_str}}}")
                    result = self.TOOLS[func_name](**params)
            self.used_tools.append(clean_action)
            self.logger.info(f"Tool executed successfully: {clean_action}")
            return result
        except Exception as e:
            self.logger.error(f"Error running tool {action_str}: {e}")
            return str(e)

    def _map_user_intent(self, user_question: str) -> str | None:
        q = user_question.lower()
        if "histórico de pedidos" in q or "meus pedidos" in q:
            return "list_orders()"
        if "estoque" in q or "produtos disponíveis" in q:
            return "list_inventory()"
        if "adicionar produto" in q:
            return "add_product()"
        return None

    def _send_to_model(self, messages, timeout=30):
        if not self.api_call_tracker.can_make_call():
            raise TimeoutException("⚠️ Limite de chamadas de API excedido.")
        truncated_messages = []
        for msg in messages:
            content = msg['content']
            if msg['role'] == 'system':
                content = 'System Prompt (Truncated)'
            elif len(content) > 100:
                content = content[:100] + '...'
            truncated_messages.append({**msg, 'content': content})
        self.logger.debug(f"Sending messages to model: {truncated_messages}")

        def _call_openai():
            return self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages).choices[0].message.content
        def _call_ollama():
            return self.client.chat(model='llama3.2:1b', messages=messages)['message']['content']
        def _call_gemini():
            combined = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
            return self.client.generate_content(combined).text

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                if self.provider == 'openai':
                    future = executor.submit(_call_openai)
                elif self.provider == 'ollama':
                    future = executor.submit(_call_ollama)
                else:
                    future = executor.submit(_call_gemini)
                content = future.result(timeout=timeout)
            self.logger.debug(f"Model response: {content[:200] + '...' if len(content) > 200 else content}")
            return content
        except concurrent.futures.TimeoutError:
            raise TimeoutException(f"⚠️ Chamada para {self.provider} excedeu o limite de {timeout}s.")
        except Exception as e:
            return f"⚠️ Erro ao processar sua solicitação: {e}"

    @log_execution_time
    def call(self, user_question):
        self.logger.info(f"User asked: {user_question}")
        self.used_tools = []
        self.memory.add_message("system", self._system_prompt())
        self.memory.add_message("user", user_question)

        max_iterations = 15
        current_iteration = 0
        completed_actions = set()
        action_counts = {}
        last_product = None

        while current_iteration < max_iterations:
            messages = self.memory.get_context()
            response = self._send_to_model(messages)
            self.memory.add_message("assistant", response)

            action = self._extract_action(response) or self._map_user_intent(user_question)

            if not action:
                self.logger.info("Nenhuma ação detectada. Encerrando loop.")
                return response

            action_counts[action] = action_counts.get(action, 0) + 1
            if action_counts[action] > 2:
                self.logger.warning(f"Ação '{action}' repetida muitas vezes. Encerrando loop.")
                break
            if action in completed_actions:
                current_iteration += 1
                continue

            try:
                if 'get_product' in action:
                    tool_result = self._run_tool(action)
                    last_product = tool_result
                elif 'generate_order' in action:
                    if not last_product:
                        product_name_start = action.find("'product_name': '")
                        if product_name_start != -1:
                            product_name_start += len("'product_name': '")
                            product_name_end = action.find("'", product_name_start)
                            product_name = action[product_name_start:product_name_end]
                            last_product = self._run_tool(f"get_product('{product_name}')")
                    tool_result = self._run_tool(action)
                    return tool_result
                else:
                    tool_result = self._run_tool(action)
                self.memory.add_message("function", str(tool_result), name=action)
                completed_actions.add(action)
            except Exception as e:
                self.logger.error(f"Erro executando ação '{action}': {e}")
                break
            current_iteration += 1

        self.logger.warning("Não foi possível concluir a tarefa completamente.")
        return "Não foi possível concluir a tarefa completamente."

    def _system_prompt(self):
        return get_agent_prompt()
