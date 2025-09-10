from src.agent.memory import Memory
from src.agent.agent import Agent

# Mock simples do agente
class TestAgentSummarizer:
    def _send_to_model(self, prompt):
        user_text = next((p["content"] for p in prompt if p["role"] == "user"), "")
        return f"(Resumo narrativo) O usuário interagiu: {user_text[:60]}..."

if __name__ == "__main__":
    memory = Memory(max_messages=10)
    agent = Agent('gemini')

    # Adiciona algumas mensagens de teste
    memory.add_message("system", "Você é um assistente.")
    memory.add_message("user", "Quero ver os produtos disponíveis.")
    memory.add_message("assistant", "Aqui estão os produtos: Webcam, Mouse, Teclado.")
    memory.add_message("user", "Adicione uma Webcam ao carrinho.")
    memory.add_message("assistant", "Webcam adicionada ao carrinho.")
    memory.add_message("user", "Agora finalize o pedido.")

    print("\n=== Antes do resumo ===")
    for msg in memory.history:
        print(f"{msg['role']}: {msg['content']}")

    # Força o resumo
    memory._maybe_summarize_block(agent=agent, summarize_every=3)

    print("\n=== Depois do resumo ===")
    for msg in memory.history:
        print(f"{msg['role']}: {msg['content']}")

    memory_ = Memory(max_messages=10)
    memory_.add_message("system", "Você é um assistente.")
    memory_.add_message("user", "Quero ver os produtos disponíveis.")
    memory_.add_message("assistant", "Aqui estão os produtos: Tinta, carrinho, areia, pedra.")
    memory_.add_message("user", "Adicione uma Tinta ao carrinho.")
    memory_.add_message("assistant", "Tinta adicionada ao carrinho.")
    memory_.add_message("user", "Agora finalize o pedido.")

    print("\n=== Antes do resumo ===")
    for msg in memory_.history:
        print(f"{msg['role']}: {msg['content']}")

    # Força o resumo
    memory_._maybe_summarize_block(agent=agent, summarize_every=1, chat=True)

    print("\n=== Depois do resumo ===")
    for msg in memory_.history:
        print(f"{msg['role']}: {msg['content']}")