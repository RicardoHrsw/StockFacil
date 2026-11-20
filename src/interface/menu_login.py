import sys
from getpass import getpass

from src.interface.menu_principal import MenuPrincipal
from src.ligacao import ErroLigacao
from src.servicos.autenticacao_servico import AutenticacaoServico


def pedir_password(rotulo):
    """Pede a palavra-passe sem a mostrar no ecrã. Fora de um terminal (ex: testes) usa input."""
    if sys.stdin.isatty():
        return getpass(rotulo)
    return input(rotulo)


class MenuLogin:
    """Primeiro ecrã do programa: só entra quem tiver username e palavra-passe certos."""

    def __init__(self):
        self.servico = AutenticacaoServico()

    def mostrar(self):
        """Pede o login até o utilizador escolher sair. Depois do logout volta aqui."""
        while True:
            print()
            print("=== StockFácil — Iniciar sessão ===")
            username = input("Username (Enter para sair): ").strip()
            if username == "":
                print("Até breve!")
                break
            password = pedir_password("Palavra-passe: ")

            try:
                utilizador = self.servico.iniciar_sessao(username, password)
            except (ValueError, ErroLigacao) as erro:
                print("Erro:", erro)
                continue

            print(f"Bem-vindo, {utilizador.nome}!")
            MenuPrincipal(utilizador).mostrar()
            print("Sessão terminada.")
