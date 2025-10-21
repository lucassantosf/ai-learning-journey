import pytest
from abc import ABC, abstractmethod
from src.ingestion.parser_base import DocumentParser


def test_cannot_instantiate_abstract_class():
    # Tenta instanciar a classe abstrata diretamente
    with pytest.raises(TypeError):
        DocumentParser()


def test_subclass_can_instantiate():
    # Define uma subclasse de teste que implementa parse
    class DummyParser(DocumentParser):
        def parse(self, file_path: str):
            return ["dummy page"]

    parser = DummyParser()
    result = parser.parse("anyfile.txt")

    assert result == ["dummy page"]
    assert isinstance(result, list)


def test_subclass_missing_implementation_raises():
    # Subclasse que não implementa parse ainda é abstrata
    class IncompleteParser(DocumentParser):
        pass

    with pytest.raises(TypeError):
        IncompleteParser()