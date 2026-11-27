"""Guarda quem tem a sessão iniciada, para o registo de ações saber quem fez cada coisa."""

_utilizador_atual = None


def iniciar(utilizador):
    global _utilizador_atual
    _utilizador_atual = utilizador


def terminar():
    global _utilizador_atual
    _utilizador_atual = None


def utilizador_atual():
    return _utilizador_atual
