class Categoria:
    """Uma categoria de produtos (ex: Bebidas, Papelaria)."""

    def __init__(self, nome, descricao=None, id_categoria=None):
        self.id_categoria = id_categoria
        self.nome = nome
        self.descricao = descricao    

    def __str__(self):
        return f"{self.id_categoria} - {self.nome}"