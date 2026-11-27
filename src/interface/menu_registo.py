from src.servicos.registo_servico import RegistoServico


def mostrar_registo():
    """Mostra as últimas ações registadas: quem fez o quê e quando (RF18)."""
    registos = RegistoServico().listar()
    if not registos:
        print("Ainda não há ações registadas.")
        return

    largura_username = max(len("Utilizador"), max(len(r.username or "-") for r in registos))
    largura_acao = max(len("Ação"), max(len(r.acao) for r in registos))

    print()
    print("Data e hora".ljust(19), "|", "Utilizador".ljust(largura_username), "|", "Ação".ljust(largura_acao), "|",
          "Detalhe")
    print("-" * (largura_username + largura_acao + 50))
    for r in registos:
        print(r.data_hora.strftime("%d/%m/%Y %H:%M:%S"), "|", (r.username or "-").ljust(largura_username), "|",
              r.acao.ljust(largura_acao), "|", r.detalhe or "")
    print()
    print(f"Últimas {len(registos)} ações")
