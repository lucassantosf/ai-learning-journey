# src/agents/agent_manager.py

from typing import Dict, Any
from openai import OpenAI
from rich.console import Console
from src.retrieval.retriever import Retriever
from src.agents.tools import build_tools
from src.agents.prompts.classify_prompt import build_classify_prompt
from src.agents.prompts.final_prompt import build_final_prompt
from src.agents.prompts.tool_execution_prompt import build_tool_execution_prompt
import json

console = Console()


class AgentManager:
    """
    Gerencia o agente e suas ferramentas.
    Suporta raciocínio multi-hop (várias etapas):
    1️⃣ Classificação da pergunta
    2️⃣ Planejamento e execução de ferramentas
    3️⃣ Geração de resposta final com justificativas e citações
    """

    def __init__(self, retriever: Retriever, model_name: str = "gpt-4o-mini", client: OpenAI = None):
        self.retriever = retriever
        self.model_name = model_name
        self.client = client or OpenAI()
        self.tools = build_tools(self.retriever, shared_client=self.client)

    def _llm(self, prompt: str) -> str:
        """Função utilitária para gerar texto com o modelo LLM."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Executa o raciocínio multi-hop completo.
        """
        reasoning_steps = []
        tools_used = []

        console.rule("[bold green]🧠 Iniciando raciocínio multi-hop")
        console.print(f"[cyan]Pergunta:[/cyan] {question}")

        # 1️⃣ CLASSIFICAÇÃO
        reasoning_steps.append("🔍 Analisando o tipo de pergunta...")
        console.print("[blue]🔹 Etapa 1:[/blue] Classificando tipo da pergunta...")

        classify_prompt = build_classify_prompt(question)
        analysis = self._llm(classify_prompt)
        reasoning_steps.append(f"📘 Classificação do LLM:\n{analysis}")

        try:
            parsed = json.loads(analysis)
            selected_tools = parsed.get("tools", [])
            reasoning_steps.append(f"🧰 Ferramentas sugeridas: {', '.join(selected_tools)}")
        except Exception as e:
            console.print(f"[yellow]⚠️ Falha ao interpretar análise ({e}), usando modo básico (RAG).[/yellow]")
            selected_tools = ["basic_rag"]

        # 2️⃣ EXECUÇÃO DAS FERRAMENTAS
        console.print("[blue]🔹 Etapa 2:[/blue] Planejando e executando ferramentas...")
        reasoning_steps.append("⚙️ Planejando execução das ferramentas...")

        final_context = ""

        if not selected_tools:
            reasoning_steps.append("⚠️ Nenhuma ferramenta sugerida — executando basic_rag por padrão.")
            selected_tools = ["basic_rag"]

        # 🧠 Geração de plano de execução via LLM
        try:
            exec_prompt = build_tool_execution_prompt(question, selected_tools)
            exec_plan_raw = self._llm(exec_prompt)
            reasoning_steps.append(f"🗂️ Plano de execução sugerido:\n{exec_plan_raw}")

            try:
                exec_plan = json.loads(exec_plan_raw)
            except Exception:
                exec_plan = [{"tool": t, "arguments": {"content": question}} for t in selected_tools]
                reasoning_steps.append("⚠️ Falha ao parsear plano, executando fallback simples.")
        except Exception as e:
            reasoning_steps.append(f"❌ Erro ao gerar plano de execução: {e}")
            exec_plan = [{"tool": t, "arguments": {"content": question}} for t in selected_tools]

        # 🧩 Executa cada ferramenta do plano
        for call in exec_plan:
            tool_name = call.get("tool")
            args = call.get("arguments", {})

            # Caso especial: basic_rag
            if tool_name == "basic_rag":
                reasoning_steps.append("📖 Usando FAISS retriever para buscar contexto relevante...")
                console.print("[magenta]🔹 Ferramenta:[/magenta] basic_rag (FAISS retriever)")
                tools_used.append("faiss_retriever")

                results = self.retriever.search(question, top_k=3)
                contexts = [r["text"] for r in results]
                final_context += "\n\n".join(contexts)
                reasoning_steps.append(f"🔎 {len(contexts)} contextos encontrados.")
                continue

            # Execução de ferramenta registrada
            if tool_name in self.tools:
                console.print(f"[magenta]🔹 Executando ferramenta:[/magenta] {tool_name}")
                tools_used.append(tool_name)

                try:
                    tool_func = self.tools[tool_name]
                    # LlamaIndex FunctionTool usa .fn para acessar a função real
                    if hasattr(tool_func, "fn"):
                        func = tool_func.fn
                    else:
                        func = tool_func

                    # Passa o argumento principal (content ou question)
                    arg_value = args.get("content", question)
                    tool_result = func(arg_value)
                    final_context += f"\n\n[Trecho {tool_name}]\n{tool_result}"
                    reasoning_steps.append(f"✅ {tool_name} executada com sucesso.")
                except Exception as e:
                    reasoning_steps.append(f"❌ Erro ao executar {tool_name}: {e}")
                    console.print(f"[red]Erro ao executar {tool_name}: {e}[/red]")
            else:
                reasoning_steps.append(f"⚠️ Ferramenta desconhecida: {tool_name}")
                tools_used.append(f"{tool_name} (não encontrada)")
                console.print(f"[yellow]⚠️ Ferramenta desconhecida: {tool_name}[/yellow]")

        # 3️⃣ RESPOSTA FINAL
        reasoning_steps.append("🧠 Gerando resposta final com base nas ferramentas executadas...")
        console.print("[blue]🔹 Etapa 3:[/blue] Gerando resposta final...")

        final_prompt = build_final_prompt(question, final_context)
        final_answer = self._llm(final_prompt)

        reasoning_steps.append("✅ Resposta final gerada com sucesso.")
        console.rule("[bold green]🏁 Raciocínio concluído")

        return {
            "reasoning": "\n".join(reasoning_steps),
            "tools_used": tools_used,
            "final_answer": final_answer,
        }
