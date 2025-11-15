from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from tests_playground.langgraph.memory_sqlite_01 import SQLiteMemory


# ============================================
# 1. Fake LLM (Mock)
# ============================================

class FakeLLM:
    """Simula uma resposta de LLM sem usar OpenAI."""
    def invoke(self, prompt: str) -> Dict[str, Any]:
        print("\n🤖 [FakeLLM] Gerando resposta...")
        return {
            "content": f"[FAKE-LLM] Resposta automática para: {prompt}"
        }


llm = FakeLLM()


# ============================================
# 2. Estado do agente (DICT)
# ============================================

def initial_state(user_input: str) -> Dict[str, Any]:
    return {
        "user_input": user_input,
        "plan": [],
        "current_step": 0,
        "history": [],
        "memory": SQLiteMemory(),
        "intermediate_results": [],
        "summary": "",
    }


# ============================================
# 3. Planner
# ============================================

def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n🧠 [Planner] Criando plano...")

    query = state["user_input"]

    response = llm.invoke(f"Gere um plano para: {query}")
    plan_text = response["content"]

    # Transformamos o texto em uma lista artificial de passos
    state["plan"] = [
        "Interpretar pedido",
        "Consultar LLM para detalhes",
        "Gerar resumo final"
    ]

    state["history"].append("Plano criado.")
    return state


# ============================================
# 4. Executor
# ============================================

def executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    plan = state["plan"]
    idx = state["current_step"]

    if idx >= len(plan):
        return state

    step = plan[idx]
    print(f"\n⚙️ [Executor] Executando passo: {step}")

    result = llm.invoke(f"Execute o passo: {step}")["content"]

    state["intermediate_results"].append(result)
    state["history"].append(f"Passo {idx+1} executado.")

    return state


# ============================================
# 5. Salvar na memória
# ============================================

def memory_node(state: Dict[str, Any]) -> Dict[str, Any]:
    idx = state["current_step"]
    step = state["plan"][idx]
    result = state["intermediate_results"][-1]

    print("💾 [Memória] Salvando no SQLite...")
    state["memory"].add(f"{step} => {result}")

    state["current_step"] += 1
    return state


# ============================================
# 6. Resumo final
# ============================================

def summarize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n🧹 [Summarizer] Criando resumo final...")

    res = "\n".join(state["intermediate_results"])
    state["summary"] = f"Resumo das execuções:\n{res}"
    state["history"].append("Resumo criado.")

    return state


# ============================================
# 7. Construção do grafo
# ============================================

workflow = StateGraph(dict)

workflow.add_node("plan", planner_node)
workflow.add_node("execute", executor_node)
workflow.add_node("memory", memory_node)
workflow.add_node("summarize", summarize_node)

workflow.set_entry_point("plan")

workflow.add_edge("plan", "execute")
workflow.add_edge("execute", "memory")

workflow.add_conditional_edges(
    "memory",
    lambda s: "execute" if s["current_step"] < len(s["plan"]) else "summarize"
)

workflow.add_edge("summarize", END)

graph = workflow.compile()


# ============================================
# 8. Execução manual
# ============================================

if __name__ == "__main__":
    state = initial_state("Quero criar um agente que gera planos")

    result = graph.invoke(state)

    print("\n========== RESULTADO FINAL ==========")
    print("Plano:", result["plan"])
    print("Histórico:", result["history"])
    print("Resultados intermediários:", result["intermediate_results"])
    print("Resumo:", result["summary"])
    print("Passos executados:", result["current_step"])