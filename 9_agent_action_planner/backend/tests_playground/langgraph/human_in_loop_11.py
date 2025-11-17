# tests_playground/langgraph/human_in_loop_11.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphInterrupt


# --------------------------------------------------------
# 1. Estado
# --------------------------------------------------------

class State(dict):
    user_input: str
    approval: str | None
    final_output: str | None


# --------------------------------------------------------
# 2. Nó que precisa de confirmação humana
# --------------------------------------------------------

def review_step(state: State):
    """
    Este nó pede intervenção humana antes de continuar.
    """

    # Se já chegou com aprovação, segue o fluxo
    if state.get("approval"):
        return {}

    # Caso contrário → interromper fluxo
    # IMPORTANTE: versão 1.0.3 permite APENAS 1 argumento (value)
    raise GraphInterrupt("REVIEW_REQUIRED")


# --------------------------------------------------------
# 3. Nó final
# --------------------------------------------------------

def finalize(state: State):
    if state.get("approval") == "approved":
        return {"final_output": "[LLM] Conteúdo aprovado e processado!"}

    if state.get("approval") == "rejected":
        return {"final_output": "[LLM] Conteúdo rejeitado pelo humano."}

    return {"final_output": "[LLM] Finalizado sem aprovação (?)"}


# --------------------------------------------------------
# 4. Construindo o Grafo
# --------------------------------------------------------

builder = StateGraph(State)

builder.add_node("review_step", review_step)
builder.add_node("finalize", finalize)

builder.set_entry_point("review_step")
builder.add_edge("review_step", "finalize")
builder.add_edge("finalize", END)

graph = builder.compile(checkpointer=MemorySaver())


# --------------------------------------------------------
# 5. Testes
# --------------------------------------------------------

def run_initial(message: str):
    """
    Primeira chamada → deve interromper.
    """
    try:
        graph.invoke(
            {"user_input": message},
            config={"configurable": {"thread_id": "ex11"}}
        )
    except GraphInterrupt as interrupt:
        print("\n📣 INTERRUPÇÃO DETECTADA!")
        print("Valor recebido:", interrupt.value)
        print("-" * 50)


def run_continue(approval: str):
    """
    Continuação após o humano aprovar/rejeitar.
    """
    result = graph.invoke(
        {"approval": approval},
        config={"configurable": {"thread_id": "ex11"}}
    )

    print("\n✅ Fluxo retomado!")
    print("Aprovação humana:", approval)
    print("Resultado final:", result["final_output"])
    print("-" * 50)


if __name__ == "__main__":
    print("\n--- TESTE EXERCÍCIO 11: HUMAN-IN-THE-LOOP ---\n")

    # Primeira execução → deve interromper
    run_initial("Avalie este conteúdo, por favor.")

    # O usuário humano agora decide e retoma
    run_continue("approved")
    run_continue("rejected")