from src.core.llm import LLMClient

class Summarizer:
    def __init__(self, use_openai=True):
        """
        Initialize the Summarizer with an LLM client.

        Args:
            use_openai (bool, optional): Whether to use OpenAI's LLM. Defaults to True.
        """
        self.llm = LLMClient(use_openai=use_openai)

    def generate_summary(self, text, max_words=200):
        """
        Generate a concise summary of the given text.

        Args:
            text (str): The text to be summarized.
            max_words (int, optional): Maximum number of words in the summary. Defaults to 200.

        Returns:
            str: A summary of the text.
        """
        prompt = f"Summarize this text in under {max_words} words:\n\n{text}"
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": prompt}
        ]
        return self.llm.chat(messages, max_tokens=max_words)

    def generate_questions(self, text, num_questions=5):
        """
        Generate study questions with answers based on the given text.

        Args:
            text (str): The text to generate questions from.
            num_questions (int, optional): Number of questions to generate. Defaults to 5.

        Returns:
            list: A list of dictionaries containing questions and answers.
        """
        prompt = f"Generate {num_questions} study questions with answers based on this text:\n\n{text}"
        messages = [
            {"role": "system", "content": "You create exam-style study questions."},
            {"role": "user", "content": prompt}
        ]
        raw = self.llm.chat(messages)

        questions = []
        current_q, current_a = "", []

        for line in raw.splitlines():
            if any(line.strip().lower().startswith(p) for p in ["q", "question", "1.", "2.", "3.", "4.", "5."]):
                if current_q:
                    questions.append({"question": current_q, "answer": " ".join(current_a).strip()})
                current_q = line.split(":", 1)[-1].strip()
                current_a = []
            elif current_q:
                current_a.append(line.strip())

        if current_q:
            questions.append({"question": current_q, "answer": " ".join(current_a).strip()})
        return questions[:num_questions]
