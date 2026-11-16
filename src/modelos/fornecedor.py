class Fornecedor:
    """Uma empresa a quem a loja compra mercadoria."""

    def __init__(self, nome, nif=None, telefone=None, email=None, morada=None, id_fornecedor=None):
        self.id_fornecedor = id_fornecedor
        self.nome = nome
        self.nif = nif
        self.telefone = telefone
        self.email = email
        self.morada = morada

    def __str__(self):
        return f"{self.id_fornecedor} - {self.nome}"
