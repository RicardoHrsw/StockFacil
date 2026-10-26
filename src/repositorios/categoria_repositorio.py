from src.ligacao import obter_ligacao
from src.modelos.categoria import Categoria

class CategoriaRepositorio:
    """Guarda e lê categorias da base de dados."""
    def criar(self, categoria):
        """Guarda uma categoria nova e devolve-a já com o id."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO categoria (nome, descricao) VALUES (%s, %s) RETURNING id_categoria",
                    (categoria.nome, categoria.descricao),
                )
                categoria.id_categoria = cursor.fetchone()[0]
        return categoria