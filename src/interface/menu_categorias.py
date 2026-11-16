from src.ligacao import ErroLigacao
from src.servicos.categoria_servico import CategoriaServico

class MenuCategorias:
    """Menu de consola para gerir categorias."""

    def __init__(self):
        self.servico = CategoriaServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Categorias ===")
            print("1 - Registar categoria")
            print("2 - Listar categorias")
            print("3 - Editar categoria")
            print("4 - Apagar categoria")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    self.registar()
                elif opcao == "2":
                    self.listar()
                elif opcao == "3":
                    self.editar()
                elif opcao == "4":
                    self.apagar()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida. Escolha 1, 2, 3, 4 ou 0.")
            except ErroLigacao as erro:
                print("Erro:", erro)

    def registar(self):
        """Pede os dados ao utilizador e regista a categoria."""
        nome = input("Nome: ")
        descricao = input("Descrição (opcional, Enter para deixar vazio): ")
        try:
            categoria = self.servico.criar(nome, descricao)
            print(f"Categoria '{categoria.nome}' registada com o número {categoria.id_categoria}.")
        except ValueError as erro:
            print("Erro:", erro)

    def editar(self):
        """Mostra a lista, pede o número da categoria e os dados novos."""
        if not self.listar():
            return
        try:
            categoria = self.servico.obter(input("Número da categoria a editar: "))
            print("Enter mantém o valor atual.")
            nome = input(f"Nome [{categoria.nome}]: ").strip() or categoria.nome
            descricao_atual = categoria.descricao or ""
            descricao = input(f"Descrição [{descricao_atual or '-'}] (escreva - para apagar): ").strip()
            if descricao == "":
                descricao = descricao_atual
            elif descricao == "-":
                descricao = ""
            categoria = self.servico.editar(categoria.id_categoria, nome, descricao)
            print(f"Categoria {categoria.id_categoria} atualizada: {categoria.nome}.")
        except ValueError as erro:
            print("Erro:", erro)

    def apagar(self):
        """Mostra a lista, pede o número da categoria e confirma antes de apagar."""
        if not self.listar():
            return
        try:
            categoria = self.servico.obter(input("Número da categoria a apagar: "))
            resposta = input(f"Tem a certeza que quer apagar '{categoria.nome}'? (s/n): ").strip().lower()
            if resposta != "s":
                print("Nada foi apagado.")
                return
            self.servico.apagar(categoria.id_categoria)
            print(f"Categoria '{categoria.nome}' apagada.")
        except ValueError as erro:
            print("Erro:", erro)

    def listar(self):
        """Mostra todas as categorias numa tabela. Devolve False se não houver nenhuma."""
        categorias = self.servico.listar()

        if not categorias:
            print("Ainda não existem categorias registadas.")
            return False

        largura_nome = max(len("Nome"), max(len(categoria.nome) for categoria in categorias))

        print()
        print("ID".rjust(4), "|", "Nome".ljust(largura_nome), "|", "Descrição")
        print("-" * (largura_nome + 30))
        for categoria in categorias:
            descricao = categoria.descricao or "-"
            print(str(categoria.id_categoria).rjust(4), "|", categoria.nome.ljust(largura_nome), "|", descricao)
        print()
        print(f"Total: {len(categorias)} categoria(s)")
        return True
