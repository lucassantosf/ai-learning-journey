import sys
from pathlib import Path

# Adiciona o diretório src ao sys.path para facilitar os imports
sys.path.append(str(Path(__file__).resolve().parent / "src"))

# Importa e executa a interface do Streamlit
from ui.streamlit_app import main

if __name__ == "__main__":
    main()