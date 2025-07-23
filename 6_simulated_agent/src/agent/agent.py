from src.agent import tools, memory

def run_agent(task: str):
    notes = []

    print(f"Nova tarefa: {task}")
    search_result = tools.search(task)
    print("Busca feita.")

    summary = tools.read(search_result)
    print("Leitura feita.")

    tools.note(summary, notes)
    print("Anotação feita.")

    memory.save(notes)
    return notes[-1]
