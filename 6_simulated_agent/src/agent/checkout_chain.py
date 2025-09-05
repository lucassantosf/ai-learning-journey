class CheckoutChain:
    """
    Chain explícito para checkout:
    1) Normaliza/valida itens
    2) Valida estoque por item
    3) Gera o pedido (generate_order)
    4) Confirma e salva na memória
    """
    def __init__(self, agent):
        self.agent = agent
        self.log = agent.logger

    def run(self, customer_name, customer_document, items):
        # --- 0) Valida dados obrigatórios ---
        if not customer_name or not customer_document:
            raise ValueError("customer_name e customer_document são obrigatórios no checkout_chain.")
        items = self._normalize_items(items)
        if not items:
            raise ValueError("Lista de items vazia/ inválida no checkout_chain.")

        # Guarda contexto do checkout (stateful memory)
        self.agent.memory.set_state("checkout_customer_name", customer_name)
        self.agent.memory.set_state("checkout_customer_document", customer_document)
        self.agent.memory.set_state("checkout_items", items)

        # --- 1) Confirmar itens (aqui já normalizados) ---
        self.log.info("🔎 Confirmando itens do checkout...")

        # --- 2) Validar estoque (usa get_product(product_name=...)) ---
        self.log.info("📦 Validando estoque item a item...")
        insuficientes = []
        for it in items:
            prod = self.agent._run_tool("get_product", {"product_name": it["product_name"]})
            disponivel = getattr(prod, "quantity", None)
            nome_real = getattr(prod, "name", it["product_name"])

            if disponivel is None:
                raise ValueError(f"Produto '{nome_real}' sem atributo 'quantity' retornado por get_product.")
            if disponivel < it["quantity"]:
                insuficientes.append({
                    "product_name": nome_real,
                    "requested": it["quantity"],
                    "available": disponivel
                })

        if insuficientes:
            # Não segue para generate_order — encerra com falha (determinístico)
            return {
                "status": "failed",
                "reason": "Estoque insuficiente",
                "details": insuficientes
            }

        # --- 3) Gerar o pedido (agora sim com os 3 argumentos obrigatórios) ---
        self.log.info("📝 Chamando generate_order...")
        order_obj = self.agent._run_tool("generate_order", {
            "customer_name": customer_name,
            "customer_document": customer_document,
            "items": items  # formato: [{"product_name": "...", "quantity": N}, ...]
        })

        # --- 4) Confirmação + memória ---
        order_id = getattr(order_obj, "id", None)
        if order_id is None and isinstance(order_obj, dict):
            order_id = order_obj.get("order_id")
        if order_id is None:
            order_id = str(order_obj)

        self.agent.memory.set_state("ultimo_pedido", order_id)
        msg = f"Pedido {order_id} criado com sucesso 🎉"
        self.agent.memory.add_message("assistant", msg)

        return {
            "status": "success",
            "order_id": order_id,
            "message": msg
        }

    # ---------- Helpers ----------
    def _normalize_items(self, items):
        """
        Aceita variações comuns de chaves vindas do LLM e padroniza em:
        [{"product_name": str, "quantity": int>0}, ...]
        """
        if not items:
            return []
        norm = []
        for it in items:
            pname = (
                it.get("product_name")
                or it.get("name")
                or it.get("produto")
                or it.get("product")
            )
            qty = it.get("quantity") or it.get("qty") or it.get("quantidade")
            try:
                qty = int(qty)
            except Exception:
                qty = None
            if pname and qty and qty > 0:
                norm.append({"product_name": str(pname), "quantity": qty})
        return norm