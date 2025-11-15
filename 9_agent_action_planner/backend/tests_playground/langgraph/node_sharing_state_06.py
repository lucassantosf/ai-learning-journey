from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

# ------------------------------
# 1 - Definição do estado
# ------------------------------
class State(TypedDict, total=False):
    input: str
    mensagemA: str
    mensagemB: str


# ------------------------------
# 2 - Criar os nós
# ------------------------------

def node_a(state: State):
    print("Executando Node A")
    state["mensagemA"] = "Gerada pelo nó A"
    return state

def node_b(state: State):
    print("Executando Node B")
    msg_a = state.get("mensagemA")
    state["mensagemB"] = f"O nó B leu: '{msg_a}' e gerou sua própria mensagem"
    return state


# ------------------------------
# 3 - Criar o grafo
# ------------------------------

checkpointer = MemorySaver()
builder = StateGraph(State)

builder.add_node("A", node_a)
builder.add_node("B", node_b)

builder.set_entry_point("A")
builder.add_edge("A", "B")
builder.add_edge("B", END)

graph = builder.compile(checkpointer=checkpointer)


# ------------------------------
# 4 - Testar o fluxo
# ------------------------------

initial_input = {"input": "start"}

print("\n--- Rodando fluxo ---\n")
result = graph.invoke(
    initial_input,
    config={"configurable": {"thread_id": "teste-06"}}
)

print("\n--- Resultado Final ---")
print(result)