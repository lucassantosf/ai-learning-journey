# backend/tests_playground/langgraph/agent_state_03.py

from dataclasses import dataclass, field
from typing import List, Any

from langgraph.graph import StateGraph, END

# Importando suas classes
from tests_playground.langgraph.memory_sqlite_01 import SQLiteMemory
from tests_playground.langgraph.planner_executor_basic_02 import SimplePlanner


# ============================================================
# 1. Agent State
# ============================================================

@dataclass
class AgentState:
    # Entrada original
    user_input: str = ""

    # Plano gerado pelo Planner
    plan: List[str] = field(default_factory=list)

    # Índice do passo atual
    current_step: int = 0

    # Histórico da execução
    history: List[str] = field(default_factory=list)

    # Resultados intermediários
    intermediate_results: List[Any] = field(default_factory=list)

    # Memória persistente (SQLite)
    memory: Any = None


# ============================================================
# 2. Funções dos nós do grafo
# ============================================================

def plan_step(state: AgentState):
    print("\n📌 [Planner] Gerando plano...")

    planner = SimplePlanner()
    plan = planner.plan(state.user_input)

    state.plan = plan
    state.current_step = 0

    print("📝 Plano gerado:")
    for i, p in enumerate(plan, start=1):
        print(f"  {i}. {p}")

    return state


def execute_step(state: AgentState):
    if state.current_step >= len(state.plan):
        print("\n✔️ Todos os passos foram executados.")
        return state

    step_text = state.plan[state.current_step]

    print(f"\n⚙️ [Executor] Executando passo {state.current_step + 1}: {step_text}")

    # Aqui está o seu "executor básico"
    result = f"Resultado do passo '{step_text}'"

    # Salva nos resultados intermediários
    state.intermediate_results.append(result)

    # Salva no histórico
    state.history.append(step_text)

    print(f"➡️ Resultado: {result}")

    return state


def save_step_to_memory(state: AgentState):
    print("💾 [Memória] Salvando passo no SQLite...")

    step_text = state.plan[state.current_step]

    state.memory.save_steps([step_text])

    print(f"   ✔️ Passo salvo: {step_text}")

    # Avança o ponteiro
    state.current_step += 1

    return state


# ============================================================
# 3. Criando o Grafo (StateGraph)
# ============================================================

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("planner", plan_step)
    workflow.add_node("executor", execute_step)
    workflow.add_node("save", save_step_to_memory)

    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "save")

    # Loop até todos os passos serem executados
    workflow.add_conditional_edges(
        "save",
        lambda state: "executor" if state.current_step < len(state.plan) else END
    )

    workflow.set_entry_point("planner")

    return workflow.compile()


# ============================================================
# 4. Execução local (python -m ...)
# ============================================================

if __name__ == "__main__":
    print("\n🚀 Inicializando agente...\n")

    agent = build_graph()

    initial_state = AgentState(
        user_input="Planejar uma mudança para um apartamento novo",
        memory=SQLiteMemory()
    )

    final_state = agent.invoke(initial_state)

    print("\n\n====== ESTADO FINAL ======")
    print("Plano:", final_state["plan"])
    print("Histórico:", final_state["history"])
    print("Resultados:", final_state["intermediate_results"])
    print("Passos executados:", final_state["current_step"])

    print("\n🎉 Execução completa!")