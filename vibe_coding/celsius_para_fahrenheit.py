def celsius_para_fahrenheit(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def fahrenheit_para_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def main() -> None:
    while True:
        print("\nEscolha a conversao:")
        print("1 - Celsius para Fahrenheit")
        print("2 - Fahrenheit para Celsius")
        print("0 - Sair")
        opcao = input("Opcao (0, 1 ou 2): ").strip()

        if opcao == "0":
            print("Programa encerrado.")
            break

        if opcao not in {"1", "2"}:
            print("Opcao invalida. Escolha 0, 1 ou 2.")
            continue

        if opcao == "1":
            entrada = input("Digite a temperatura em Celsius: ").strip().replace(",", ".")
        else:
            entrada = input("Digite a temperatura em Fahrenheit: ").strip().replace(",", ".")

        try:
            temperatura = float(entrada)
        except ValueError:
            print("Valor invalido. Digite um numero.")
            continue

        if opcao == "1":
            fahrenheit = celsius_para_fahrenheit(temperatura)
            print(f"{temperatura:.2f} C equivale a {fahrenheit:.2f} F")
        else:
            celsius = fahrenheit_para_celsius(temperatura)
            print(f"{temperatura:.2f} F equivale a {celsius:.2f} C")


if __name__ == "__main__":
    main()
