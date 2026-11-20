from src.ligacao import obter_ligacao
from src.modelos.utilizador import Utilizador

SELECT_UTILIZADOR = """SELECT u.id_utilizador, u.nome, u.username, u.password_hash,
                              u.id_perfil, p.nome, u.ativo, u.tentativas_falhadas
                       FROM utilizador u
                       JOIN perfil p ON p.id_perfil = u.id_perfil"""


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
                cursor.execute(f"{SELECT_UTILIZADOR} WHERE u.username = %s", (username,))
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

    def obter(self, id_utilizador):
        """Devolve o utilizador com este id, ou None se não existir."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(f"{SELECT_UTILIZADOR} WHERE u.id_utilizador = %s", (id_utilizador,))
                linha = cursor.fetchone()
        if linha is None:
            return None
        return linha_para_utilizador(linha)

    def listar(self):
        """Devolve todos os utilizadores, também os desativados, ordenados por username."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(f"{SELECT_UTILIZADOR} ORDER BY u.username")
                linhas = cursor.fetchall()
        return [linha_para_utilizador(linha) for linha in linhas]

    def listar_perfis(self):
        """Devolve os perfis como pares (id, nome)."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute("SELECT id_perfil, nome FROM perfil ORDER BY id_perfil")
                return cursor.fetchall()

    def criar(self, utilizador):
        """Guarda um utilizador novo e devolve-o já com o id."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO utilizador (nome, username, password_hash, id_perfil)
                       VALUES (%s, %s, %s, %s)
                       RETURNING id_utilizador""",
                    (utilizador.nome, utilizador.username, utilizador.password_hash, utilizador.id_perfil),
                )
                utilizador.id_utilizador = cursor.fetchone()[0]
        return utilizador

    def editar(self, utilizador):
        """Atualiza o nome, o username e o perfil. Devolve False se não existir ou estiver desativado."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """UPDATE utilizador SET nome = %s, username = %s, id_perfil = %s
                       WHERE id_utilizador = %s AND ativo""",
                    (utilizador.nome, utilizador.username, utilizador.id_perfil, utilizador.id_utilizador),
                )
                return cursor.rowcount > 0

    def desativar(self, id_utilizador):
        """Desativa o utilizador em vez de o apagar, para guardar o histórico das vendas."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "UPDATE utilizador SET ativo = FALSE WHERE id_utilizador = %s AND ativo",
                    (id_utilizador,),
                )
                return cursor.rowcount > 0
