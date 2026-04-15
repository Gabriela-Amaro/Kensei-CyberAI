from datetime import datetime
import os
import socket
import time


PORTAS_COMUNS: dict[int, str] = {
    20: "FTP Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP Alt",
}


def ler_sim_nao(pergunta: str) -> bool:
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Resposta invalida. Digite 's' para sim ou 'n' para nao.")


def ler_timeout() -> float:
    while True:
        entrada = input("Timeout por porta em segundos (padrao 0.3): ").strip().replace(",", ".")
        if not entrada:
            return 0.3

        try:
            timeout = float(entrada)
        except ValueError:
            print("Valor invalido. Digite um numero, por exemplo 0.3")
            continue

        if timeout <= 0:
            print("O timeout precisa ser maior que zero.")
            continue

        return timeout


def escolher_portas() -> list[int]:
    while True:
        print("\nEscolha o tipo de varredura:")
        print("1. Portas comuns")
        print("2. Intervalo personalizado")
        escolha = input("Opcao (1 ou 2): ").strip()

        if escolha == "1":
            return sorted(PORTAS_COMUNS.keys())

        if escolha == "2":
            inicio = ler_porta("Porta inicial: ")
            fim = ler_porta("Porta final: ")

            if inicio > fim:
                print("Intervalo invalido: a porta inicial nao pode ser maior que a final.")
                continue

            return list(range(inicio, fim + 1))

        print("Opcao invalida. Escolha 1 ou 2.")


def ler_porta(pergunta: str) -> int:
    while True:
        entrada = input(pergunta).strip()

        if not entrada.isdigit():
            print("Digite apenas numeros inteiros.")
            continue

        porta = int(entrada)
        if porta < 1 or porta > 65535:
            print("Porta fora do intervalo valido (1-65535).")
            continue

        return porta


def obter_nome_servico(porta: int) -> str:
    if porta in PORTAS_COMUNS:
        return PORTAS_COMUNS[porta]

    try:
        return socket.getservbyport(porta)
    except OSError:
        return "desconhecido"


def porta_aberta(host: str, porta: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, porta), timeout=timeout):
            return True
    except (ConnectionRefusedError, TimeoutError, OSError):
        return False


def descrever_intervalo(portas: list[int]) -> str:
    if not portas:
        return "nenhum"
    return f"{min(portas)}-{max(portas)}"


def salvar_resultado(
    host: str,
    portas_testadas: list[int],
    portas_abertas: list[int],
    duracao: float,
    caminho_arquivo: str = "resultado_scan.txt",
) -> None:
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    intervalo = descrever_intervalo(portas_testadas)

    linhas_resultado: list[str] = [
        "=== Resultado do Scanner de Portas ===",
        f"Data: {data_hora}",
        f"Host: {host}",
        f"Intervalo escaneado: {intervalo}",
        f"Total de portas testadas: {len(portas_testadas)}",
        f"Tempo total: {duracao:.2f}s",
        f"Quantidade de portas abertas: {len(portas_abertas)}",
        "",
    ]

    if portas_abertas:
        linhas_resultado.append("Portas abertas:")
        for porta in portas_abertas:
            servico = obter_nome_servico(porta)
            linhas_resultado.append(f"- {porta} ({servico})")
    else:
        linhas_resultado.append("Nenhuma porta aberta foi encontrada.")

    novo_resultado = "\n".join(linhas_resultado)
    conteudo_antigo = ""

    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo_existente:
            conteudo_antigo = arquivo_existente.read().strip()

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        if conteudo_antigo:
            arquivo.write(f"{novo_resultado}\n\n{conteudo_antigo}\n")
        else:
            arquivo.write(f"{novo_resultado}\n")


def executar_scan(host: str, portas: list[int], timeout: float) -> tuple[list[int], float]:
    abertas: list[int] = []
    inicio = time.time()

    print("\nIniciando varredura...")
    for porta in portas:
        if porta_aberta(host, porta, timeout):
            abertas.append(porta)
            print(f"[ABERTA] {porta} ({obter_nome_servico(porta)})")

    duracao = time.time() - inicio
    return abertas, duracao


def main() -> None:
    print("=== Scanner de Portas Basico ===")
    print("Use somente em maquinas e redes com autorizacao.")

    host = input("Host alvo (ex: 127.0.0.1): ").strip()
    if not host:
        print("Host invalido.")
        return

    portas = escolher_portas()
    timeout = ler_timeout()

    portas_abertas, duracao = executar_scan(host, portas, timeout)

    print("\n=== Resultado Final ===")
    print(f"Host: {host}")
    print(f"Intervalo escaneado: {descrever_intervalo(portas)}")
    print(f"Total de portas testadas: {len(portas)}")
    print(f"Total de portas abertas: {len(portas_abertas)}")
    print(f"Tempo total: {duracao:.2f}s")

    if portas_abertas:
        print("Lista de portas abertas:")
        for porta in portas_abertas:
            print(f"- {porta} ({obter_nome_servico(porta)})")

    if ler_sim_nao("\nSalvar resultado em arquivo .txt? (s/n): "):
        try:
            salvar_resultado(host, portas, portas_abertas, duracao)
            print("Resultado salvo em 'resultado_scan.txt'.")
        except OSError as erro:
            print(f"Nao foi possivel salvar o arquivo: {erro}")


if __name__ == "__main__":
    main()
