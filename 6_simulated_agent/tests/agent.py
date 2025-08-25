import sys
import os
import readline
import atexit

# Arquivo para armazenar histórico (pode escolher outro caminho se quiser separar)
histfile = os.path.expanduser("~/.agent_chat_history")

# Carrega histórico anterior (se existir)
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass

# Mantém no máximo 1000 entradas
readline.set_history_length(1000)

# Salva histórico no fim da execução também (caso saia de forma limpa)
atexit.register(readline.write_history_file, histfile)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import Agent


def test_simple_communication():
    """
    Test basic communication with each LLM provider.
    
    This test checks if each provider can respond to a simple greeting.
    """
    providers = ['openai', 'ollama', 'gemini']

    for provider in providers:
        print(f"\n--- Testing {provider.upper()} Provider Communication ---")
        try:
            agent = Agent(provider)

            greeting = "Oi, boa tarde!"
            print(f"Sending greeting: {greeting}")

            try:
                response = agent.call(greeting)
                print(f"{provider.upper()} Response: {response}")
            except Exception as communication_error:
                print(f"Communication error with {provider}: {communication_error}")

        except Exception as provider_error:
            print(f"Failed to initialize {provider} provider: {provider_error}")


def interactive_chat():
    """
    Interactive chat with the user where they can input questions 
    and receive responses from a selected LLM provider.
    Allows switching providers or exiting completely.
    """
    while True:
        # Select provider
        print("\nSelect an LLM Provider:")
        print("1. OpenAI")
        print("2. Ollama")
        print("3. Gemini")
        print("4. Exit")

        while True:
            try:
                choice = int(input("Enter the number of the provider (1-4): "))
                readline.write_history_file(histfile)  # salva histórico a cada input

                if choice not in [1, 2, 3, 4]:
                    print("Invalid selection. Please choose 1-4.")
                    continue

                if choice == 4:
                    print("Exiting the application.")
                    return

                providers = ['openai', 'ollama', 'gemini']
                selected_provider = providers[choice - 1]
                break
            except ValueError:
                print("Please enter a valid number.")

        try:
            agent = Agent(selected_provider)
            print(f"\n--- Interactive Chat with {selected_provider.upper()} Provider ---")
            print("Type 'exit' to change provider.")

            while True:
                user_input = input("\nYou: ")
                readline.write_history_file(histfile)  # salva histórico a cada input

                if user_input.lower() == 'exit':
                    print("Returning to provider selection.")
                    break

                if user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"\n--- Interactive Chat with {selected_provider.upper()} Provider ---")
                    print("Type 'exit' to change provider.")
                    continue

                try:
                    response = agent.call(user_input)
                    print(f"Agent ({selected_provider.upper()}): {response}")
                except Exception as chat_error:
                    print(f"Error processing your message: {chat_error}")

        except Exception as init_error:
            print(f"Failed to initialize {selected_provider} provider: {init_error}")


def main():
    # Uncomment if you want the simple test
    # test_simple_communication()
    interactive_chat()

if __name__ == "__main__":
    main()