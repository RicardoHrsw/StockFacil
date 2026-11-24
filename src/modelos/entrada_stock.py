class EntradaStock:
    """Mercadoria que chegou à loja: faz subir o stock do produto (RF10)."""

    def __init__(self, id_produto, id_fornecedor, id_utilizador, quantidade, preco_custo,
                 id_entrada=None, data_entrada=None, codigo_produto=None, nome_produto=None,
                 nome_fornecedor=None, username=None):
        self.id_entrada = id_entrada
        self.data_entrada = data_entrada
        self.id_produto = id_produto
        self.id_fornecedor = id_fornecedor
        self.id_utilizador = id_utilizador
        self.quantidade = quantidade
        self.preco_custo = preco_custo
        self.codigo_produto = codigo_produto
        self.nome_produto = nome_produto
        self.nome_fornecedor = nome_fornecedor
        self.username = username
