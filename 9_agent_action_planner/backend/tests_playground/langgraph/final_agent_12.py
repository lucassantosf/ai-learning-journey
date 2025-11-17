# backend/tests_playground/langgraph/final_agent_12.py
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphInterrupt

from tests_playground.langgraph.memory_sqlite_01 import SQLiteMemory

# -----------------------
# Fake LLM + Tools
# -----------------------
class FakeLLM:
    def respond(self, prompt: str) -> str:
        return f"[FAKE-LLM] {prompt[:120]}"

llm = FakeLLM()

def tool_search_flights(origin: str, destination: str) -> str:
    return f"[TOOL] Voo simulado: {origin} -> {destination} por R$799"

def tool_get_weather(city: str) -> str:
    return f"[TOOL] Clima em {city}: ensolarado, 28ºC"

def tool_calculate(a: int, b: int) -> str:
    return f"[TOOL] Soma: {a + b}"

TOOLS = {
    "search_flights": tool_search_flights,
    "get_weather": tool_get_weather,
    "calculate": tool_calculate,
}

# -----------------------
# Global default memory (NOT stored inside serializable state)
# -----------------------
DEFAULT_MEMORY = SQLiteMemory("final_agent_memory.db")

# -----------------------
# Sanitizer: remove non-serializables and LangGraph internals
# -----------------------
def is_simple_value(v: Any) -> bool:
    """Return True if v is safe to serialize with msgpack/jsonplus used by LangGraph."""
    simple_types = (str, int, float, bool, type(None))
    if isinstance(v, simple_types):
        return True
    if isinstance(v, (list, tuple)):
        return all(is_simple_value(x) for x in v)
    if isinstance(v, dict):
        return all(isinstance(k, str) and is_simple_value(x) for k, x in v.items())
    return False

def sanitize_state(state: dict) -> dict:
    """
    Return a copy of state containing only simple, serializable keys.
    Removes keys that start with '_' and values that are complex (like SQLiteMemory instances).
    """
    out = {}
    for k, v in state.items():
        if k.startswith("_"):
            continue
        # Skip the actual memory object (we use DEFAULT_MEMORY instead)
        if isinstance(v, SQLiteMemory):
            continue
        if is_simple_value(v):
            out[k] = v
        else:
            # If it's a list/dict potentially containing simple elements, try to clean it
            if isinstance(v, list):
                cleaned = []
                for item in v:
                    if is_simple_value(item):
                        cleaned.append(item)
                out[k] = cleaned
            # else: skip complex types
    return out

# -----------------------
# Estado (DICT factory)
# -----------------------
def make_initial_state(user_input: str) -> Dict[str, Any]:
    return {
        "user_input": user_input,
        "plan": [],                 # list[str]
        "current_step": 0,
        "intermediate_results": [], # list[str]
        "selected_tool": None,      # optional
        "approval": None,           # human approval if needed
        "final_output": None,
        # DO NOT put SQLiteMemory here; nodes will use DEFAULT_MEMORY if missing
    }

# -----------------------
# Helper to obtain memory object for runtime (not serialized)
# -----------------------
def get_runtime_memory(state: Dict[str, Any]) -> SQLiteMemory:
    """
    Return the SQLiteMemory instance to use at runtime.
    Preference order:
      1. explicit `memory` key (rare)
      2. DEFAULT_MEMORY
    """
    mem = state.get("memory")
    if isinstance(mem, SQLiteMemory):
        return mem
    return DEFAULT_MEMORY

# -----------------------
# Planner node (gera plano com passos)
# Passos podem ser:
# - "ANALYZE"
# - "TOOL:search_flights São Paulo Salvador"
# - "HUMAN_REVIEW"
# - "SUMMARIZE"
# -----------------------
def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state.get("user_input", "").lower()
    print("\n🧠 [Planner] Gerando plano para:", state.get("user_input"))

    plan: List[str] = []
    plan.append("ANALYZE")

    # Decide tools based on keywords
    if "voo" in query or "viajar" in query:
        plan.append("TOOL:search_flights São Paulo Salvador")
        plan.append("TOOL:get_weather Salvador")

    if "somar" in query or "soma" in query:
        plan.append("TOOL:calculate 2 3")

    # If query asks for verification, request human review mid-flow
    if "verificar" in query or "checar" in query:
        plan.append("HUMAN_REVIEW")

    plan.append("SUMMARIZE")

    # Build new partial state and sanitize before returning (avoid non-serializable)
    new_state = {
        **state,
        "plan": plan,
        "current_step": 0,
        "intermediate_results": []
    }
    return sanitize_state(new_state)


