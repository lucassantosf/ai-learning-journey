# tests_playground/langgraph/router_07.py

from typing import Any
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver


# -----------------------------
# 1. Definir o estado
# -----------------------------

class State(MessagesState):
    input: Any
    result: Any = None


# -----------------------------
# 2. Definir os nós do grafo
# -----------------------------

def router_node(state: State):
    """Decide qual nó irá rodar baseado no tipo do input."""
    value = state["input"]

    if isinstance(value, str):
        return {"next": "processar_texto"}

    if isinstance(value, (int, float)):
        return {"next": "processar_numero"}

    return {"next": END}


def processar_texto(state: State):
    texto = state["input"]
    return {"result": f"Texto processado: '{texto.upper()}'"}


def processar_numero(state: State):
    numero = state["input"]
    return {"result": numero * 10}


# -----------------------------
# 3. Construir grafo
# -----------------------------

builder = StateGraph(State)

builder.add_node("router", router_node)
builder.add_node("processar_texto", processar_texto)
builder.add_node("processar_numero", processar_numero)

builder.set_entry_point("router")

# ⚠️ IMPORTANTE — versão 1.0.3 usa a função direto (sem "cond=")
builder.add_conditional_edges(
    "router",
    lambda out: out["next"],
    {
        "processar_texto": "processar_texto",
        "processar_numero": "processar_numero",
        END: END,
    },
)

builder.add_edge("processar_texto", END)
builder.add_edge("processar_numero", END)

graph = builder.compile(checkpointer=MemorySaver())


# -----------------------------
# 4. Executar testes
# -----------------------------

def run(value, thread="router-test"):
    result = graph.invoke(
        {"input": value},
        config={"configurable": {"thread_id": thread}}
    )
    print("\nInput:", value)
    print("Resultado:", result["result"])
    print("-" * 50)


if __name__ == "__main__":
    print("\n--- Testando roteamento ---")
    run("olá mundo")
    run(7)
    run(3.14)