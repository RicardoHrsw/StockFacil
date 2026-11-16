from src.ligacao import obter_ligacao
from src.modelos.fornecedor import Fornecedor


def linha_para_fornecedor(linha):
    """Transforma uma linha do SELECT num objeto Fornecedor."""
    return Fornecedor(id_fornecedor=linha[0], nome=linha[1], nif=linha[2],
                      telefone=linha[3], email=linha[4], morada=linha[5])


class FornecedorRepositorio:
    """Guarda e lê fornecedores da base de dados."""

    def criar(self, fornecedor):
        """Guarda um fornecedor novo e devolve-o já com o id."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO fornecedor (nome, nif, telefone, email, morada)
                       VALUES (%s, %s, %s, %s, %s)
                       RETURNING id_fornecedor""",
                    (fornecedor.nome, fornecedor.nif, fornecedor.telefone, fornecedor.email, fornecedor.morada),
                )
                fornecedor.id_fornecedor = cursor.fetchone()[0]
        return fornecedor

    def listar(self):
        """Devolve todos os fornecedores, ordenados por nome."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_fornecedor, nome, nif, telefone, email, morada FROM fornecedor ORDER BY nome"
                )
                linhas = cursor.fetchall()
        return [linha_para_fornecedor(linha) for linha in linhas]

    def obter(self, id_fornecedor):
        """Devolve o fornecedor com este id, ou None se não existir."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "SELECT id_fornecedor, nome, nif, telefone, email, morada FROM fornecedor WHERE id_fornecedor = %s",
                    (id_fornecedor,),
                )
                linha = cursor.fetchone()
        if linha is None:
            return None
        return linha_para_fornecedor(linha)

    def editar(self, fornecedor):
        """Atualiza os dados do fornecedor. Devolve False se não existir."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """UPDATE fornecedor
                       SET nome = %s, nif = %s, telefone = %s, email = %s, morada = %s
                       WHERE id_fornecedor = %s""",
                    (fornecedor.nome, fornecedor.nif, fornecedor.telefone, fornecedor.email,
                     fornecedor.morada, fornecedor.id_fornecedor),
                )
                return cursor.rowcount > 0

    def apagar(self, id_fornecedor):
        """Apaga o fornecedor. Devolve False se não existir."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute("DELETE FROM fornecedor WHERE id_fornecedor = %s", (id_fornecedor,))
                return cursor.rowcount > 0
