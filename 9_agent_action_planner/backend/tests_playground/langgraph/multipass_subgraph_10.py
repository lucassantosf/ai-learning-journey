# tests_playground/langgraph/multipass_subgraph_10.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# --------------------------------------------------------
# 1. Estado
# --------------------------------------------------------

class State(dict):
    user_input: str
    plan: str | None
    sub_result: str | None
    final_output: str | None


# --------------------------------------------------------
# 2. Criando um SUBGRAFO (pipeline interno)
# --------------------------------------------------------

def sub_step_1(state: State):
    return {"sub_result": f"[SUB1] Processando: {state['user_input']}"}

def sub_step_2(state: State):
    return {"sub_result": f"[SUB2] Refinado: {state['sub_result']}"}


sub_builder = StateGraph(State)

sub_builder.add_node("sub_step_1", sub_step_1)
sub_builder.add_node("sub_step_2", sub_step_2)

sub_builder.set_entry_point("sub_step_1")
sub_builder.add_edge("sub_step_1", "sub_step_2")
sub_builder.add_edge("sub_step_2", END)

subgraph = sub_builder.compile()


# --------------------------------------------------------
# 3. Nó principal: Planner
# --------------------------------------------------------

def planner(state: State):
    text = state["user_input"].lower()

    if "analisar" in text:
        return {"plan": "use_subgraph"}

    return {"plan": "direct"}


# --------------------------------------------------------
# 4. Executor do subgrafo
# --------------------------------------------------------

def run_subgraph(state: State):
    result = subgraph.invoke({"user_input": state["user_input"]})
    return {"sub_result": result["sub_result"]}


# --------------------------------------------------------
# 5. LLM Fake final
# --------------------------------------------------------

def llm_final(state: State):
    if state.get("sub_result"):
        return {
            "final_output": f"[LLM] Resultado do sub-processo: {state['sub_result']}"
        }

    return {
        "final_output": f"[LLM] Mensagem processada diretamente: {state['user_input']}"
    }


# --------------------------------------------------------
# 6. Construção do GRAFO PRINCIPAL
# --------------------------------------------------------

builder = StateGraph(State)

builder.add_node("planner", planner)
builder.add_node("run_subgraph", run_subgraph)
builder.add_node("llm_final", llm_final)

builder.set_entry_point("planner")

builder.add_conditional_edges(
    "planner",
    lambda o: o["plan"],
    {
        "use_subgraph": "run_subgraph",
        "direct": "llm_final",
    }
)

builder.add_edge("run_subgraph", "llm_final")
builder.add_edge("llm_final", END)

graph = builder.compile(checkpointer=MemorySaver())


# --------------------------------------------------------
# 7. Testes
# --------------------------------------------------------

def run(message: str):
    result = graph.invoke(
        {"user_input": message},
        config={"configurable": {"thread_id": "ex10"}}
    )

    print("\n📥 Input:", message)
    print("🧭 Plano:", result.get("plan"))
    print("🔧 SubResult:", result.get("sub_result"))
    print("🤖 Output final:", result.get("final_output"))
    print("-" * 50)


if __name__ == "__main__":
    print("\n--- TESTE EXERCÍCIO 10: MULTIPASSO COM SUBGRAFO ---\n")

    run("Preciso analisar profundamente este texto")
    run("Apenas processe isto diretamente")