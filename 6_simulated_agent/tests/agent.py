import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import Agent

def test_simple_communication():
    """
    Test basic communication with each LLM provider.
    
    This test checks if each provider can respond to a simple greeting.
    """
    # Test providers
    providers = ['openai', 'ollama', 'gemini']

    # Run simple communication test for each provider
    for provider in providers:
        print(f"\n--- Testing {provider.upper()} Provider Communication ---")
        try:
            # Initialize the agent with the current provider
            agent = Agent(provider)
            
            # Simple greeting test
            greeting = "Oi, boa tarde!"
            print(f"Sending greeting: {greeting}")
            
            try:
                # Call the agent with a simple greeting
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
        
        # Get provider selection
        while True:
            try:
                choice = int(input("Enter the number of the provider (1-4): "))
                if choice not in [1, 2, 3, 4]:
                    print("Invalid selection. Please choose 1-4.")
                    continue
                
                # Exit condition
                if choice == 4:
                    print("Exiting the application.")
                    return
                
                # Map selection to provider name
                providers = ['openai', 'ollama', 'gemini']
                selected_provider = providers[choice - 1]
                break
            except ValueError:
                print("Please enter a valid number.")
        
        # Initialize agent with selected provider
        try:
            agent = Agent(selected_provider)
            print(f"\n--- Interactive Chat with {selected_provider.upper()} Provider ---")
            print("Type 'exit' to change provider.")
            
            # Chat loop
            while True:
                # Get user input
                user_input = input("\nYou: ")
                
                # Check for exit condition
                if user_input.lower() == 'exit':
                    print("Returning to provider selection.")
                    break
                
                # Get and print agent response
                try:
                    response = agent.call(user_input)
                    print(f"Agent ({selected_provider.upper()}): {response}")
                except Exception as chat_error:
                    print(f"Error processing your message: {chat_error}")
        
        except Exception as init_error:
            print(f"Failed to initialize {selected_provider} provider: {init_error}")

def main():
    # Uncomment the function you want to run
    # test_simple_communication()
    interactive_chat()

if __name__ == "__main__":
    main()
