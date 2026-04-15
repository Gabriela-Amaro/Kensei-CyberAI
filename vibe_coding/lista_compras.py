def mostrar_menu() -> None:
    print("\n=== Lista de Compras ===")
    print("1. Adicionar item")
    print("2. Ver itens")
    print("3. Remover item")
    print("4. Sair")


def adicionar_item(itens: list[str]) -> None:
    item = input("Digite o nome do item para adicionar: ").strip()

    if not item:
        print("Item vazio nao pode ser adicionado.")
        return

    itens.append(item)
    print(f"Item '{item}' adicionado com sucesso.")


def ver_itens(itens: list[str]) -> None:
    if not itens:
        print("A lista de compras esta vazia.")
        return

    print("\nItens na lista:")
    for indice, item in enumerate(itens, start=1):
        print(f"{indice}. {item}")


def remover_item(itens: list[str]) -> None:
    if not itens:
        print("Nao ha itens para remover.")
        return

    ver_itens(itens)
    entrada = input("Digite o numero do item para remover: ").strip()

    if not entrada.isdigit():
        print("Entrada invalida. Digite um numero.")
        return

    indice = int(entrada)
    if indice < 1 or indice > len(itens):
        print("Numero fora do intervalo da lista.")
        return

    removido = itens.pop(indice - 1)
    print(f"Item '{removido}' removido com sucesso.")


def salvar_itens_em_arquivo(itens: list[str], caminho_arquivo: str = "lista_compras.txt") -> None:
    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            for item in itens:
                arquivo.write(f"{item}\n")
        print(f"Lista salva em '{caminho_arquivo}'.")
    except OSError as erro:
        print(f"Nao foi possivel salvar a lista: {erro}")


def main() -> None:
    itens: list[str] = []

    while True:
        mostrar_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            adicionar_item(itens)
        elif opcao == "2":
            ver_itens(itens)
        elif opcao == "3":
            remover_item(itens)
        elif opcao == "4":
            salvar_itens_em_arquivo(itens)
            print("Saindo do programa. Ate logo!")
            break
        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    main()
