from src import sessao
from src.modelos.registo_acao import RegistoAcao
from src.repositorios.registo_repositorio import RegistoRepositorio

TAMANHO_MAXIMO_ACAO = 50
TAMANHO_MAXIMO_DETALHE = 255


class RegistoServico:
    """Regista automaticamente as ações importantes, com o utilizador e a data e hora (RF18)."""

    def __init__(self):
        self.repositorio = RegistoRepositorio()

    def registar(self, acao, detalhe=None, utilizador=None):
        """Guarda a ação. Sem utilizador indicado, usa quem tem a sessão iniciada."""
        utilizador = utilizador or sessao.utilizador_atual()
        id_utilizador = utilizador.id_utilizador if utilizador else None
        if detalhe is not None:
            detalhe = str(detalhe)[:TAMANHO_MAXIMO_DETALHE]
        self.repositorio.registar(RegistoAcao(acao[:TAMANHO_MAXIMO_ACAO], detalhe, id_utilizador))

    def listar(self):
        """Devolve as últimas ações registadas."""
        return self.repositorio.listar()
