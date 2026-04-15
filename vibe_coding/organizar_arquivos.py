import os
import shutil


EXTENSOES_IMAGENS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}
EXTENSOES_DOCS = {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"}
EXTENSOES_VIDEOS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"}


def obter_pasta_destino(extensao: str) -> str | None:
    if extensao in EXTENSOES_IMAGENS:
        return "imagens"
    if extensao in EXTENSOES_DOCS:
        return "docs"
    if extensao in EXTENSOES_VIDEOS:
        return "videos"
    return None


def caminho_unico(caminho: str) -> str:
    if not os.path.exists(caminho):
        return caminho

    base, ext = os.path.splitext(caminho)
    contador = 1
    while True:
        novo_caminho = f"{base}_{contador}{ext}"
        if not os.path.exists(novo_caminho):
            return novo_caminho
        contador += 1


def organizar_arquivos(diretorio: str) -> None:
    if not os.path.isdir(diretorio):
        print("Diretorio invalido.")
        return

    script_atual = os.path.basename(__file__)
    movidos = 0
    pastas_criadas: set[str] = set()
    movidos_por_categoria: dict[str, int] = {
        "imagens": 0,
        "docs": 0,
        "videos": 0,
    }

    for nome in os.listdir(diretorio):
        caminho_origem = os.path.join(diretorio, nome)

        if not os.path.isfile(caminho_origem):
            continue

        # Evita mover o proprio script enquanto ele roda.
        if nome == script_atual:
            continue

        _, extensao = os.path.splitext(nome)
        pasta_destino = obter_pasta_destino(extensao.lower())

        if not pasta_destino:
            continue

        caminho_pasta_destino = os.path.join(diretorio, pasta_destino)
        if pasta_destino not in pastas_criadas and not os.path.exists(caminho_pasta_destino):
            os.makedirs(caminho_pasta_destino, exist_ok=True)
            pastas_criadas.add(pasta_destino)

        caminho_destino = os.path.join(caminho_pasta_destino, nome)
        caminho_destino = caminho_unico(caminho_destino)

        shutil.move(caminho_origem, caminho_destino)
        movidos += 1
        movidos_por_categoria[pasta_destino] += 1
        print(f"Movido: {nome} -> {pasta_destino}/")

    print(f"\nTotal de arquivos movidos: {movidos}")
    print("Movidos por categoria:")
    print(f"- imagens: {movidos_por_categoria['imagens']}")
    print(f"- docs: {movidos_por_categoria['docs']}")
    print(f"- videos: {movidos_por_categoria['videos']}")


def main() -> None:
    entrada = input("Digite o caminho da pasta para organizar (vazio = pasta atual): ").strip()
    diretorio = entrada if entrada else os.getcwd()
    organizar_arquivos(diretorio)


if __name__ == "__main__":
    main()
