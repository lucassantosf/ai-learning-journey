# tests_playground/langgraph/model_router_08.py

from typing import Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# -----------------------------
# 1. Estado
# -----------------------------

class State(dict):
    input: str
    model_used: str | None
    output: str | None


# -----------------------------
# 2. LLMs Fake
# -----------------------------

def llm_fast(prompt: str) -> str:
    return f"[FAST_MODEL] resposta rápida para: {prompt}"


def llm_slow(prompt: str) -> str:
    return f"[SLOW_MODEL] resposta detalhada para: {prompt}"


# -----------------------------
# 3. Router
# -----------------------------

def choose_model(state: State):
    text = state["input"]

    if len(text) < 40:
        return {"next": "fast_model"}

    return {"next": "slow_model"}


# -----------------------------
# 4. Nós dos modelos
# -----------------------------

def fast_model_node(state: State):
    prompt = state["input"]
    return {
        "model_used": "fast",
        "output": llm_fast(prompt),
    }


def slow_model_node(state: State):
    prompt = state["input"]
    return {
        "model_used": "slow",
        "output": llm_slow(prompt),
    }


# -----------------------------
# 5. Construção do grafo
# -----------------------------

builder = StateGraph(State)

builder.add_node("router", choose_model)
builder.add_node("fast_model", fast_model_node)
builder.add_node("slow_model", slow_model_node)

builder.set_entry_point("router")

builder.add_conditional_edges(
    "router",
    lambda out: out["next"],
    {
        "fast_model": "fast_model",
        "slow_model": "slow_model",
    },
)

builder.add_edge("fast_model", END)
builder.add_edge("slow_model", END)

graph = builder.compile(checkpointer=MemorySaver())


# -----------------------------
# 6. Testes
# -----------------------------

def run(text):
    result = graph.invoke(
        {"input": text},
        config={"configurable": {"thread_id": "router-08"}}
    )

    print("\n📥 Input:", text)
    print("⚙️ Modelo escolhido:", result["model_used"])
    print("📤 Output:", result["output"])
    print("-" * 50)


if __name__ == "__main__":
    print("\n--- Roteamento de modelos ---")

    run("Olá!")
    run("Preciso de uma explicação extremamente detalhada sobre LangGraph...")