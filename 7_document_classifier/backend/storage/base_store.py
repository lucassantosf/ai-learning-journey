from abc import ABC, abstractmethod

class BaseStore(ABC):
    @abstractmethod
    def save_vector(self, embedding, metadata):
        pass

    @abstractmethod
    def load_vectors(self):
        pass