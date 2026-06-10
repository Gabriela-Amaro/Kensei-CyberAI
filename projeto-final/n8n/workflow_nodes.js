/**
 * ==========================================================================
 *  Code Review & Documentation Generator — Nós JavaScript para n8n
 *  Estruturação completa do fluxo de automação passo a passo.
 * ==========================================================================
 *
 *  ARQUITETURA DO WORKFLOW N8N COM API RECEIVER PYTHON (Flask):
 *
 *  ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
 *  │  Webhook 1   │────▶│  Code: Parse │────▶│      IF:       │
 *  │  (GitHub     │     │  Payload     │     │  skipped?    │
 *  │   Push)      │     │  do Push     │     │              │
 *  └─────────────┘     └──────────────┘     └──────────────┘
 *                                                  │
 *                                            [false / push]
 *                                                  │
 *                                                  ▼
 *                                     ┌──────────────────────────┐
 *                                     │  HTTP Requests (Parallel)│
 *                                     │  - Árvore                │
 *                                     │  - Docs                  │
 *                                     │  - Diff                  │
 *                                     └──────────────────────────┘
 *                                                  │
 *                                                  ▼
 *                                           ┌──────────────┐
 *                                           │    Merge     │
 *                                           └──────────────┘
 *                                                  │
 *                                                  ▼
 *                                     ┌──────────────────────────┐
 *                                     │  Code: Montar Prompt 1   │
 *                                     │  (Analisador)            │
 *                                     └──────────────────────────┘
 *                                                  │
 *                                                  ▼
 *                                     ┌──────────────────────────┐
 *                                     │  IA Analisador (Gemini)  │
 *                                     └──────────────────────────┘
 *                                                  │
 *                                                  ▼
 *                                     ┌──────────────────────────┐
 *                                     │  Code: Parse Resposta +  │
 *                                     │  Decisão (IF)            │
 *                                     └──────────────────────────┘
 *                                                  │
 *                                           ┌──────┴───────┐
 *                                           │              │
 *                                        [true]         [false]
 *                                           │              │
 *                                           ▼              │
 *                                  ┌────────────────┐      │
 *                                  │  Code: Montar  │      │
 *                                  │  Prompt 2      │      │
 *                                  │  (Gerador)     │      │
 *                                  └────────────────┘      │
 *                                           │              │
 *                                           ▼              │
 *                                  ┌────────────────┐      │
 *                                  │   IA Gerador   │      │
 *                                  │   (Gemini)     │      │
 *                                  └────────────────┘      │
 *                                           │              │
 *                                           ▼              ▼
 *                                  ┌────────────────────────────────┐
 *                                  │  Code: Preparar SQLite (Flask) │
 *                                  └────────────────────────────────┘
 *                                                  │
 *                                                  ▼
 *                                  ┌────────────────────────────────┐
 *                                  │  HTTP: Salvar no SQLite        │
 *                                  │  (POST -> Flask /insert-doc)   │
 *                                  └────────────────────────────────┘
 */


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 1: WEBHOOK DE ENTRADA (GitHub Push)
// ═══════════════════════════════════════════════════════════════════════════
//
// CONFIGURAÇÃO NO N8N (UI):
// - Tipo: Webhook
// - Método: POST
// - Path: /github-push
// - Response Mode: whenLastNodeFinishes
// - No GitHub, configure o webhook com Content-Type = application/json e URL com /webhook/ (Produção)


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 2: CODE NODE — Parse do Payload do Push
// ═══════════════════════════════════════════════════════════════════════════

// Detecta o formato do payload (JSON direto ou form-encoded)
const raw = $input.first().json.body;
let payload;

if (typeof raw.payload === 'string') {
  payload = JSON.parse(raw.payload);
} else {
  payload = raw;
}

// Ignora eventos que NÃO são push (ex: ping do GitHub)
const event = $input.first().json.headers['x-github-event'];
if (event !== 'push') {
  return [{
    json: {
      skipped: true,
      reason: `Evento '${event}' ignorado. Apenas 'push' é processado.`
    }
  }];
}

// Extrai dados do repositório
const repoFullName = payload.repository.full_name;  // "owner/repo"
const repoName = payload.repository.name;
const repoOwner = payload.repository.owner.login || payload.repository.owner.name;
const defaultBranch = payload.repository.default_branch || "main";

// Extrai dados do push
const headCommitSha = payload.head_commit.id;
const headCommitMessage = payload.head_commit.message;

// Monta o diff URL (compara o before com o after)
const beforeSha = payload.before;
const afterSha = payload.after;

// Lista de arquivos modificados (do payload do push)
const commits = payload.commits || [];
const modifiedFiles = [];
commits.forEach(commit => {
    (commit.added || []).forEach(f => modifiedFiles.push({ file: f, action: "added" }));
    (commit.modified || []).forEach(f => modifiedFiles.push({ file: f, action: "modified" }));
    (commit.removed || []).forEach(f => modifiedFiles.push({ file: f, action: "removed" }));
});

