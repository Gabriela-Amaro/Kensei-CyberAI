# Primeira Semana - Vibe Coding

Nesta primeira semana, foram desenvolvidos pequenos programas em Python para praticar vibe coding.

## Resumo do que foi feito

- Conversor de temperatura entre Celsius e Fahrenheit.
- Lista de compras com adicionar, listar, remover e salvar em arquivo.
- Gerador de senhas com salvamento de 5 senhas em `.txt`.
- Quiz de segurança cibernética com pontuação, validação e tempo por pergunta.
- Organizador de arquivos por categoria com log de movimentações.
- Scanner de portas básico com relatório salvo em `.txt`.
- Contador de palavras lendo texto de arquivo e exibindo frequência das palavras.

## Detalhamento dos códigos

### 1. Conversor de temperatura

Arquivo: `celsius_para_fahrenheit.py`

- Faz conversão nos dois sentidos:
  - Celsius para Fahrenheit
  - Fahrenheit para Celsius
- Permite escolher a opção no menu.
- O programa roda em loop até o usuário sair.

### 2. Lista de compras

Arquivo: `lista_compras.py`

- Permite adicionar itens.
- Mostra a lista de itens.
- Remove itens pelo número.
- Ao sair, salva a lista em `lista_compras.txt`.

### 3. Gerador de senhas

Arquivo: `gerador_senhas.py`

- Gera 5 senhas de uma vez.
- Permite escolher se a senha terá maiúsculas, números e símbolos.
- Salva o resultado em `senhas.txt` com data e hora.

### 4. Quiz Cyber

Arquivo: `quiz_cyber.py`

- Traz 5 perguntas de segurança cibernética.
- Valida respostas com `a`, `b` ou `c`.
- Cada pergunta tem limite de 10 segundos.
- Se o tempo acabar, a resposta conta como erro.

### 5. Organizador de arquivos

Arquivo: `organizar_arquivos.py`

- Organiza arquivos por tipo:
  - imagens
  - documentos
  - vídeos
- Cria pastas automaticamente quando necessário.
- Evita sobrescrever arquivos com nomes iguais.
- Mostra log com total geral e por categoria.

### 6. Scanner de portas básico

Arquivo: `scanner_portas_basico.py`

- Faz varredura TCP em um host informado.
- Permite escolher portas comuns ou intervalo personalizado.
- Mostra portas abertas no terminal.
- Salva relatório em `resultado_scan.txt`.
- O histórico novo entra no topo do arquivo.

### 7. Contador de palavras

Arquivo: `contador_palavras.py`

- Lê um arquivo `.txt` informado pelo usuário.
- Conta palavras e caracteres.
- Mostra o top 10 palavras mais frequentes.
- Trata erro se o arquivo não existir ou estiver vazio.
