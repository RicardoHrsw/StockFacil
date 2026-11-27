import bcrypt

from src.modelos.utilizador import MAXIMO_TENTATIVAS
from src import sessao
from src.repositorios.utilizador_repositorio import UtilizadorRepositorio
from src.servicos.registo_servico import RegistoServico

TAMANHO_MINIMO_PASSWORD = 6
TAMANHO_MAXIMO_PASSWORD = 72
PASSWORD_INICIAL = "admin"
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


def precisa_mudar_password(password):
    """Quem entra com a palavra-passe inicial tem de a mudar logo (RF21 e RF20)."""
    return password == PASSWORD_INICIAL


def validar_nova_password(nova, confirmacao):
    """Confirma que a nova palavra-passe é segura o suficiente e foi escrita duas vezes igual."""
    nova = nova or ""
    if len(nova) < TAMANHO_MINIMO_PASSWORD:
        raise ValueError(f"A palavra-passe tem de ter pelo menos {TAMANHO_MINIMO_PASSWORD} caracteres.")
    if len(nova.encode("utf-8")) > TAMANHO_MAXIMO_PASSWORD:
        raise ValueError(f"A palavra-passe não pode ter mais de {TAMANHO_MAXIMO_PASSWORD} caracteres.")
    if nova != confirmacao:
        raise ValueError("As duas palavras-passe não são iguais.")
    if precisa_mudar_password(nova):
        raise ValueError("Escolha uma palavra-passe diferente da inicial.")
    return nova


class AutenticacaoServico:
    """Regras do login: palavra-passe com hash e bloqueio após 5 tentativas falhadas."""

    def __init__(self):
        self.repositorio = UtilizadorRepositorio()
        self.registo = RegistoServico()

    def iniciar_sessao(self, username, password):
        """Devolve o utilizador se o login estiver certo; senão dá erro com uma mensagem clara."""
        username = (username or "").strip()
        password = password or ""
        if username == "" or password == "":
            raise ValueError("Escreva o username e a palavra-passe.")

        utilizador = self.repositorio.obter_por_username(username)
        if utilizador is None or not utilizador.ativo:
            self.registo.registar("LOGIN_FALHADO", f"username '{username}'", utilizador)
            raise ValueError(MENSAGEM_DADOS_ERRADOS)
        if utilizador.bloqueado:
            self.registo.registar("LOGIN_FALHADO", "conta bloqueada", utilizador)
            raise ValueError(MENSAGEM_BLOQUEADA)

        if not password_correta(password, utilizador.password_hash):
            tentativas = self.repositorio.somar_tentativa_falhada(utilizador.id_utilizador)
            self.registo.registar("LOGIN_FALHADO", f"palavra-passe errada ({tentativas}.ª vez)", utilizador)
            if tentativas >= MAXIMO_TENTATIVAS:
                self.registo.registar("CONTA_BLOQUEADA", f"{MAXIMO_TENTATIVAS} tentativas falhadas", utilizador)
                raise ValueError(f"Palavra-passe errada {MAXIMO_TENTATIVAS} vezes seguidas. " + MENSAGEM_BLOQUEADA)
            raise ValueError(MENSAGEM_DADOS_ERRADOS)

        if utilizador.tentativas_falhadas > 0:
            self.repositorio.limpar_tentativas(utilizador.id_utilizador)
            utilizador.tentativas_falhadas = 0
        sessao.iniciar(utilizador)
        self.registo.registar("LOGIN", None, utilizador)
        return utilizador

    def terminar_sessao(self, utilizador):
        """Regista o fim da sessão (RF03) e esquece quem estava a usar o programa."""
        sessao.terminar()
        self.registo.registar("LOGOUT", None, utilizador)

    def alterar_password(self, utilizador, atual, nova, confirmacao):
        """Muda a palavra-passe do utilizador, que tem de indicar a atual (RF20)."""
        if not password_correta(atual or "", utilizador.password_hash):
            raise ValueError("A palavra-passe atual está errada.")
        nova = validar_nova_password(nova, confirmacao)
        if nova == atual:
            raise ValueError("A nova palavra-passe tem de ser diferente da atual.")
        novo_hash = gerar_hash(nova)
        if not self.repositorio.alterar_password(utilizador.id_utilizador, novo_hash):
            raise ValueError("Este utilizador já não existe ou foi desativado.")
        utilizador.password_hash = novo_hash
        self.registo.registar("ALTERAR_PASSWORD", None, utilizador)