# -----------------------
# Executor node
# Executa o passo atual. Se o passo for HUMAN_REVIEW, lança GraphInterrupt.
# -----------------------
def executor_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # runtime memory object (not serialized)
    runtime_mem = get_runtime_memory(state)

    # ensure keys exist (planner should have set them, but be defensive)
    idx = state.get("current_step", 0)
    plan = state.get("plan", [])

    if idx >= len(plan):
        return sanitize_state(state)

    step = plan[idx]
    print(f"\n⚙️ [Executor] Executando passo {idx+1}/{len(plan)}: {step}")

    # HUMAN_REVIEW requires human intervention
    if step == "HUMAN_REVIEW":
        # if approval already in state, continue (no interrupt)
        if state.get("approval"):
            # mark progress and return sanitized state
            state["current_step"] = idx + 1
            return sanitize_state(state)
        # raise interrupt (v1.0.3 uses single-argument GraphInterrupt)
        raise GraphInterrupt("REVIEW_REQUIRED")

    # TOOL handling
    if isinstance(step, str) and step.startswith("TOOL:"):
        _, raw = step.split(":", 1)
        parts = raw.strip().split()
        tool_name = parts[0]
        args = parts[1:]

        # normalize args: if number of args fits function signature, call accordingly
        if tool_name not in TOOLS:
            result = f"Erro: ferramenta '{tool_name}' não encontrada"
        else:
            if tool_name == "calculate":
                # expect two ints
                try:
                    a = int(args[0])
                    b = int(args[1])
                except Exception:
                    a, b = 2, 3
                result = TOOLS[tool_name](a, b)
            elif tool_name == "search_flights":
                origin = args[0] if args else "OrigemDesconhecida"
                destination = " ".join(args[1:]) if len(args) > 1 else "DestinoDesconhecido"
                result = TOOLS[tool_name](origin, destination)
            elif tool_name == "get_weather":
                location = " ".join(args) if args else "LocalDesconhecido"
                result = TOOLS[tool_name](location)
            else:
                # generic
                result = TOOLS[tool_name](*args)

        # persist result in intermediate_results and memory (runtime memory)
        state.setdefault("intermediate_results", []).append(result)
        try:
            runtime_mem.add(f"STEP-{idx+1}: {step} => {result}")
        except Exception:
            # if memory add fails, ignore but keep execution
            print("⚠️ Falha ao gravar na memória (ignorada)")

        # advance pointer
        state["current_step"] = idx + 1
        return sanitize_state(state)

    # ANALYZE or SUMMARIZE or generic step - simulate LLM work
    if step == "ANALYZE":
        res = llm.respond(f"Analyze: {state.get('user_input')}")
        state.setdefault("intermediate_results", []).append(res)
        try:
            runtime_mem.add(f"STEP-{idx+1}: ANALYZE => {res}")
        except Exception:
            pass
        state["current_step"] = idx + 1
        return sanitize_state(state)

    if step == "SUMMARIZE":
        # build summary from intermediate_results
        summary = " | ".join(state.get("intermediate_results", []))
        res = llm.respond(f"Summarize: {summary}")
        state.setdefault("intermediate_results", []).append(res)
        try:
            runtime_mem.add(f"STEP-{idx+1}: SUMMARIZE => {res}")
        except Exception:
            pass
        state["final_output"] = f"FINAL SUMMARY: {res}"
        state["current_step"] = idx + 1
        return sanitize_state(state)

    # fallback: just append a note
    res = llm.respond(f"Execute: {step}")
    state.setdefault("intermediate_results", []).append(res)
    try:
        runtime_mem.add(f"STEP-{idx+1}: {step} => {res}")
    except Exception:
        pass
    state["current_step"] = idx + 1
    return sanitize_state(state)


# -----------------------
# Final node (returns final_output if any)
# -----------------------
def finalize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    fo = state.get("final_output")
    if fo:
        return {"final_output": fo}
    # if no final_output, generate from intermediate results
    res = " | ".join(state.get("intermediate_results", []))
    return {"final_output": f"[FINAL GENERATED] {res}"}

# -----------------------
# Build graph
# -----------------------
builder = StateGraph(dict)

builder.add_node("planner", planner_node)
builder.add_node("executor", executor_node)
builder.add_node("finalize", finalize_node)

# Entry is planner
builder.set_entry_point("planner")

builder.add_edge("planner", "executor")
# loop executor until all steps done, then finalize
builder.add_conditional_edges(
    "executor",
    lambda s: "executor" if s.get("current_step", 0) < len(s.get("plan", [])) else "finalize",
    {
        "executor": "executor",
        "finalize": "finalize",
    },
)

builder.add_edge("finalize", END)

graph = builder.compile(checkpointer=MemorySaver())


# -----------------------
# Run demonstration
# -----------------------
def run_demo(user_text: str, thread_id: str = "final-agent-12"):
    state = make_initial_state(user_text)

    try:
        print("\n--- Executando agente (primeira invocação) ---")
        result = graph.invoke(state, config={"configurable": {"thread_id": thread_id}})
        # if finished without interrupts, print final result
        print("\n✅ Execução finalizada (sem interrupt):")
        print("final_output:", result.get("final_output"))
        return result

    except GraphInterrupt as interrupt:
        # interrupt.value contains the keyword (v1.0.3)
        print("\n📣 INTERRUPÇÃO solicitada pelo grafo:", interrupt.value)
        # inspect status saved in checkpoint: we can resume by providing approval in next invoke
        print("Estado salvo. Simulando intervenção humana para CONTINUAR...")
        # simulate human approval (approve)
        resumed = graph.invoke({"approval": "approved"}, config={"configurable": {"thread_id": thread_id}})
        print("\n✅ Fluxo retomado após intervenção:")
        print("final_output:", resumed.get("final_output"))
        return resumed

if __name__ == "__main__":
    # Example 1: flow that triggers tools and finishes
    run_demo("Quero viajar e verificar voos e clima")  # will call search_flights and get_weather

    # Example 2: flow that triggers human review (uses 'verificar' keyword)
    run_demo("Por favor, verificar e aprovar este relatório")