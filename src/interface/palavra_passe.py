import sys
from getpass import getpass

from src.ligacao import ErroLigacao


def pedir_password(rotulo):
    """Pede a palavra-passe sem a mostrar no ecrã. Fora de um terminal (ex: testes) usa input."""
    if sys.stdin.isatty():
        return getpass(rotulo)
    return input(rotulo)


def alterar_password(servico, utilizador, atual=None):
    """Pede a palavra-passe atual (se ainda não a souber) e a nova, duas vezes.
    Devolve True se a palavra-passe foi mudada."""
    if atual is None:
        atual = pedir_password("Palavra-passe atual: ")
    nova = pedir_password("Nova palavra-passe (mínimo 6 caracteres): ")
    confirmacao = pedir_password("Repita a nova palavra-passe: ")
    try:
        servico.alterar_password(utilizador, atual, nova, confirmacao)
    except (ValueError, ErroLigacao) as erro:
        print("Erro:", erro)
        return False
    print("Palavra-passe alterada.")
    return True
