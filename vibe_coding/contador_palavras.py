from collections import Counter
import re


def ler_texto_arquivo(caminho_arquivo: str) -> str:
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        return arquivo.read()


def ler_caminho_arquivo() -> str:
    print("=== Contador de Palavras ===")
    print("Informe o caminho de um arquivo de texto (.txt).")
    return input("Caminho do arquivo: ").strip()


def extrair_palavras(texto: str) -> list[str]:
    # Separa palavras ignorando pontuacao e diferencas de maiusculo/minusculo.
    return re.findall(r"\b[\w']+\b", texto.lower(), flags=re.UNICODE)


def mostrar_resultado(texto: str) -> None:
    palavras = extrair_palavras(texto)
    frequencias = Counter(palavras)

    total_palavras = len(palavras)
    total_caracteres = len(texto)

    print("\n=== Resultado ===")
    print(f"Total de palavras: {total_palavras}")
    print(f"Total de caracteres: {total_caracteres}")

    print("\nTop 10 palavras mais frequentes:")
    if not frequencias:
        print("Nenhuma palavra encontrada.")
        return

    for indice, (palavra, quantidade) in enumerate(frequencias.most_common(10), start=1):
        print(f"{indice}. {palavra} - {quantidade}")


def main() -> None:
    caminho_arquivo = ler_caminho_arquivo()

    if not caminho_arquivo:
        print("Nenhum caminho informado.")
        return

    try:
        texto = ler_texto_arquivo(caminho_arquivo)
    except FileNotFoundError:
        print("Arquivo nao encontrado.")
        return
    except OSError as erro:
        print(f"Nao foi possivel ler o arquivo: {erro}")
        return

    if not texto.strip():
        print("O arquivo esta vazio.")
        return

    mostrar_resultado(texto)


if __name__ == "__main__":
    main()
