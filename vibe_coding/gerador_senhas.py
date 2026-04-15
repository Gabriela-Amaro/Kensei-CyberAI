from datetime import datetime
import random
import string


def ler_sim_nao(pergunta: str) -> bool:
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Resposta invalida. Digite 's' para sim ou 'n' para nao.")


def gerar_senha(tamanho: int, usar_maiusculas: bool, usar_numeros: bool, usar_simbolos: bool) -> str:
    caracteres = string.ascii_lowercase

    if usar_maiusculas:
        caracteres += string.ascii_uppercase
    if usar_numeros:
        caracteres += string.digits
    if usar_simbolos:
        caracteres += string.punctuation

    return "".join(random.choice(caracteres) for _ in range(tamanho))


def salvar_senhas_em_arquivo(senhas: list[str], caminho_arquivo: str = "senhas.txt") -> None:
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(f"Data de geracao: {data_hora}\n")
        arquivo.write("Senhas geradas:\n")
        for indice, senha in enumerate(senhas, start=1):
            arquivo.write(f"{indice}. {senha}\n")


def main() -> None:
    print("=== Gerador de Senhas ===")

    while True:
        entrada_tamanho = input("Digite o tamanho da senha: ").strip()
        if entrada_tamanho.isdigit() and int(entrada_tamanho) > 0:
            tamanho = int(entrada_tamanho)
            break
        print("Tamanho invalido. Digite um numero inteiro maior que zero.")

    usar_maiusculas = ler_sim_nao("Incluir letras maiusculas? (s/n): ")
    usar_numeros = ler_sim_nao("Incluir numeros? (s/n): ")
    usar_simbolos = ler_sim_nao("Incluir simbolos? (s/n): ")

    senhas = [
        gerar_senha(tamanho, usar_maiusculas, usar_numeros, usar_simbolos)
        for _ in range(5)
    ]

    print("\n5 senhas geradas:")
    for indice, senha in enumerate(senhas, start=1):
        print(f"{indice}. {senha}")

    salvar_senhas_em_arquivo(senhas)
    print("\nSenhas salvas em 'senhas.txt'.")


if __name__ == "__main__":
    main()
