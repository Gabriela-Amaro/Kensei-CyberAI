# n8n

Esta pasta guarda workflows e automacoes criadas para o n8n.

## Rodar localmente

Recomendado para nao perder workflows e credenciais ao fechar o container:

```bash
docker volume create n8n_data

docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

Se quiser rodar de forma temporaria, sem persistir dados:

```bash
docker run -it --rm \
  -p 5678:5678 \
  n8nio/n8n
```

Depois acesse:

```text
http://localhost:5678
```

## Workflows

- [Frases motivacionais](frases%20motivacionais/README.md)
- [Monitoramento de site](monitoramento%20site/README.md)
