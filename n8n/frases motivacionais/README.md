# Frases motivacionais

Workflow: `frase-motivacional-gemini-google-sheets.json`

## O que faz

Ao executar o `Manual Trigger`, o workflow:

1. chama a API do Gemini 2.5 Flash;
2. gera uma frase motivacional curta em portugues;
3. cria uma linha com `data` e `frase`;
4. adiciona a linha em uma planilha do Google Sheets.

## Criar a API key do Gemini

1. Acesse `https://aistudio.google.com/app/apikey`.
2. Clique em `Create API key`.
3. Copie a chave gerada.

## Configurar a credencial do Gemini no n8n

1. No n8n, abra `Credentials`.
2. Clique em `Create Credential`.
3. Procure por `Header Auth`.
4. Crie uma credencial com estes campos:

```text
Name: Gemini API Key
Header Name: x-goog-api-key
Header Value: sua_api_key_do_gemini
```

5. Salve a credencial.
6. Importe o workflow `frase-motivacional-gemini-google-sheets.json`.
7. Abra o node `Gerar frase com Gemini`.
8. Em `Credential for Header Auth`, selecione `Gemini API Key`.

O node `Gerar frase com Gemini` usa:

```text
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
```

## Preparar a planilha

1. Crie uma planilha no Google Sheets.
2. Na primeira linha da aba, crie estes cabecalhos:

```text
data | frase
```

3. Copie o ID da planilha pela URL:

```text
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```

4. Confirme o nome da aba. O workflow usa `Sheet1` por padrao.

## Conectar o Google Sheets no n8n

1. No n8n, importe `frase-motivacional-gemini-google-sheets.json` em `Workflows > Import from File`.
2. Abra o node `Salvar no Google Sheets`.
3. Em `Credential`, clique para criar uma nova credencial do Google Sheets OAuth2.
4. No Google Cloud Console, crie ou selecione um projeto.
5. Ative a API `Google Sheets API` no projeto.
6. Configure a tela de consentimento OAuth.
7. Crie um OAuth Client ID do tipo `Web application`.
8. Em `Authorized redirect URIs`, use a URL de callback mostrada pelo proprio n8n na credencial. Rodando localmente, normalmente fica assim:

```text
http://localhost:5678/rest/oauth2-credential/callback
```

9. Copie o `Client ID` e o `Client Secret` para a credencial do n8n.
10. Clique em `Sign in with Google` e autorize acesso a planilha.
11. No node `Salvar no Google Sheets`, troque `COLE_AQUI_O_SPREADSHEET_ID` pelo ID da sua planilha.
12. Ajuste `Sheet1` se sua aba tiver outro nome.

## Testar

1. Clique em `Execute workflow`.
2. Clique no `Manual Trigger`.
3. Confira se uma nova linha apareceu na planilha com `data` e `frase`.

Se o node do Gemini falhar com credencial ausente, abra `Gerar frase com Gemini` e selecione a credencial `Gemini API Key`.
