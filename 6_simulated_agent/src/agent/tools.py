from src.repository.produto_mem_repo import ProdutoMemRepository
from src.repository.pedido_mem_repo import PedidoMemRepository
from src.repository.estoque_mem_repo import EstoqueMemRepository

produto_repo = ProdutoMemRepository()
pedido_repo = PedidoMemRepository()
estoque_repo = EstoqueMemRepository(produto_repo)

def gerar_pedido(...):
    # gera pedido...
    repo.salvar(pedido)

def consultar_pedido(pedido_id):
    return repo.buscar(pedido_id)

def listar_pedidos():
    return repo.listar()

def avaliar_pedido(pedido_id, texto):
    pedido = repo.buscar(pedido_id)
    if pedido:
        pedido["avaliacao"] = texto
        repo.atualizar(pedido_id, pedido)