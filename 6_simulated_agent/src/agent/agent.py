import os
import httpx
from dotenv import load_dotenv
import ollama
import google.generativeai as genai
from openai import OpenAI
import concurrent.futures
import time
import json
import re 
import ast

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


    def _extract_action(self, response: str) -> tuple[str, dict] | None:
        """
        Extrai ACTIONs do texto, convertendo os argumentos para dicts.
        """
        action_pattern = r"ACTION:\s*(\w+)\((.*?)\)"
        match = re.search(action_pattern, response, re.DOTALL)
        if not match:
            return None

        action_name, args_text = match.groups()
        args_text = args_text.strip()

        # Handle different argument formats
        if not args_text:
            args_dict = {}
        else:
            try:
                # Try to parse as JSON first
                args_dict = json.loads(args_text)
            except json.JSONDecodeError:
                # Handle key-value pair format
                if '=' in args_text:
                    # Split key-value pairs
                    pairs = [p.strip() for p in args_text.split(',')]
                    args_dict = {}
                    for pair in pairs:
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            # Remove quotes and strip
                            key = key.strip().strip("'\"")
                            value = value.strip().strip("'\"")
                            args_dict[key] = value
                else:
                    # Fallback to simple string parsing
                    # Remove surrounding quotes if present
                    clean_text = args_text.strip("'\"")
                    
                    # Determine if it's a product name or ID
                    if clean_text.startswith('p'):
                        args_dict = {"product_id": clean_text}
                    else:
                        args_dict = {"product_name": clean_text}

        return (action_name, args_dict)

    def _run_tool(self, action_name: str, args: dict):
        """
        Executa a ferramenta correspondente ao nome da ação.
        """
        tool = self.TOOLS.get(action_name)
        if not tool:
            raise ValueError(f"Tool '{action_name}' not found")

        if args:
            return tool(**args)
        return tool()
    
    def _map_user_intent(self, user_question: str) -> str | None:
        q = user_question.lower()

        # mapeamento de palavras-chave para tool (pode evoluir para NLP simples se quiser)
        keyword_map = {
            "produto": "list_products",
            "produtos": "list_products",
            "listar produtos": "list_products",
            "todos produtos": "list_products",
            "estoque": "list_inventory",
            "inventário": "list_inventory",
            "meus pedidos": "list_orders",
            "histórico de pedidos": "list_orders",
            "adicionar": "add_product",
            "atualizar": "update_product",
            "deletar": "delete_product",
            "remover": "delete_product",
            "pedido": "generate_order",
            "fazer compra": "generate_order",
            "avaliar pedido": "rate_order",
        }

        for keyword, tool_name in keyword_map.items():
            if keyword in q and tool_name in self.TOOLS:
                return f"{tool_name}()"

        # fallback: se o usuário escrever exatamente o nome de uma tool
        for tool_name in self.TOOLS:
            if tool_name in q:
                return f"{tool_name}()"

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
        final_result = None  # Track the final result to return

        while current_iteration < max_iterations:
            messages = self.memory.get_context()
            response = self._send_to_model(messages)
            self.memory.add_message("assistant", response)

            # Extrai ação do modelo
            action_data = self._extract_action(response)
            if action_data:
                action_name, action_args = action_data
            else:
                action_name, action_args = self._map_user_intent(user_question), {}

            if not action_name:
                # Nenhuma ação detectada, retorna o último resultado ou resposta
                if final_result:
                    return final_result
                return response

            # Contabiliza repetição de ações
            action_counts[action_name] = action_counts.get(action_name, 0) + 1
            if action_counts[action_name] > 2:
                self.logger.warning(f"Ação '{action_name}' repetida muitas vezes. Encerrando loop.")
                break

            if action_name in completed_actions:
                current_iteration += 1
                continue

            try:
                tool_result = None
                if action_name in self.TOOLS or action_name in ["get_product", "generate_order", "list_products", "list_orders", "list_inventory"]:
                    tool_result = self._run_tool(action_name, args=action_args)
                    self.memory.add_message("function", str(tool_result), name=action_name)
                    completed_actions.add(action_name)
                    self.used_tools.append(action_name)

                    # Store list actions, but don't return immediately
                    if action_name in ["list_products", "list_orders", "list_inventory"]:
                        final_result = tool_result
                    
                    # If generate_order is successful, return the order
                    if action_name == "generate_order":
                        return tool_result

            except Exception as e:
                self.logger.error(f"Erro executando ação '{action_name}': {e}")
                break

            current_iteration += 1

        self.logger.warning("Não foi possível concluir a tarefa completamente.")
        return "Não foi possível concluir a tarefa completamente."
    
    def _system_prompt(self):
        return get_agent_prompt()
