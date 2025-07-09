import uuid

class TextChunker:
    def __init__(self, chunk_size=700, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, text, source="unknown"):
        chunks, start = [], 0

        while start < len(text):
            end = start + self.chunk_size
            if start > 0:
                start -= self.chunk_overlap

            chunk = text[start:end]
            if end < len(text):
                last_period = chunk.rfind(".")
                if last_period != -1:
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1

            chunks.append({
                "id": str(uuid.uuid4()),
                "text": chunk,
                "metadata": {"source": source}
            })
            start = end
        return chunks
