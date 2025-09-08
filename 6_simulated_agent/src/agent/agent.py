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

from src.agent import tools
from src.agent.memory import Memory
from src.agent.prompt import get_agent_prompt
from src.utils.logger import setup_logger, log_execution_time
from src.agent.checkout_chain import CheckoutChain

class APICallTracker:
    def __init__(self, max_calls=50, reset_time=900, max_conversation_calls=10):
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
        self.memory = Memory(max_messages=10)
        self.api_call_tracker = APICallTracker()
        self.memory.add_message("system", self._system_prompt()) # Inicia com o prompt do sistema

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
            return action_name, {}

        args_dict = {}

        # Caso especial: items=[...]
        items_match = re.search(r"items\s*=\s*(\[.*\])", args_text, re.DOTALL)
        if items_match:
            items_str = items_match.group(1)
            try:
                items = ast.literal_eval(items_str)
            except Exception:
                try:
                    items = json.loads(items_str.replace("'", '"'))
                except Exception:
                    items = [items_str]  # fallback
            args_dict["items"] = items

            # Remove o trecho de items=... do args_text para não duplicar
            args_text = re.sub(r"items\s*=\s*\[.*\]", "", args_text, flags=re.DOTALL).strip(", ")

        # Agora processa os outros key=value
        if args_text:
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

        result = tool(**args) if args else tool()
        
        # Atualiza memória de estado para ações importantes
        if action_name == "get_product":
            self.memory.set_state("ultimo_produto_consultado", args.get("product_name"))
        elif action_name == "generate_order":
            self.memory.set_state("ultimo_pedido", result.get("order_id") if isinstance(result, dict) else str(result))
        elif action_name == "rate_order":
            self.memory.set_state("ultimo_pedido_avaliado", args.get("order_id"))
        elif action_name == "list_products":
            produtos_dict = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "average_rating": p.average_rating,
                    "image_url": p.image_url
                }
                for p in result
            ]
            self.memory.set_state("ultimos_produtos_listados", produtos_dict)
        elif action_name == "list_inventory":
            # Salva o resumo completo do inventário
            self.memory.set_state("estoque_resumo", result.get("formatted_summary"))

            # Salva totais numéricos para lógica de negócio
            self.memory.set_state("estoque_total_produtos", result.get("total_products"))
            self.memory.set_state("estoque_total_itens", result.get("total_items"))

            # Salva a lista detalhada (como strings já formatadas)
            self.memory.set_state("estoque_lista", result.get("inventory_list"))

            # 🔑 Fechar o ciclo: adiciona também a resposta como se fosse do assistente
            resumo = result.get("formatted_summary", "Estoque listado com sucesso.")
            self.memory.add_message("assistant", f"Aqui está o resumo do estoque atualizado:\n\n{resumo}")

        return result
        
    def _send_to_model(self, messages, timeout=30):

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
            self.logger.debug(f"Model response: {content[:400] + '...' if len(content) > 400 else content}")
            return content
        except concurrent.futures.TimeoutError:
            raise TimeoutException(f"⚠️ Chamada para {self.provider} excedeu o limite de {timeout}s.")
        except Exception as e:
            return f"⚠️ Erro ao processar sua solicitação: {e}"

    @log_execution_time
    def call(self, user_question):
        self.logger.info(f"User asked: {user_question}")
        self.used_tools = []
        self.memory.add_message("user", user_question)

        max_iterations = 15
        current_iteration = 0
        action_counts = {}
        final_result = None

        while current_iteration < max_iterations:
            # Antes de mandar pro modelo, já garante truncamento com resumo
            self.memory._truncate(
                summarize_fn=lambda text: self._summarize_with_model(text, self)
            )

            messages = self.memory.get_context()
            response = self._send_to_model(messages)
            self.memory.add_message("assistant", response)

            # Extrai ação do modelo
            action_data = self._extract_action(response)
            if action_data:
                action_name, action_args = action_data
            else:
                action_name, action_args = None, None

            if not action_name:
                return final_result if final_result else response

            # Contabiliza repetição de ações
            action_counts[action_name] = action_counts.get(action_name, 0) + 1
            if action_counts[action_name] > 20:
                self.logger.warning(f"Ação '{action_name}' repetida muitas vezes. Encerrando loop.")
                break

            try:
                
                # ---- Ação especial: CheckoutChain (encerramento determinístico do fluxo) ----
                if action_name == "checkout_chain":
                    self.logger.info("➡️ Executando CheckoutChain (explícito)...")
                    chain = CheckoutChain(self)

                    customer_name = action_args.get("customer_name") if action_args else None
                    customer_document = action_args.get("customer_document") if action_args else None
                    items = action_args.get("items") if action_args else None

                    chain_result = chain.run(
                        customer_name=customer_name,
                        customer_document=customer_document,
                        items=items
                    )
                    # registra o resultado como uma "function" no histórico
                    try:
                        self.memory.add_message("function", json.dumps(chain_result, ensure_ascii=False), name="checkout_chain")
                    except Exception:
                        self.memory.add_message("function", str(chain_result), name="checkout_chain")

                    # retorna direto (fluxo fechado e determinístico)
                    if isinstance(chain_result, dict) and chain_result.get("status") == "success":
                        return chain_result.get("message") or f"Pedido {chain_result.get('order_id')} criado com sucesso."
                    else:
                        return f"Não foi possível finalizar o pedido: {chain_result.get('reason', 'erro desconhecido')}. Detalhes: {chain_result.get('details', '')}"

                # ---- Ações normais ----
                tool_result = None
                if action_name in self.TOOLS:
                    tool_result = self._run_tool(action_name, args=action_args)

                    # Serializa resultados complexos
                    serialized_result = tool_result
                    if action_name in ["list_orders", "list_products", "list_inventory"]:
                        if isinstance(tool_result, list):
                            serialized_result = [
                                {k: v for k, v in vars(item).items()} if hasattr(item, "__dict__") else item
                                for item in tool_result
                            ]
                        else:
                            serialized_result = str(tool_result)

                        # Adiciona na memória, mas não retorna imediatamente
                        self.memory.add_message("function", str(serialized_result), name=action_name)
                        self.used_tools.append(action_name)
                        final_result = serialized_result
                        current_iteration += 1
                        continue

                    # Ações finais
                    if action_name == "generate_order":
                        return serialized_result

                    if action_name == "rate_order":
                        return f"Order successfully rated: Order ID={action_args.get('order_id')}, Rating={action_args.get('rating')}"

                    # Para outras ferramentas, adiciona na memória
                    self.memory.add_message("function", str(serialized_result), name=action_name)
                    self.used_tools.append(action_name)

            except Exception as e:
                self.logger.error(f"Erro executando ação '{action_name}': {e}")
                current_iteration += 1
                continue

            current_iteration += 1

        self.logger.warning("Não foi possível concluir a tarefa completamente.")
        return "Não foi possível concluir a tarefa completamente."
    
    def _system_prompt(self):
        return get_agent_prompt()