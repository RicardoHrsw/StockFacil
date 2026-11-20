PERFIL_ADMINISTRADOR = "Administrador"
MAXIMO_TENTATIVAS = 5


class Utilizador:
    """Uma pessoa que usa o sistema, com o perfil Administrador ou Funcionário."""

    def __init__(self, nome, username, password_hash, id_perfil, nome_perfil=None, ativo=True,
                 tentativas_falhadas=0, id_utilizador=None):
        self.id_utilizador = id_utilizador
        self.nome = nome
        self.username = username
        self.password_hash = password_hash
        self.id_perfil = id_perfil
        self.nome_perfil = nome_perfil
        self.ativo = ativo
        self.tentativas_falhadas = tentativas_falhadas

    @property
    def bloqueado(self):
        """A conta fica bloqueada depois de 5 tentativas de login falhadas seguidas (RF02)."""
        return self.tentativas_falhadas >= MAXIMO_TENTATIVAS

    @property
    def estado(self):
        """Texto para a listagem: Ativo, Bloqueado ou Desativado."""
        if not self.ativo:
            return "Desativado"
        if self.bloqueado:
            return "Bloqueado"
        return "Ativo"

    @property
    def e_administrador(self):
        return self.nome_perfil == PERFIL_ADMINISTRADOR

    def __str__(self):
        return f"{self.nome} ({self.nome_perfil})"
