# tests_playground/langgraph/agent_tools_router_09.py

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# --------------------------------------------------
# 1. Estado do Agente
# --------------------------------------------------

class State(dict):
    user_input: str
    tool_result: str | None
    final_output: str | None
    selected_action: str | None


# --------------------------------------------------
# 2. Ferramentas fake
# --------------------------------------------------

def tool_calculate(x: int, y: int) -> str:
    return f"[TOOL_CALCULATE] Resultado: {x + y}"


def tool_weather(city: str) -> str:
    return f"[TOOL_WEATHER] Clima em {city}: ensolarado"


TOOLS = {
    "calculate": tool_calculate,
    "weather": tool_weather,
}


# --------------------------------------------------
# 3. Router decide a ação
# --------------------------------------------------

def router(state: State):
    text = state["user_input"].lower()

    if "somar" in text:
        return {"next": "tool_executor", "selected_action": "calculate"}

    if "clima" in text:
        return {"next": "tool_executor", "selected_action": "weather"}

    return {"next": "llm"}


# --------------------------------------------------
# 4. Executor de ferramentas
# --------------------------------------------------

def tool_executor(state: State):
    action = state["selected_action"]
    text = state["user_input"]

    if action == "calculate":
        return {
            "tool_result": tool_calculate(2, 3)
        }

    if action == "weather":
        return {
            "tool_result": tool_weather("Salvador")
        }

    return {"tool_result": "Erro: ferramenta desconhecida"}


# --------------------------------------------------
# 5. LLM fake final
# --------------------------------------------------

def llm_fake(state: State):
    user_text = state["user_input"]

    if state.get("tool_result"):
        return {
            "final_output": f"[LLM] Aqui está o resultado que encontrei: {state['tool_result']}"
        }

    return {
        "final_output": f"[LLM] Entendi sua mensagem: '{user_text}'"
    }


# --------------------------------------------------
# 6. Construção do Grafo
# --------------------------------------------------

builder = StateGraph(State)

builder.add_node("router", router)
builder.add_node("tool_executor", tool_executor)
builder.add_node("llm", llm_fake)

builder.set_entry_point("router")

# Rotas condicionais
builder.add_conditional_edges(
    "router",
    lambda o: o["next"],
    {
        "tool_executor": "tool_executor",
        "llm": "llm",
    }
)

# Fim do fluxo
builder.add_edge("tool_executor", "llm")
builder.add_edge("llm", END)

graph = builder.compile(checkpointer=MemorySaver())


# --------------------------------------------------
# 7. Testes
# --------------------------------------------------

def run(message: str):
    result = graph.invoke(
        {"user_input": message},
        config={"configurable": {"thread_id": "agent-09"}}
    )

    print("\n📥 Input:", message)
    print("🛠️ Ação:", result.get("selected_action"))
    print("🔧 Tool result:", result.get("tool_result"))
    print("🤖 Output final:", result.get("final_output"))
    print("-" * 50)


if __name__ == "__main__":
    print("\n--- TESTANDO AGENTE COM TOOLS E ROUTER ---\n")

    run("Por favor, somar 2 e 3.")
    run("Qual é o clima hoje?")
    run("Me explique o que é LangGraph.")