class RegistoAcao:
    """Uma linha do registo de ações: quem fez o quê e quando (RF18)."""

    def __init__(self, acao, detalhe=None, id_utilizador=None, id_registo=None, data_hora=None, username=None):
        self.id_registo = id_registo
        self.data_hora = data_hora
        self.id_utilizador = id_utilizador
        self.acao = acao
        self.detalhe = detalhe
        self.username = username
