# Monitoramento de site com alerta por email

Workflow: `monitoramento-site-email.json`

## O que faz

O workflow:

1. roda automaticamente a cada 5 minutos;
2. checa se `https://cajui.ifnmg.edu.br` responde com status HTTP de sucesso;
3. nao faz nada se o site estiver no ar;
4. envia um email se o site estiver fora do ar, com erro, horario e status HTTP.

## Importar o workflow

1. Abra o n8n em `http://localhost:5678`.
2. Va em `Workflows`.
3. Clique em `Import from File`.
4. Selecione `monitoramento-site-email.json`.

## Alterar o site monitorado

1. Abra o node `Verificar se o site esta no ar`.
2. No codigo, altere esta linha:

```js
const siteUrl = 'https://cajui.ifnmg.edu.br';
```

3. Use sempre a URL completa, com `https://` ou `http://`.
4. Salve o node.

## Configurar o envio de email

O workflow usa o node `Send Email`, que precisa de uma credencial SMTP.

1. No n8n, abra `Credentials`.
2. Clique em `Create Credential`.
3. Procure por `SMTP`.
4. Preencha os dados do seu provedor de email.
5. Salve a credencial.
6. Abra o workflow importado.
7. Abra o node `Enviar email de alerta`.
8. Em `Credential`, selecione a credencial SMTP criada.
9. Troque os campos:

```text
From Email: seu email remetente
To Email: seu email de destino
```

## Exemplo com Gmail

Para Gmail, normalmente voce precisa usar senha de app, nao a senha normal da conta.

1. Ative a verificacao em duas etapas na conta Google.
2. Crie uma senha de app em `https://myaccount.google.com/apppasswords`.
3. No n8n, configure a credencial SMTP assim:

```text
Host: smtp.gmail.com
Port: 465
SSL/TLS: true
User: seu_email@gmail.com
Password: senha_de_app_do_google
```

4. No node `Enviar email de alerta`, use o mesmo email no campo `From Email`.

## Testar

1. Abra o node `Verificar se o site esta no ar`.
2. Troque temporariamente a URL para um dominio invalido, por exemplo:

```js
const siteUrl = 'https://site-invalido-exemplo.local';
```

3. Clique em `Execute workflow`.
4. Confira se o email de alerta chegou.
5. Volte a URL correta:

```js
const siteUrl = 'https://cajui.ifnmg.edu.br';
```

6. Salve o workflow.

## Ativar o monitoramento

Depois de testar:

1. Clique no toggle `Active` no workflow.
2. O n8n passara a checar o site automaticamente a cada 5 minutos.

Para que o monitoramento continue rodando, mantenha o container do n8n ativo.