return [{
    json: {
        skipped: false,
        repo_full_name: repoFullName,
        repo_name: repoName,
        repo_owner: repoOwner,
        default_branch: defaultBranch,
        head_commit_sha: headCommitSha,
        head_commit_message: headCommitMessage,
        before_sha: beforeSha,
        after_sha: afterSha,
        modified_files: modifiedFiles,
        compare_url: `https://api.github.com/repos/${repoFullName}/compare/${beforeSha}...${afterSha}`
    }
}];


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 3: IF — skipped?
// ═══════════════════════════════════════════════════════════════════════════
//
// CONFIGURAÇÃO NO N8N (UI):
// - Condição: {{ $json.skipped }} is false (Boolean)
// - True  -> Conecta aos 3 HTTP Requests em paralelo
// - False -> Fim da execução (ignora ping)


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 4: HTTP REQUESTS — Buscar Árvore de Arquivos, Docs e Diff (Paralelo)
// ═══════════════════════════════════════════════════════════════════════════
//
// 4a) Buscar Árvore de Arquivos (Renomear para: HTTP Árvore):
//   - Método: GET
//   - URL: https://api.github.com/repos/{{ $json.repo_full_name }}/git/trees/{{ $json.default_branch }}?recursive=1
//   - Authentication: Generic Credential Type -> Header Auth (Authorization: Bearer <token>)
//   - Headers: Accept = application/vnd.github.v3+json
//
// 4b) Buscar Documentação Atual (Renomear para: HTTP Docs):
//   - Método: GET
//   - URL: https://api.github.com/repos/{{ $json.repo_full_name }}/contents/README.md?ref={{ $json.default_branch }}
//   - Authentication: Generic Credential Type -> Header Auth (Authorization: Bearer <token>)
//   - Headers: Accept = application/vnd.github.v3+json
//
// 4c) Buscar Git Diff (Renomear para: HTTP Diff):
//   - Método: GET
//   - URL: {{ $json.compare_url }}
//   - Authentication: Generic Credential Type -> Header Auth (Authorization: Bearer <token>)
//   - Headers: Accept = application/vnd.github.v3.diff


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 5: MERGE
// ═══════════════════════════════════════════════════════════════════════════
//
// CONFIGURAÇÃO NO N8N (UI):
// - Mode: Choose how to merge -> Append
// - Input 1: HTTP Árvore
// - Input 2: HTTP Docs
// - Input 3: HTTP Diff (clique em "Add Input" para adicionar a 3ª entrada)
// - Conecta na entrada do Code Node "Montar Contexto Prompt 1"


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 6: CODE NODE — Montar Contexto para IA (Prompt 1 — Analisador)
// ═══════════════════════════════════════════════════════════════════════════

// Busca dados consolidados dos nós executados anteriormente
const repoData = $('Parse Payload').first().json;

// Resultado da árvore de arquivos
const treeResponse = $('HTTP Árvore').first().json;
const fileTree = (treeResponse.tree || [])
    .map(item => `${item.type === 'tree' ? '[DIR]' : '[FILE]'} ${item.path}`)
    .join('\n');

// Resultado da documentação atual
const docsResponse = $('HTTP Docs').first().json;
let currentDocs = '';
if (docsResponse.content) {
    currentDocs = Buffer.from(docsResponse.content, 'base64').toString('utf-8');
}
const docFileSha = docsResponse.sha || '';
const docFilePath = docsResponse.path || 'README.md';

// Resultado do diff
const gitDiff = $('HTTP Diff').first().json;
const diffText = typeof gitDiff === 'string' ? gitDiff : (gitDiff.body || JSON.stringify(gitDiff));

// Monta o prompt
const analyzerPrompt = `
<ARVORE_ARQUIVOS>
${fileTree}
</ARVORE_ARQUIVOS>

<DOCUMENTACAO_ATUAL>
${currentDocs}
</DOCUMENTACAO_ATUAL>

<GIT_DIFF>
${diffText}
</GIT_DIFF>
`;

return [{
    json: {
        ...repoData,
        file_tree: fileTree,
        current_docs: currentDocs,
        git_diff: diffText,
        doc_file_sha: docFileSha,
        doc_file_path: docFilePath,
        analyzer_prompt: analyzerPrompt
    }
}];


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 7: AI AGENT — Analisador de Contexto (Prompt 1)
// ═══════════════════════════════════════════════════════════════════════════
//
// CONFIGURAÇÃO NO N8N (UI):
// - Source for Prompt: Define below
// - System Message: Cole o conteúdo de prompts/prompt_01_analisador_contexto.md
// - User Message: {{ $json.analyzer_prompt }}
// - Require Specific Output Format: Ative e selecione JSON
// - Chat Model: Conecte o Google Gemini Chat Model configurado com a API Key e o modelo gemini-2.5-flash


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 8: CODE NODE — Parse da Resposta do Analisador + Decisão (IF)
// ═══════════════════════════════════════════════════════════════════════════

