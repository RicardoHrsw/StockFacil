from src.ligacao import ErroLigacao
from src.servicos.categoria_servico import CategoriaServico
from src.servicos.produto_servico import ProdutoServico


def formatar_preco(preco):
    """Mostra o preço à portuguesa, ex: 1,20 €."""
    return f"{preco:.2f} €".replace(".", ",")


class MenuProdutos:
    """Menu de consola para gerir produtos."""

    def __init__(self):
        self.servico = ProdutoServico()
        self.categorias = CategoriaServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Produtos ===")
            print("1 - Registar produto")
            print("2 - Listar produtos")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    self.registar()
                elif opcao == "2":
                    self.listar()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida. Escolha 1, 2 ou 0.")
            except ErroLigacao as erro:
                print("Erro:", erro)

    def registar(self):
        """Pede os dados ao utilizador e regista o produto numa categoria que já existe."""
        categorias = self.categorias.listar()
        if not categorias:
            print("Ainda não existem categorias. Registe primeiro uma categoria.")
            return

        codigo = input("Código: ")
        nome = input("Nome: ")
        descricao = input("Descrição (opcional, Enter para deixar vazio): ")
        preco = input("Preço de venda (ex: 1,20): ")
        stock_minimo = input("Stock mínimo (Enter para 0): ")

        print()
        print("Categorias:")
        for categoria in categorias:
            print(str(categoria.id_categoria).rjust(4), "-", categoria.nome)
        id_categoria = input("Número da categoria: ")

        try:
            produto = self.servico.criar(codigo, nome, preco, id_categoria, descricao, stock_minimo)
            print(f"Produto '{produto.nome}' registado com o código {produto.codigo}.")
        except ValueError as erro:
            print("Erro:", erro)

    def listar(self):
        """Mostra os produtos ativos numa tabela."""
        produtos = self.servico.listar()

        if not produtos:
            print("Ainda não existem produtos registados.")
            return

        largura_codigo = max(len("Código"), max(len(p.codigo) for p in produtos))
        largura_nome = max(len("Nome"), max(len(p.nome) for p in produtos))
        largura_categoria = max(len("Categoria"), max(len(p.nome_categoria) for p in produtos))

        print()
        print("Código".ljust(largura_codigo), "|", "Nome".ljust(largura_nome), "|",
              "Categoria".ljust(largura_categoria), "|", "Preço".rjust(10), "|", "Stock", "|", "Mínimo")
        print("-" * (largura_codigo + largura_nome + largura_categoria + 40))
        for p in produtos:
            print(p.codigo.ljust(largura_codigo), "|", p.nome.ljust(largura_nome), "|",
                  p.nome_categoria.ljust(largura_categoria), "|", formatar_preco(p.preco_venda).rjust(10), "|",
                  str(p.stock_atual).rjust(5), "|", str(p.stock_minimo).rjust(6))
        print()
        print(f"Total: {len(produtos)} produto(s)")
