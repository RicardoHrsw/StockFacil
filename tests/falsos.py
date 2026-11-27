class RegistoFalso:
    """Faz de conta que é o registo de ações: guarda as ações numa lista, sem base de dados."""

    def __init__(self):
        self.acoes = []

    def registar(self, acao, detalhe=None, utilizador=None):
        self.acoes.append(acao)
