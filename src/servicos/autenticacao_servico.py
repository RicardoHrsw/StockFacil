import bcrypt

from src.modelos.utilizador import MAXIMO_TENTATIVAS
from src.repositorios.utilizador_repositorio import UtilizadorRepositorio

TAMANHO_MAXIMO_PASSWORD = 72
MENSAGEM_DADOS_ERRADOS = "Username ou palavra-passe errados."
MENSAGEM_BLOQUEADA = "Esta conta está bloqueada. Peça ao Administrador para a desbloquear."


def gerar_hash(password):
    """Transforma a palavra-passe num hash bcrypt, para nunca a guardar em texto simples (RNF01)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def password_correta(password, password_hash):
    """Confirma se a palavra-passe escrita corresponde ao hash guardado."""
    dados = password.encode("utf-8")
    if len(dados) > TAMANHO_MAXIMO_PASSWORD:
        return False
    return bcrypt.checkpw(dados, password_hash.encode("utf-8"))


class AutenticacaoServico:
    """Regras do login: palavra-passe com hash e bloqueio após 5 tentativas falhadas."""

    def __init__(self):
        self.repositorio = UtilizadorRepositorio()

    def iniciar_sessao(self, username, password):
        """Devolve o utilizador se o login estiver certo; senão dá erro com uma mensagem clara."""
        username = (username or "").strip()
        password = password or ""
        if username == "" or password == "":
            raise ValueError("Escreva o username e a palavra-passe.")

        utilizador = self.repositorio.obter_por_username(username)
        if utilizador is None or not utilizador.ativo:
            raise ValueError(MENSAGEM_DADOS_ERRADOS)
        if utilizador.bloqueado:
            raise ValueError(MENSAGEM_BLOQUEADA)

        if not password_correta(password, utilizador.password_hash):
            tentativas = self.repositorio.somar_tentativa_falhada(utilizador.id_utilizador)
            if tentativas >= MAXIMO_TENTATIVAS:
                raise ValueError(f"Palavra-passe errada {MAXIMO_TENTATIVAS} vezes seguidas. " + MENSAGEM_BLOQUEADA)
            raise ValueError(MENSAGEM_DADOS_ERRADOS)

        if utilizador.tentativas_falhadas > 0:
            self.repositorio.limpar_tentativas(utilizador.id_utilizador)
            utilizador.tentativas_falhadas = 0
        return utilizador
