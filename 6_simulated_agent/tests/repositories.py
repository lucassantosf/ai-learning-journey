import sys
import os
from pprint import pprint
from datetime import datetime

# Caminho absoluto para o diretório pai da pasta 'tests'
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Adiciona 'src' à variável de path para imports funcionarem
sys.path.append(os.path.join(BASE_DIR, "src"))

from repository.produto_mem_repo import ProdutoMemRepository
from repository.pedido_mem_repo import PedidoMemRepository
from repository.estoque_mem_repo import EstoqueMemRepository
from models.produto import Produto
from models.pedido import Pedido, ItemPedido
from models.estoque import Estoque


def main():
    # Inicializa os repositórios
    produto_repo = ProdutoMemRepository()
    pedido_repo = PedidoMemRepository()
    estoque_repo = EstoqueMemRepository()

    print("✅ Produtos disponíveis:")
    pprint(produto_repo.listar_todos())
    print("\n")

    # Teste: Criar produto novo
    novo_produto = Produto(id="p011", nome="Headset Gamer RGB", quantidade=20, avaliacao_media=4.6)
    produto_repo.criar(novo_produto)
    print("➕ Produto criado:")
    pprint(produto_repo.buscar_por_id("p011"))
    print("\n")

    # Teste: Atualizar produto
    produto_para_atualizar = produto_repo.buscar_por_id("p011")
    produto_para_atualizar.avaliacao_media = 4.7
    produto_repo.atualizar(produto_para_atualizar)
    print("✏️ Produto atualizado (nota):")
    pprint(produto_repo.buscar_por_id("p011"))
    print("\n")

    # Teste: Adicionar estoque
    estoque_repo.adicionar(Estoque(produto_id="p011", quantidade=5))
    print("➕ Estoque após adicionar 5 unidades:")
    pprint(estoque_repo.listar_todos())
    print("\n")

    # Teste: Remover estoque
    estoque_repo.remover(produto_id="p011", quantidade=3)
    print("➖ Estoque após remover 3 unidades:")
    pprint(estoque_repo.listar_todos())
    print("\n")

    # Teste: Criar pedido
    itens = [ItemPedido(produto_id="p001", quantidade=1), ItemPedido(produto_id="p002", quantidade=2)]
    novo_pedido = Pedido(id="pedido_001", itens=itens, data_criacao=datetime.now())
    pedido_repo.criar(novo_pedido)
    print("📦 Pedido criado:")
    pprint(pedido_repo.buscar_por_id("pedido_001"))
    print("\n")

    # Teste: Avaliar pedido
    pedido_repo.avaliar("pedido_001", 4.8)
    print("🌟 Pedido avaliado:")
    pprint(pedido_repo.buscar_por_id("pedido_001"))
    print("\n")

    # Teste: Listar todos os pedidos
    print("📋 Lista de todos os pedidos:")
    pprint(pedido_repo.listar_todos())
    print("\n")

    # Teste: Deletar produto
    produto_repo.deletar("p011")
    print("❌ Produto deletado (p011):")
    pprint(produto_repo.listar_todos())
    print("\n")


if __name__ == "__main__":
    main()
