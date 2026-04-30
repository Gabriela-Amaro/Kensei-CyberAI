"""
Script interativo para fazer perguntas ao Gemini (Google AI).
A chave da API é lida do arquivo .env na raiz do projeto.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path


# ─── Carregar a chave da API do .env ─────────────────────────────────────────
def carregar_api_key():
    """Lê a variável gemini_api_key do arquivo .env."""
    env_path = Path(__file__).resolve().parent.parent / ".env"

    if not env_path.exists():
        print(f"❌ Arquivo .env não encontrado em: {env_path}")
        sys.exit(1)

    with open(env_path) as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("gemini_api_key="):
                return linha.split("=", 1)[1].strip()

    print("❌ Variável 'gemini_api_key' não encontrada no .env")
    sys.exit(1)


# ─── Enviar pergunta para a API do Gemini ────────────────────────────────────
def perguntar_ao_gemini(pergunta: str, api_key: str) -> str:
    """Envia uma pergunta para a API do Gemini e retorna a resposta."""
    modelo = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json",
    }

    payload = json.dumps({
        "contents": [
            {
                "parts": [{"text": pergunta}]
            }
        ],
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            dados = json.loads(resp.read().decode("utf-8"))
            return dados["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        corpo = e.read().decode("utf-8", errors="replace")
        print(f"\n❌ Erro na API (HTTP {e.code}): {corpo}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\n❌ Erro de conexão: {e.reason}")
        sys.exit(1)


# ─── Loop principal ──────────────────────────────────────────────────────────
def main():
    api_key = carregar_api_key()

    print("╔══════════════════════════════════════════════════╗")
    print("║       🤖  Assistente Gemini — Kensei AI         ║")
    print("║  Digite sua pergunta e pressione Enter.         ║")
    print("║  Digite 'sair' para encerrar.                   ║")
    print("╚══════════════════════════════════════════════════╝\n")

    while True:
        try:
            pergunta = input("🔹 Sua pergunta: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Até mais!")
            break

        if not pergunta:
            continue
        if pergunta.lower() in ("sair", "exit", "quit"):
            print("\n👋 Até mais!")
            break

        print("\n⏳ Consultando o Gemini...\n")
        resposta = perguntar_ao_gemini(pergunta, api_key)

        print("━" * 50)
        print(f"🤖 Gemini:\n\n{resposta}")
        print("━" * 50)
        print()


if __name__ == "__main__":
    main()
