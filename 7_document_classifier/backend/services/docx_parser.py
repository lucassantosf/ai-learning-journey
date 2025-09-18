import docx2txt
import os

class DocxParser:
    """
    Uma classe para ler e extrair texto de arquivos .docx.
    """

    def __init__(self, file_path):
        """
        Inicializa a classe com o caminho do arquivo.

        Args:
            file_path (str): O caminho completo para o arquivo .docx.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"O arquivo não foi encontrado: {file_path}")
        self.file_path = file_path

    def get_text(self):
        """
        Extrai e retorna o texto completo do arquivo .docx.

        Returns:
            str: O texto extraído do arquivo.
        """
        try:
            # Extrai o texto do arquivo usando docx2txt
            text = docx2txt.process(self.file_path)
            return text
        except Exception as e:
            print(f"Ocorreu um erro ao processar o arquivo: {e}")
            return ""

# Exemplo de uso da classe
if __name__ == "__main__":
    # Crie um arquivo .docx de teste manualmente ou coloque o seu próprio.
    # Exemplo: 'lorem_ipsum.docx'
    
    # Substitua 'caminho/para/seu/arquivo.docx' pelo caminho real do seu arquivo.
    caminho_do_arquivo = 'lorem_ipsum.docx' 

    try:
        reader = DocxParser(caminho_do_arquivo)
        conteudo = reader.get_text()
        
        if conteudo:
            print("Conteúdo do arquivo .docx:")
            print("---")
            print(conteudo)
    
    except FileNotFoundError as e:
        print(e)