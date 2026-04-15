import signal


def input_com_timeout(prompt: str, timeout_segundos: int) -> str | None:
    def _timeout_handler(signum: int, frame: object) -> None:
        raise TimeoutError

    handler_anterior = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(timeout_segundos)

    try:
        return input(prompt).strip().lower()
    except TimeoutError:
        return None
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, handler_anterior)


def executar_quiz() -> None:
    perguntas = [
        {
            "pergunta": "1) O que significa phishing?",
            "opcoes": {
                "a": "Ataque que tenta enganar para roubar dados",
                "b": "Ferramenta de backup automatico",
                "c": "Metodo de compressao de arquivos",
            },
            "correta": "a",
        },
        {
            "pergunta": "2) Qual senha e mais segura?",
            "opcoes": {
                "a": "123456",
                "b": "senha123",
                "c": "R!9x#2Lp@7Qm",
            },
            "correta": "c",
        },
        {
            "pergunta": "3) Para que serve autenticacao de dois fatores (2FA)?",
            "opcoes": {
                "a": "Aumentar seguranca exigindo segunda verificacao",
                "b": "Dobrar a velocidade da internet",
                "c": "Criptografar arquivos automaticamente",
            },
            "correta": "a",
        },
        {
            "pergunta": "4) O que um firewall faz?",
            "opcoes": {
                "a": "Limpa poeira do computador",
                "b": "Filtra e controla trafego de rede",
                "c": "Aumenta o brilho da tela",
            },
            "correta": "b",
        },
        {
            "pergunta": "5) Qual pratica ajuda a prevenir malware?",
            "opcoes": {
                "a": "Abrir anexos desconhecidos",
                "b": "Atualizar sistema e aplicativos",
                "c": "Desativar antivirus",
            },
            "correta": "b",
        },
    ]

    acertos = 0
    tempo_limite = 10

    print("=== Quiz Cyber (5 perguntas) ===")
    print(f"Responda com: a, b ou c. Voce tem {tempo_limite} segundos por pergunta.\n")

    for item in perguntas:
        print(item["pergunta"])
        for letra, texto in item["opcoes"].items():
            print(f"  {letra}) {texto}")

        resposta = input_com_timeout("Sua resposta: ", tempo_limite)

        if resposta is None:
            print("Tempo esgotado! Conta como erro.\n")
            continue

        if resposta not in ("a", "b", "c"):
            print("Opcao invalida. Conta como erro.\n")
            continue

        if resposta == item["correta"]:
            acertos += 1
            print("Correto!\n")
        else:
            print(f"Errado! Resposta correta: {item['correta']}\n")

    print("=== Resultado Final ===")
    print(f"Pontuacao: {acertos}/5")

    if acertos >= 3:
        print("Voce passou!")
    else:
        print("Voce nao passou.")


if __name__ == "__main__":
    executar_quiz()
