# import libraries for frontend
import streamlit as st

# import libraries for backend
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

# Embedding Class
class EmbeddingModel:
    def __init__(self):
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

class LLMModel:
    def __init__(self):
        self.client = OpenAI(base_url="http://localhost:11434/v1",api_key="ollama")
        self.model_name = "llama3.2:1b"

    def generate_completion(self,messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0
            )
            return response.choices[0].message.content 
        except Exception as e:
            return f"Error generating response: {str(e)}" 

def load_questions():
    return [
        {"id": 1, "question": "Como faço para redefinir minha senha?", "answer": "Você pode redefinir sua senha clicando em 'Esqueci minha senha' na tela de login."},
        {"id": 2, "question": "Onde posso alterar meu e-mail cadastrado?", "answer": "Acesse seu perfil, vá em configurações de conta e atualize o campo de e-mail."},
        {"id": 3, "question": "Quais são os planos disponíveis no sistema?", "answer": "Oferecemos planos Básico, Profissional e Empresarial. Confira os detalhes na página de preços."},
        {"id": 4, "question": "Como posso cancelar minha conta?", "answer": "Entre em 'Configurações da Conta' e clique em 'Cancelar Conta'. Você também pode entrar em contato com o suporte."},
        {"id": 5, "question": "O sistema possui aplicativo para celular?", "answer": "Sim, nosso app está disponível para Android e iOS nas lojas oficiais."},
        {"id": 6, "question": "Como gero um relatório de atividades?", "answer": "Acesse o menu 'Relatórios' e selecione o tipo de atividade que deseja visualizar."},
        {"id": 7, "question": "Consigo exportar os dados para Excel ou PDF?", "answer": "Sim, em várias telas do sistema há a opção de exportação nos formatos Excel e PDF."},
        {"id": 8, "question": "É possível integrar com outros sistemas?", "answer": "Sim, temos uma API disponível e integrações prontas com diversos sistemas."},
        {"id": 9, "question": "Onde encontro o histórico das minhas ações?", "answer": "O histórico fica disponível no seu perfil, na aba 'Atividades recentes'."},
        {"id": 10, "question": "Como funciona a política de privacidade?", "answer": "Nossa política de privacidade está disponível no rodapé do site e explica como usamos seus dados."},
        {"id": 11, "question": "Posso cadastrar mais de um usuário na conta?", "answer": "Sim, em planos superiores você pode adicionar múltiplos usuários com diferentes níveis de acesso."},
        {"id": 12, "question": "O sistema envia notificações por e-mail?", "answer": "Sim, você pode configurar quais notificações deseja receber no seu perfil."},
        {"id": 13, "question": "Qual é o horário de atendimento do suporte?", "answer": "Nosso suporte está disponível de segunda a sexta, das 9h às 18h."},
        {"id": 14, "question": "Como faço o backup dos meus dados?", "answer": "Você pode solicitar um backup completo acessando as configurações de conta ou via suporte."},
        {"id": 15, "question": "O sistema armazena os dados em nuvem?", "answer": "Sim, todos os dados são armazenados com segurança em servidores em nuvem."},
        {"id": 16, "question": "Existe um modo escuro (dark mode)?", "answer": "Sim, você pode ativar o modo escuro nas preferências de visualização."},
        {"id": 17, "question": "É possível recuperar registros excluídos?", "answer": "Sim, registros excluídos ficam disponíveis na lixeira por até 30 dias."},
        {"id": 18, "question": "Qual a diferença entre os perfis de acesso?", "answer": "Os perfis definem permissões diferentes, como administrador, editor e visualizador."},
        {"id": 19, "question": "Consigo acompanhar as atualizações do sistema?", "answer": "Sim, todas as atualizações são divulgadas na aba 'Novidades' dentro do sistema."},
        {"id": 20, "question": "Onde posso alterar as configurações da minha conta?", "answer": "Basta acessar seu perfil e clicar em 'Configurações da Conta'."},
    ]

def setup_chromadb(documents, embedding_model):
    client = chromadb.Client()

    try:
        client.delete_collection("faqs")
    except:
        pass

    collection = client.create_collection(
        name="faqs", embedding_function=embedding_model.embedding_fn
    )

    collection.add(documents=documents, ids=[str(i) for i in range(len(documents))])
    return collection

def find_related_chunks(query, collection, top_k=2):
    results = collection.query(query_texts=[query], n_results=top_k)

    return list(
        zip(
            results["documents"][0],
            (
                results["metadatas"][0]
                if results["metadatas"][0]
                else [{}] * len(results["documents"][0])
            ),
        )
    )

def augment_prompt(query, related_chunks, example_q=None, example_a=None):
    context = "\n".join([chunk[0] for chunk in related_chunks])
    example_text = ""
    if example_q and example_a:
        example_text = f"Example:\nQuestion: {example_q}\nAnswer: {example_a}\n\n"          
    augmented_prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

    return augmented_prompt

def rag_pipeline(query, collection, llm_model, top_k=2, example_q=None, example_a=None):
    print(f"\nProcessing query: {query}")

    related_chunks = find_related_chunks(query, collection, top_k)
    augmented_prompt = augment_prompt(query, related_chunks, example_q, example_a)

    response = llm_model.generate_completion(
        [
            {
                "role": "system",
                "content": "You are a helpful assistant who can answer questions about our system through the FAQ in the sources/documents given.",
            },
            {"role": "user", "content": augmented_prompt},
        ]
    )

    references = [chunk[0] for chunk in related_chunks]
    return response, references

def main():
    # Initialize models
    llm_model = LLMModel()
    embedding_model = EmbeddingModel()

    # Generate and load data
    questions = load_questions()
    documents = [f"{q['question']} {q['answer']}" for q in questions]

    # Setup ChromaDB
    collection = setup_chromadb(documents, embedding_model)

    st.set_page_config(page_title="Faq Bot", layout="wide")
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2:
        st.title("💬 Chat")
        st.write("Ask your question about the FAQ below:")

        if "history" not in st.session_state:
            st.session_state.history = []

        # Caixa de texto que envia ao pressionar Enter
        user_input = st.text_input('')

        # Se houver entrada, adiciona ao histórico e gera resposta
        if user_input:

            st.session_state.history.append(user_input)

            # Exemplo de pergunta e resposta ideal para ajudar o modelo
            example_question = "Como faço para redefinir minha senha?"
            example_answer = "Você pode redefinir sua senha clicando em 'Esqueci minha senha' na tela de login."

            with st.spinner("Processing..."):
                # Chama a função RAG
                response, references = rag_pipeline(user_input, collection, llm_model, example_q=example_question, example_a=example_answer)

            st.markdown(f"**Bot:** {response}")
 
if __name__ == "__main__":
    main()