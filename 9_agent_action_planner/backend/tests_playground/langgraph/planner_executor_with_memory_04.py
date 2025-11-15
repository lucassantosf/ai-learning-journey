from typing import List, Any
from dataclasses import dataclass, field
from langgraph.graph import StateGraph, END
from tests_playground.langgraph.memory_sqlite_01 import SQLiteMemory

# ===============================
# Agent State
# ===============================

@dataclass
class AgentState:
    user_input: str = ""
    plan: List[str] = field(default_factory=list)
    current_step: int = 0
    history: List[str] = field(default_factory=list)
    intermediate_results: List[Any] = field(default_factory=list)
    memory: Any = None

# ===============================
# Tools
# ===============================

def get_current_weather(location: str) -> str:
    return f"Clima atual em {location}: ensolarado e 28ºC"

def search_flights(origin: str, destination: str) -> str:
    return f"Voo fictício encontrado: {origin} → {destination} por R$ 799"

TOOLS = {
    "get_current_weather": get_current_weather,
    "search_flights": search_flights,
}

# ===============================
# Planner
# ===============================

class ToolPlanner:
    def plan(self, user_input: str) -> List[str]:
        print("\n🧠 [Planner] Gerando plano...")

        return [
            f"Entender origem e destino da viagem: {user_input}",
            "TOOL:search_flights São Paulo Salvador",
            "TOOL:get_current_weather Salvador",
            "Criar um resumo final combinando voo e clima"
        ]

# ===============================
# Executor
# ===============================

class ToolExecutor:
    def execute(self, step: str) -> str:
        print(f"\n⚙️ [Executor] Executando passo: {step}")

        if step.startswith("TOOL:"):
            _, raw = step.split(":", 1)
            parts = raw.split()

            tool_name = parts[0]
            args = parts[1:]

            if tool_name not in TOOLS:
                return f"Erro: ferramenta '{tool_name}' não encontrada"

            print(f"🔧 Detectado Tool Call → {tool_name}({args})")

            # ---- NOVO: tratamento de argumentos compostos ----
            if tool_name == "search_flights":
                # origem = primeira palavra
                # destino = resto (pode ter espaço)
                origin = args[0]
                destination = " ".join(args[1:])
                result = TOOLS[tool_name](origin, destination)

            elif tool_name == "get_current_weather":
                # clima sempre recebe 1 argumento (pode ter mais de uma palavra)
                location = " ".join(args)
                result = TOOLS[tool_name](location)

            else:
                result = TOOLS[tool_name](*args)
            # ----------------------------------------------------

            print(f"🔍 Resultado da Tool: {result}")
            return result

        return f"Resultado do passo '{step}'"

# ===============================
# Nós do Grafo
# ===============================

planner = ToolPlanner()
executor = ToolExecutor()

def plan_step(state: AgentState) -> AgentState:
    state.plan = planner.plan(state.user_input)
    state.history.append("Plano criado.")
    return state

def execute_step(state: AgentState) -> AgentState:
    if state.current_step >= len(state.plan):
        return state

    step = state.plan[state.current_step]
    result = executor.execute(step)

    state.intermediate_results.append(result)
    state.history.append(f"Step {state.current_step+1} executado.")

    return state

def save_step_to_memory(state: AgentState) -> AgentState:
    step = state.plan[state.current_step]
    result = state.intermediate_results[-1]

    print("💾 [Memória] Salvando no SQLite...")
    state.memory.add(f"STEP: {step} | RESULT: {result}")

    state.current_step += 1
    return state

# ===============================
# Definição do Grafo
# ===============================

workflow = StateGraph(AgentState)

workflow.add_node("plan", plan_step)
workflow.add_node("execute", execute_step)
workflow.add_node("save", save_step_to_memory)

workflow.set_entry_point("plan")

workflow.add_edge("plan", "execute")
workflow.add_edge("execute", "save")

workflow.add_conditional_edges(
    "save",
    lambda s: "execute" if s.current_step < len(s.plan) else END
)

graph = workflow.compile()

# ===============================
# Execução manual
# ===============================

if __name__ == "__main__":
    initial_state = AgentState(
        user_input="Quero viajar de São Paulo para Salvador",
        memory=SQLiteMemory()
    )

    final_state = graph.invoke(initial_state)

    print("\n======= RESULTADO FINAL =======")
    print("Plano:", final_state["plan"])
    print("Histórico:", final_state["history"])
    print("Resultados:", final_state["intermediate_results"])
    print("Passos executados:", final_state["current_step"])