const aiResponse = $input.first().json;

// A resposta pode vir em "output", "text" ou "message"
const rawText = aiResponse.output || aiResponse.text || aiResponse.message || JSON.stringify(aiResponse);
const cleaned = rawText.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
const analysis = JSON.parse(cleaned);

// Recupera dados do Parse Payload
const previous = $('Parse Payload').first().json;

return [{
    json: {
        repo_full_name: previous.repo_full_name,
        head_commit_sha: previous.head_commit_sha,
        default_branch: previous.default_branch,
        contextual_analysis: JSON.stringify(analysis),
        requires_update: analysis.requires_update,
        justification: analysis.justification,
        impact_level: analysis.impact_level
    }
}];

// Após este nó, use um IF do n8n:
// Condição: {{ $json.requires_update }} is true (Boolean)
// True  -> Segue para "Montar Contexto Prompt 2"
// False -> Segue para "Preparar SQLite"


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 9: CODE NODE — Montar Contexto para IA (Prompt 2 — Gerador)
// ═══════════════════════════════════════════════════════════════════════════

// Apenas no caminho TRUE do IF
const data = $input.first().json;

// Busca o estado anterior dos nós HTTP
const fileTreePrompt2 = $('Montar Contexto para IA - Analisador').first().json.file_tree;
const currentDocsPrompt2 = $('Montar Contexto para IA - Analisador').first().json.current_docs;
const gitDiffPrompt2 = $('Montar Contexto para IA - Analisador').first().json.git_diff;

const generatorPrompt = `
<DOCUMENTACAO_ATUAL>
${currentDocsPrompt2}
</DOCUMENTACAO_ATUAL>

<GIT_DIFF>
${gitDiffPrompt2}
</GIT_DIFF>

<ANALISE_CONTEXTO>
${data.contextual_analysis}
</ANALISE_CONTEXTO>

<ARVORE_ARQUIVOS>
${fileTreePrompt2}
</ARVORE_ARQUIVOS>
`;

return [{
    json: {
        ...data,
        generator_prompt: generatorPrompt
    }
}];


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 10: AI AGENT — Gerador de Documentação (Prompt 2)
// ═══════════════════════════════════════════════════════════════════════════
//
// CONFIGURAÇÃO NO N8N (UI):
// - Source for Prompt: Define below
// - System Message: Cole o conteúdo de prompts/prompt_02_gerador_documentacao.md
// - User Message: {{ $json.generator_prompt }}
// - Chat Model: Google Gemini (gemini-2.5-flash)


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 11: CODE NODE — Preparar Dados para Inserção (Flask / SQLite)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Consolida dados do caminho com documentação (True) ou sem documentação (False).
 * Conecte as duas saídas (o AI Agent Gerador e o caminho False do IF) a este nó.
 */
const inputData = $input.first().json;

// Se veio do gerador, a documentação está em "output" ou "text". Se veio do caminho False, fica null.
const generatedDocs = inputData.output || inputData.text || null;

// Busca dados da resposta do decisor (nó 8)
const decisionData = $('Parse da Resposta').first().json;

return [{
    json: {
        repo_name: decisionData.repo_full_name,
        commit_sha: decisionData.head_commit_sha,
        contextual_analysis: decisionData.contextual_analysis,
        generated_docs: generatedDocs,
        status: 'pending'
    }
}];


// ═══════════════════════════════════════════════════════════════════════════
// NÓ 12: HTTP REQUEST — Salvar no SQLite via API Receiver
// ═══════════════════════════════════════════════════════════════════════════
//
// CONFIGURAÇÃO NO N8N (UI):
// - Método: POST
// - URL: http://localhost:5000/insert-doc
// - Send Body: True
// - Body Content Type: JSON
// - Specify Body: Using Fields Below
//   - repo_name: {{ $json.repo_name }}
//   - commit_sha: {{ $json.commit_sha }}
//   - contextual_analysis: {{ $json.contextual_analysis }}
//   - generated_docs: {{ $json.generated_docs }}
//   - status: {{ $json.status }}


// ═══════════════════════════════════════════════════════════════════════════
// ══════════════════════  FLUXO 2: PUBLICAÇÃO  ═══════════════════════════
// ═══════════════════════════════════════════════════════════════════════════

// O fluxo de publicação (Webhook 2 -> Buscar SHA -> Preparar Commit -> PUT Commit -> Respond)
// segue a mesma estrutura original. Certifique-se de que os nós de HTTP usam a credencial do GitHub.
