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

    def listar(self):
        """Devolve uma lista com todas as categorias."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute("SELECT id_categoria, nome, descricao FROM categoria ORDER BY nome")
                linhas = cursor.fetchall()

        categorias = []
        for linha in linhas:
            categorias.append(Categoria(nome=linha[1], descricao=linha[2], id_categoria=linha[0]))
        return categorias