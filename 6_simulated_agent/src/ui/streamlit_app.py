import streamlit as st
import re
from src.agent.agent import Agent
from src.utils.helpers import get_products

def get_or_create_agent():
    """Retrieve existing agent from session state or create a new one."""
    if 'agent' not in st.session_state:
        st.session_state.agent = Agent('gemini')
    return st.session_state.agent

def initialize_chat_history():
    """Initialize or retrieve the chat history from session state."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def display_chat_messages():
    """Display chat messages from history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def add_message(role, content):
    """Add a message to the chat history."""
    st.session_state.messages.append({"role": role, "content": content})

def show_product_images(products):
    """Dynamically show product images based on product IDs."""
    cols = st.columns(min(len(products), 3))
    
    for i, product_id in enumerate(products):
        product = get_products()[product_id]
        col = cols[i % len(cols)]
        with col:
            st.image(product.image_url, width=200, caption=f"{product.name}\nR${product.price}")
            st.write(f"⭐ {product.average_rating} | Estoque: {product.quantity}")

def detect_product_list(response):
    """
    Detect if the response contains a product list.
    Look for specific patterns that indicate a product listing.
    """
    # Patterns to detect product list
    product_list_patterns = [
        r'Lista de Produtos:',
        r'Catálogo de Produtos:',
        r'Produtos Disponíveis:',
        r'Nossos Produtos:'
    ]
    
    # Check if any pattern matches
    for pattern in product_list_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            # Extract product IDs if the pattern matches
            product_ids = re.findall(r'p\d{3}', response)
            return product_ids
    
    return None

def main():
    # Initialize the page configuration
    st.set_page_config(page_title="Agente Simulado", page_icon="🤖")
    st.title("🤖 Agente Simulado com IA")

    # Get or create agent with persistent memory
    agent = get_or_create_agent()

    # Initialize chat history
    initialize_chat_history()

    # Display existing messages
    display_chat_messages()

    # Chat input
    user_input = st.chat_input("Digite a tarefa que deseja que o agente realize")

    # Process user input
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Add user message to history
        add_message("user", user_input)

        # Generate agent response
        with st.chat_message("assistant"):
            with st.spinner("Executando..."):
                # Use the agent's memory to maintain context
                response = agent.call(user_input)
                st.markdown(response)
                
                # Check if response contains a product list
                product_ids = detect_product_list(response)
                if product_ids:
                    # Show images for mentioned products
                    st.markdown("### 📸 Imagens dos Produtos")
                    show_product_images(product_ids)
        
        # Add agent response to history
        add_message("assistant", response)

if __name__ == "__main__":
    main()
