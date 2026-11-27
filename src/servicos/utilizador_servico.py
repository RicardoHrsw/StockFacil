from psycopg.errors import UniqueViolation

from src.modelos.utilizador import PERFIL_ADMINISTRADOR, Utilizador
from src.repositorios.utilizador_repositorio import UtilizadorRepositorio
from src.servicos.autenticacao_servico import gerar_hash, validar_nova_password
from src.servicos.registo_servico import RegistoServico

TAMANHO_MAXIMO_NOME = 100
TAMANHO_MAXIMO_USERNAME = 50


def validar_dados(nome, username):
    """Limpa e valida o nome e o username. Devolve os dois prontos a gravar."""
    nome = (nome or "").strip()
    username = (username or "").strip()

    if nome == "":
        raise ValueError("O nome não pode estar vazio.")
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise ValueError(f"O nome não pode ter mais de {TAMANHO_MAXIMO_NOME} caracteres.")
    if username == "":
        raise ValueError("O username não pode estar vazio.")
    if len(username) > TAMANHO_MAXIMO_USERNAME:
        raise ValueError(f"O username não pode ter mais de {TAMANHO_MAXIMO_USERNAME} caracteres.")
    if " " in username:
        raise ValueError("O username não pode ter espaços.")
    return nome, username


def converter_id(valor, mensagem):
    """Confirma que o número escolhido é um inteiro positivo."""
    try:
        numero = int(str(valor).strip())
    except ValueError:
        raise ValueError(mensagem)
    if numero <= 0:
        raise ValueError(mensagem)
    return numero


class UtilizadorServico:
    """Regras da gestão de utilizadores, feita pelo Administrador (RF04 e RF05)."""

    def __init__(self):
        self.repositorio = UtilizadorRepositorio()
        self.registo = RegistoServico()

    def listar(self):
        """Devolve todos os utilizadores, ordenados por username."""
        return self.repositorio.listar()

    def listar_perfis(self):
        """Devolve os perfis como pares (id, nome)."""
        return self.repositorio.listar_perfis()

    def obter(self, id_utilizador):
        """Devolve o utilizador com este número, ou dá erro se não existir."""
        id_utilizador = converter_id(id_utilizador, "Escolha um utilizador da lista, pelo número.")
        utilizador = self.repositorio.obter(id_utilizador)
        if utilizador is None:
            raise ValueError(f"Não existe nenhum utilizador com o número {id_utilizador}.")
        return utilizador

    def obter_perfil(self, id_perfil):
        """Devolve o par (id, nome) do perfil escolhido, ou dá erro se não existir."""
        id_perfil = converter_id(id_perfil, "Escolha um perfil da lista, pelo número.")
        for perfil in self.listar_perfis():
            if perfil[0] == id_perfil:
                return perfil
        raise ValueError("Escolha um perfil da lista, pelo número.")

    def criar(self, nome, username, id_perfil, password, confirmacao):
        """Valida os dados e cria o utilizador com a palavra-passe definida pelo Administrador."""
        nome, username = validar_dados(nome, username)
        perfil = self.obter_perfil(id_perfil)
        password = validar_nova_password(password, confirmacao)
        utilizador = Utilizador(nome, username, gerar_hash(password), perfil[0], perfil[1])
        try:
            utilizador = self.repositorio.criar(utilizador)
        except UniqueViolation:
            raise ValueError(f"Já existe um utilizador com o username '{username}'.")
        self.registo.registar("CRIAR_UTILIZADOR", f"{username} ({perfil[1]})")
        return utilizador

    def editar(self, id_utilizador, nome, username, id_perfil, sessao):
        """Muda o nome, o username e o perfil. O Administrador não pode tirar a si próprio o perfil."""
        utilizador = self.obter(id_utilizador)
        nome, username = validar_dados(nome, username)
        perfil = self.obter_perfil(id_perfil)
        if utilizador.id_utilizador == sessao.id_utilizador and perfil[1] != PERFIL_ADMINISTRADOR:
            raise ValueError("Não pode tirar a si próprio o perfil de Administrador.")

        utilizador.nome, utilizador.username = nome, username
        utilizador.id_perfil, utilizador.nome_perfil = perfil
        try:
            encontrado = self.repositorio.editar(utilizador)
        except UniqueViolation:
            raise ValueError(f"Já existe um utilizador com o username '{username}'.")
        if not encontrado:
            raise ValueError("Este utilizador está desativado e não pode ser editado.")
        self.registo.registar("EDITAR_UTILIZADOR", f"{username} ({utilizador.nome_perfil})")
        return utilizador

    def desativar(self, id_utilizador, sessao):
        """Desativa o utilizador: deixa de poder entrar, mas o histórico fica guardado."""
        utilizador = self.obter(id_utilizador)
        if utilizador.id_utilizador == sessao.id_utilizador:
            raise ValueError("Não pode desativar a sua própria conta.")
        if not self.repositorio.desativar(utilizador.id_utilizador):
            raise ValueError("Este utilizador já estava desativado.")
        self.registo.registar("DESATIVAR_UTILIZADOR", utilizador.username)
        return utilizador

    def desbloquear(self, id_utilizador):
        """Volta a deixar entrar uma conta bloqueada por 5 tentativas falhadas (RF05)."""
        utilizador = self.obter(id_utilizador)
        if not utilizador.bloqueado:
            raise ValueError(f"A conta de '{utilizador.username}' não está bloqueada.")
        self.repositorio.limpar_tentativas(utilizador.id_utilizador)
        utilizador.tentativas_falhadas = 0
        self.registo.registar("DESBLOQUEAR_UTILIZADOR", utilizador.username)
        return utilizador
