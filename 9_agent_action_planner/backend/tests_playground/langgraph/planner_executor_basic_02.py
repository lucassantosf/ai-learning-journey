# backend/tests_playground/langgraph/02_planner_executor_basic.py

from typing import List
import time

class SimplePlanner:
    def plan(self, goal: str) -> List[str]:
        return [
            f"1. Analisar o objetivo recebido: {goal}",
            "2. Identificar informações essenciais necessárias",
            "3. Pesquisar dados relevantes ao objetivo",
            "4. Criar rascunho inicial do plano",
            "5. Revisar o plano e ajustar a sequência de passos",
            "6. Gerar plano final estruturado e pronto para execução"
        ]

class SimpleExecutor:
    def execute(self, steps: List[str]):
        results = []
        for step in steps:
            print(f"Executando: {step}")
            time.sleep(0.5)
            results.append(f"Concluído: {step}")
        return results


if __name__ == "__main__":
    planner = SimplePlanner()
    executor = SimpleExecutor()

    plan = planner.plan("Planejar uma viagem de São Paulo a Salvador")
    print("Plano criado:")
    for step in plan:
        print(step)

    result = executor.execute(plan)
    print("\nResultados:")
    print(result)