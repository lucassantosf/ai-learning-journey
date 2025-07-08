import streamlit as st
import json
from utils.SimplePDFProcessor import SimplePDFProcessor 
from utils.Summarizer import Summarizer

def main():

    st.set_page_config(page_title="Summarizer", layout="wide")

    # Initialize session state
    # if "processed_files" not in st.session_state:
    #     st.session_state.processed_files = set()
    # if "current_embedding_model" not in st.session_state:
    #     st.session_state.current_embedding_model = set()
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = set()

    st.title("📚 Summarizer: Geração Automática de Resumos e Flashcards com IA")
    st.write("Automatize seu aprendizado com resumos, perguntas e flashcards gerados por IA a partir de qualquer texto ou PDF.")

    # ==============================
    # Barra lateral com menu e configs
    # ==============================
    st.sidebar.header("🔷 Menu Principal")

    menu = st.sidebar.radio(
        "Escolha o modo de uso:",
        ["📄 Upload de PDF", "📝 Inserir texto manualmente", "🔍 Perguntar sobre conteúdo"]
    )

    st.sidebar.header("🔧 Configurações")
    num_questions = st.sidebar.slider("Quantidade de perguntas/flashcards", min_value=1, max_value=20, value=5)
    if st.sidebar.button("🔄 Resetar tudo"):
        st.experimental_rerun()

    # ==============================
    # Área principal
    # ==============================

    # Seção de upload ou entrada de texto
    content = None

    if menu == "📄 Upload de PDF":
        pdf_file = st.file_uploader("Envie um PDF com o conteúdo de estudo", type=["pdf"])
        if pdf_file is not None:
            
            # Aqui você extrairia o texto do PDF (simulação):
            processor = SimplePDFProcessor()
            with st.spinner("Processing PDF...."):
                try:
                    # Extract text
                    text = processor.read_pdf(pdf_file)

                    st.text_area("Texto extraído do PDF", value=text, height=300)
 
                    # Create chunks 
                    chunks = processor.create_chunks(text,pdf_file)

                    for chunk in chunks:
                        st.write(f"Chunk ID: {chunk['id']}")
                        st.write(f"Texto: {chunk['text']}...")

                    # Add to database
                    # if st.session_state.rag_system.add_documents(chunks):
                    #     st.session_state.processed_files.add(pdf_file.name)
                    #     st.success(f"Successfully processed {pdf_file.name}")

                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")

            content = f"Conteúdo simulado extraído do arquivo: {pdf_file.name}"
            st.success(f"PDF '{pdf_file.name}' carregado com sucesso!")

    elif menu == "📝 Inserir texto manualmente":

        content = st.text_area("Cole ou digite o conteúdo que deseja estudar", height=300)

        if st.button("Processar texto"):
            if content:
                with st.spinner("Processando texto..."):
                    # Simulação de processamento
                    summarizer = Summarizer()
                    summary = summarizer.generate_summary(content)
                    questions = summarizer.generate_questions(content, num_questions)

                    st.subheader("✅ Resumo gerado")
                    st.write(summary)

                    st.subheader("❓ Perguntas geradas")
                    for q in questions:
                        st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")

                    # Simulação de flashcards
                    flashcards = [{"front": q["question"], "back": q["answer"]} for q in questions]
                    
                    st.subheader("🃏 Flashcards gerados")
                    for f in flashcards:
                        st.markdown(f"**Frente:** {f['front']}  \n**Verso:** {f['back']}")

                st.success("Texto processado com sucesso!")
            else:
                st.error("Por favor, insira algum texto para processar.")

    elif menu == "🔍 Perguntar sobre conteúdo":
        user_question = st.text_input("Digite sua pergunta sobre o conteúdo:")
        if st.button("🔎 Responder"):
            # Simulação de resposta gerada
            st.write(f"Resposta simulada para a pergunta: **{user_question}**")
        st.stop()  # Não processa mais nada se o modo for "Perguntar sobre conteúdo"

    # 3️⃣ Botão de ação para gerar materiais de estudo
    if content:
        if st.button("📚 Gerar materiais de estudo"):
            with st.spinner("Gerando materiais com IA..."):
                # ====== Simulação do processamento ======
                summary = f"Resumo simulado do conteúdo (tamanho: {len(content)} caracteres)."
                questions = [
                    {"question": f"Pergunta {i+1} simulada?", "answer": f"Resposta {i+1} simulada."}
                    for i in range(num_questions)
                ]
                flashcards = [
                    {"front": q["question"], "back": q["answer"]}
                    for q in questions
                ]
                # ====== Fim do placeholder ======

                # 4️⃣ Resultado principal
                st.subheader("✅ Materiais Gerados")
                
                with st.expander("📌 Resumo do conteúdo"):
                    st.write(summary)

                with st.expander("❓ Perguntas para revisão"):
                    for q in questions:
                        st.markdown(f"**Q:** {q['question']}  \n**A:** {q['answer']}")

                with st.expander("🃏 Flashcards gerados"):
                    for f in flashcards:
                        st.markdown(f"**Frente:** {f['front']}  \n**Verso:** {f['back']}")
                
                # 5️⃣ Exportação
                export_data = {
                    "summary": summary,
                    "questions": questions,
                    "flashcards": flashcards
                }
                export_json = json.dumps(export_data, ensure_ascii=False, indent=2)

                st.download_button(
                    label="⬇️ Baixar materiais em JSON",
                    data=export_json,
                    file_name="materiais_estudo.json",
                    mime="application/json"
                )

                # CSV export simplificado (flashcards front/back)
                csv_data = "front,back\n" + "\n".join([f'"{f["front"]}","{f["back"]}"' for f in flashcards])
                st.download_button(
                    label="⬇️ Exportar flashcards para Anki (CSV)",
                    data=csv_data,
                    file_name="flashcards.csv",
                    mime="text/csv"
                )
                st.success("Materiais gerados com sucesso!")

    # 6️⃣ Rodapé
    st.markdown("---")
    st.caption("Desenvolvido por XXX. Powered by LLMs & Streamlit.") 

if __name__ == "__main__":
    main()