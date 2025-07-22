import uuid
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

class TextChunker:
    def __init__(self, chunk_size=700, chunk_overlap=200):
        """
        Initialize a TextChunker for breaking text into semantic chunks.

        Args:
            chunk_size (int, optional): Maximum number of characters per chunk. Defaults to 700.
            chunk_overlap (int, optional): Number of characters to overlap between chunks. Defaults to 200.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, text, source="unknown"):
        """
        Break text into semantic chunks with optional overlap.

        Args:
            text (str): The input text to be chunked.
            source (str, optional): Source identifier for the text. Defaults to "unknown".

        Returns:
            list: A list of chunks, where each chunk is a dictionary containing:
                - id: Unique identifier for the chunk
                - chunk_index: Index of the chunk in the sequence
                - text: The actual text content of the chunk
                - metadata: Additional metadata about the chunk

        Raises:
            TypeError: If the input text is not a string.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected text to be str, got {type(text)}")

        sentences = sent_tokenize(text)
        chunks = []
        current_chunk, current_length = [], 0
        chunk_index = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size:
                chunk_text = " ".join(current_chunk).strip()
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "metadata": {"source": source}
                })
                chunk_index += 1
                # Start new chunk with overlap
                current_chunk = current_chunk[-self.chunk_overlap:] if self.chunk_overlap else []
                current_length = sum(len(s) for s in current_chunk)

            current_chunk.append(sentence)
            current_length += sentence_length

        # Last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk).strip()
            chunks.append({
                "id": str(uuid.uuid4()),
                "chunk_index": chunk_index,
                "text": chunk_text,
                "metadata": {"source": source}
            })

        return chunks
