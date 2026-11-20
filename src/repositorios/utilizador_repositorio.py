from src.ligacao import obter_ligacao
from src.modelos.utilizador import Utilizador


def linha_para_utilizador(linha):
    """Transforma uma linha do SELECT num objeto Utilizador."""
    return Utilizador(
        id_utilizador=linha[0], nome=linha[1], username=linha[2], password_hash=linha[3],
        id_perfil=linha[4], nome_perfil=linha[5], ativo=linha[6], tentativas_falhadas=linha[7],
    )


class UtilizadorRepositorio:
    """Guarda e lê utilizadores da base de dados."""

    def obter_por_username(self, username):
        """Devolve o utilizador com este username, ou None se não existir."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """SELECT u.id_utilizador, u.nome, u.username, u.password_hash,
                              u.id_perfil, p.nome, u.ativo, u.tentativas_falhadas
                       FROM utilizador u
                       JOIN perfil p ON p.id_perfil = u.id_perfil
                       WHERE u.username = %s""",
                    (username,),
                )
                linha = cursor.fetchone()
        if linha is None:
            return None
        return linha_para_utilizador(linha)

    def somar_tentativa_falhada(self, id_utilizador):
        """Soma 1 às tentativas falhadas e devolve o novo total."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """UPDATE utilizador
                       SET tentativas_falhadas = tentativas_falhadas + 1
                       WHERE id_utilizador = %s
                       RETURNING tentativas_falhadas""",
                    (id_utilizador,),
                )
                return cursor.fetchone()[0]

    def alterar_password(self, id_utilizador, password_hash):
        """Guarda o hash da nova palavra-passe. Devolve False se o utilizador não existir."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "UPDATE utilizador SET password_hash = %s WHERE id_utilizador = %s AND ativo",
                    (password_hash, id_utilizador),
                )
                return cursor.rowcount > 0

    def limpar_tentativas(self, id_utilizador):
        """Põe as tentativas falhadas a 0, depois de um login com sucesso."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "UPDATE utilizador SET tentativas_falhadas = 0 WHERE id_utilizador = %s",
                    (id_utilizador,),
                )
