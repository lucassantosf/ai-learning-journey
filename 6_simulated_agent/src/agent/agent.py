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
        Lida com JSON, literal Python e key=value.
        """
        action_pattern = r"ACTION:\s*(\w+)\((.*?)\)"
        match = re.search(action_pattern, response, re.DOTALL)
        if not match:
            return None

        action_name, args_text = match.groups()
        args_text = args_text.strip()

        if not args_text:
            return {}
        
        try:
            # tenta interpretar como literal Python
            args_dict = ast.literal_eval(f"dict({args_text})")
            if not isinstance(args_dict, dict):
                args_dict = {'items': args_dict}  # fallback para lista de items
        except Exception:
            try:
                # tenta como JSON
                args_dict = json.loads(args_text.replace("'", '"'))
            except Exception:
                # fallback key=value
                args_dict = {}
                pairs = [p.strip() for p in args_text.split(',')]
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")
                        args_dict[key] = value

        return action_name, args_dict
    
    def _run_tool(self, action_name: str, args):
        tool = self.TOOLS.get(action_name)
        if not tool:
            raise ValueError(f"Tool '{action_name}' not found")

        self.logger.debug(f"_run_tool chamado com action='{action_name}', args={args}")

        if args is None:
            return tool()

        if isinstance(args, dict):
            if action_name == "generate_order" and "items" in args and isinstance(args["items"], str):
                items_str = args["items"]
                # Tenta extrair o array completo do começo até o último ']'
                match = re.search(r"\[.*\]", items_str)
                if match:
                    items_str = match.group(0)
                try:
                    args["items"] = json.loads(items_str.replace("'", '"'))
                except Exception:
                    try:
                        args["items"] = ast.literal_eval(items_str)
                    except Exception:
                        self.logger.warning(f"Falha ao converter items string, fallback seguro: {items_str}")
                        args["items"] = [items_str]  # fallback seguro
            return tool(**args)

        if isinstance(args, list):
            return tool(items=args)

        if isinstance(args, str):
            for parser in (ast.literal_eval, lambda x: json.loads(x.replace("'", '"'))):
                try:
                    parsed = parser(args)
                    if isinstance(parsed, dict):
                        return tool(**parsed)
                    if isinstance(parsed, list):
                        return tool(items=parsed)
                    return tool(parsed)
                except Exception:
                    continue
            return tool(args)

        return tool(args)
        
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

    def normalize_items(self, items):
        """
        Converte items do modelo em lista de dicts válidos para generate_order.
        Remove campos extras e corrige strings aninhadas.
        """
        # Se já é lista de dicts, filtra campos
        if isinstance(items, list) and all(isinstance(i, dict) for i in items):
            return [{'product_name': i['product_name'], 'quantity': i['quantity']} for i in items if 'product_name' in i and 'quantity' in i]

        # Se for string, tenta parse
        if isinstance(items, str):
            try:
                import ast
                items_list = ast.literal_eval(items)
                if isinstance(items_list, list):
                    return [{'product_name': i['product_name'], 'quantity': i['quantity']} 
                            for i in items_list if isinstance(i, dict) and 'product_name' in i and 'quantity' in i]
            except Exception:
                pass

        # fallback seguro
        self.logger.warning(f"normalize_items fallback seguro: {items}")
        return []

    def _convert_item_str(self, s):
        # tenta JSON
        try:
            return json.loads(s.replace("'", '"'))
        except Exception:
            pass
        # tenta literal_eval
        try:
            return ast.literal_eval(s)
        except Exception:
            pass
        # fallback seguro: retorna dict mínimo
        self.logger.warning(f"Falha ao converter items string, fallback seguro: {s}")
        return {"product_name": str(s)}

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
        final_result = None

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
                return final_result if final_result else response

            # Contabiliza repetição de ações
            action_counts[action_name] = action_counts.get(action_name, 0) + 1
            if action_counts[action_name] > 2:
                self.logger.warning(f"Ação '{action_name}' repetida muitas vezes. Encerrando loop.")
                break

            if action_name in completed_actions:
                current_iteration += 1
                continue

            try:
                # Normaliza items do generate_order
                if action_name == "generate_order" and "items" in action_args:
                    action_args["items"] = self.normalize_items(action_args["items"])
                    # Garante que só passe 'items'
                    action_args = {"items": action_args["items"]}
                    
                    self.logger.debug(f"Items normalizados: {action_args['items']}")

                tool_result = None
                if action_name in self.TOOLS or action_name in ["get_product", "generate_order", "list_products", "list_orders", "list_inventory"]:
                    tool_result = self._run_tool(action_name, args=action_args)

                    # Serializa resultados complexos
                    serialized_result = tool_result
                    if action_name in ["list_orders", "list_products", "list_inventory"]:
                        if isinstance(tool_result, list):
                            serialized_result = []
                            for item in tool_result:
                                if hasattr(item, "__dict__"):
                                    serialized_result.append({k: v for k, v in vars(item).items()})
                                else:
                                    serialized_result.append(item)
                        else:
                            serialized_result = str(tool_result)

                    elif action_name == "generate_order":
                        if hasattr(tool_result, "__dict__"):
                            serialized_result = {k: v for k, v in vars(tool_result).items()}

                    self.memory.add_message("function", str(serialized_result), name=action_name)
                    completed_actions.add(action_name)
                    self.used_tools.append(action_name)

                    # Guarda resultados de listagens
                    if action_name in ["list_products", "list_orders", "list_inventory"]:
                        final_result = serialized_result

                    # Retorna imediatamente se order gerada com sucesso
                    if action_name == "generate_order":
                        return serialized_result

            except Exception as e:
                self.logger.error(f"Erro executando ação '{action_name}': {e}")
                completed_actions.add(action_name)  # evita repetir
                current_iteration += 1
                continue

            current_iteration += 1

        self.logger.warning("Não foi possível concluir a tarefa completamente.")
        return "Não foi possível concluir a tarefa completamente."


    def _system_prompt(self):
        return get_agent_prompt()
