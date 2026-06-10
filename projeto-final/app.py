"""
==========================================================================
  Code Review & Documentation Generator — Interface de Revisão Humana
  Aplicativo Streamlit para gerenciamento e aprovação de documentações
  geradas automaticamente por IA a partir de commits Git.
==========================================================================
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════════════

# URL do webhook do n8n que recebe a aprovação e faz o commit no GitHub
N8N_PUBLISH_WEBHOOK_URL = st.secrets.get(
    "N8N_PUBLISH_WEBHOOK_URL",
    "http://localhost:5678/webhook/publish-docs"
)

DATABASE_PATH = Path(__file__).parent / "database.db"


# ═══════════════════════════════════════════════════════════════════════════
# CAMADA DE BANCO DE DADOS (SQLite)
# ═══════════════════════════════════════════════════════════════════════════

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão reutilizável ao banco SQLite local."""
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database(conn: sqlite3.Connection) -> None:
    """Cria a tabela `documentations` caso ainda não exista."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documentations (
            id              INTEGER   PRIMARY KEY AUTOINCREMENT,
            repo_name       TEXT      NOT NULL,
            commit_sha      TEXT      NOT NULL,
            contextual_analysis TEXT,
            generated_docs  TEXT,
            status          TEXT      NOT NULL DEFAULT 'pending',
            created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def fetch_by_status(conn: sqlite3.Connection, status: str) -> list[dict]:
    """Busca todas as documentações filtradas por status."""
    rows = conn.execute(
        "SELECT * FROM documentations WHERE status = ? ORDER BY created_at DESC",
        (status,),
    ).fetchall()
    return [dict(row) for row in rows]


def count_by_status(conn: sqlite3.Connection, status: str) -> int:
    """Retorna a contagem de registros por status."""
    result = conn.execute(
        "SELECT COUNT(*) FROM documentations WHERE status = ?",
        (status,),
    ).fetchone()
    return result[0]


def update_status(conn: sqlite3.Connection, doc_id: int, new_status: str) -> None:
    """Atualiza o status de um registro específico."""
    conn.execute(
        "UPDATE documentations SET status = ? WHERE id = ?",
        (new_status, doc_id),
    )
    conn.commit()


def update_docs_content(
    conn: sqlite3.Connection, doc_id: int, new_content: str
) -> None:
    """Atualiza o conteúdo da documentação gerada (após edição humana)."""
    conn.execute(
        "UPDATE documentations SET generated_docs = ? WHERE id = ?",
        (new_content, doc_id),
    )
    conn.commit()


# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE INTEGRAÇÃO (n8n Webhook)
# ═══════════════════════════════════════════════════════════════════════════

def publish_documentation(
    repo_name: str, commit_sha: str, final_docs: str
) -> requests.Response:
    """
    Envia a documentação aprovada para o webhook de publicação do n8n.
    O n8n se encarrega de fazer o commit do arquivo .md no repositório.
    """
    payload = {
        "repo_name": repo_name,
        "commit_sha": commit_sha,
        "final_docs": final_docs,
        "published_at": datetime.utcnow().isoformat(),
    }
    response = requests.post(
        N8N_PUBLISH_WEBHOOK_URL,
        json=payload,
        timeout=30,
    )
    return response


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS DE UI
# ═══════════════════════════════════════════════════════════════════════════

def render_impact_badge(level: str) -> str:
    """Retorna um badge colorido baseado no nível de impacto."""
    colors = {
        "Low": "🟢",
        "Medium": "🟡",
        "High": "🔴",
    }
    emoji = colors.get(level, "⚪")
    return f"{emoji} **{level}**"


def parse_contextual_analysis(raw: str) -> dict | None:
    """Tenta parsear a análise contextual como JSON estruturado."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


# ═══════════════════════════════════════════════════════════════════════════
# INTERFACE STREAMLIT
# ═══════════════════════════════════════════════════════════════════════════

def main() -> None:
    # ── Configuração da página ──────────────────────────────────────────
    st.set_page_config(
        page_title="Code Review & Docs Generator",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── CSS customizado para visual limpo e moderno ─────────────────────
    st.markdown("""
    <style>
        /* Tipografia e fundo geral */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        /* Cards de estatísticas na sidebar */
        .stat-card {
            background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 0.8rem;
            text-align: center;
        }
        .stat-card h2 {
            margin: 0;
            font-size: 2.4rem;
            font-weight: 700;
            background: linear-gradient(90deg, #6C63FF, #48C9B0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-card p {
            margin: 0.3rem 0 0 0;
            font-size: 0.85rem;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Cabeçalho principal */
        .main-header {
            text-align: center;
            padding: 1.5rem 0 1rem 0;
        }
        .main-header h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #6C63FF, #48C9B0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .main-header p {
            color: #999;
            font-size: 0.95rem;
        }

        /* Estilo do card de documentação */
        .doc-card {
            background: rgba(30, 30, 47, 0.6);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 14px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(10px);
        }
        .doc-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
        }
        .doc-card-header .repo {
            font-weight: 600;
            font-size: 1.1rem;
            color: #e0e0e0;
        }
        .doc-card-header .sha {
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
            color: #6C63FF;
            background: rgba(108,99,255,0.1);
            padding: 2px 8px;
            border-radius: 6px;
        }

        /* Botões estilizados */
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            padding: 0.5rem 1.5rem;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(108,99,255,0.3);
        }

        /* Divisor com gradiente */
        .gradient-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #6C63FF, #48C9B0, transparent);
            border: none;
            margin: 1.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

    # ── Inicialização do banco ──────────────────────────────────────────
    conn = get_connection()
    init_database(conn)

    # ── Sidebar — Estatísticas e Navegação ──────────────────────────────
    with st.sidebar:
        st.markdown("## 📊 Painel de Controle")
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        pending_count = count_by_status(conn, "pending")
        approved_count = count_by_status(conn, "approved")
        rejected_count = count_by_status(conn, "rejected")

        st.markdown(f"""
        <div class="stat-card">
            <h2>{pending_count}</h2>
            <p>⏳ Pendentes</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-card">
            <h2>{approved_count}</h2>
            <p>✅ Aprovadas</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-card">
            <h2>{rejected_count}</h2>
            <p>❌ Rejeitadas</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Filtro de visualização
        view_filter = st.selectbox(
            "Visualizar",
            ["Pendentes", "Aprovadas", "Rejeitadas"],
            index=0,
        )

    # ── Cabeçalho Principal ─────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>📝 Code Review & Documentation Generator</h1>
        <p>Revisão humana inteligente de documentações geradas por IA</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # ── Mapeamento de filtros para status ───────────────────────────────
    status_map = {
        "Pendentes": "pending",
        "Aprovadas": "approved",
        "Rejeitadas": "rejected",
    }
    current_status = status_map[view_filter]
    docs = fetch_by_status(conn, current_status)

    if not docs:
        st.info(
            f"Nenhuma documentação com status **'{view_filter.lower()}'** encontrada.",
            icon="📭",
        )
        return

    # ── Lista de documentações ──────────────────────────────────────────
    st.markdown(f"### 📋 {view_filter} ({len(docs)})")

    for doc in docs:
        doc_id = doc["id"]
        repo = doc["repo_name"]
        sha = doc["commit_sha"][:8]
        created = doc["created_at"]

        with st.expander(f"🔹 {repo}  —  `{sha}`  •  {created}", expanded=False):

            # ── Análise Contextual ──────────────────────────────────────
            st.markdown("#### 🧠 Análise Contextual da IA")

            analysis = parse_contextual_analysis(doc["contextual_analysis"])

            if analysis:
                col1, col2 = st.columns(2)
                with col1:
                    requires = "✅ Sim" if analysis.get("requires_update") else "❌ Não"
                    st.metric("Requer Atualização?", requires)
                with col2:
                    impact = analysis.get("impact_level", "N/A")
                    st.markdown(
                        f"**Nível de Impacto:** {render_impact_badge(impact)}"
                    )

                st.markdown("**Justificativa:**")
                st.info(analysis.get("justification", "Sem justificativa disponível."))
            else:
                # Caso a análise não seja JSON, exibe como texto
                st.text(doc["contextual_analysis"] or "Análise não disponível.")

            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

            # ── Documentação Gerada ─────────────────────────────────────
            st.markdown("#### 📄 Documentação Gerada")

            generated = doc["generated_docs"]

            if generated:
                # Editor de texto para revisão humana
                edited_docs = st.text_area(
                    "Edite a documentação antes de aprovar (se necessário):",
                    value=generated,
                    height=400,
                    key=f"editor_{doc_id}",
                )

                # Preview renderizado
                with st.expander("👁️ Pré-visualização Renderizada", expanded=False):
                    st.markdown(edited_docs)

            else:
                st.warning(
                    "A IA decidiu que este commit não necessita de atualização na "
                    "documentação. Veja a justificativa acima.",
                    icon="ℹ️",
                )
                edited_docs = None

            # ── Ações (apenas para pendentes) ───────────────────────────
            if current_status == "pending":
                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

                col_approve, col_reject = st.columns(2)

                with col_approve:
                    if edited_docs and st.button(
                        "✅ Aprovar e Publicar",
                        key=f"approve_{doc_id}",
                        type="primary",
                        use_container_width=True,
                    ):
                        with st.spinner("Enviando para publicação via n8n..."):
                            try:
                                # Salva edições no banco antes de publicar
                                update_docs_content(conn, doc_id, edited_docs)

                                # Envia para o webhook de publicação
                                resp = publish_documentation(
                                    repo_name=doc["repo_name"],
                                    commit_sha=doc["commit_sha"],
                                    final_docs=edited_docs,
                                )
                                resp.raise_for_status()

                                # Atualiza status
                                update_status(conn, doc_id, "approved")
                                st.success(
                                    "Documentação aprovada e enviada com sucesso! 🚀",
                                    icon="✅",
                                )
                                st.rerun()

                            except requests.RequestException as e:
                                st.error(
                                    f"Erro ao publicar: {e}. "
                                    "Verifique se o webhook do n8n está ativo.",
                                    icon="🚨",
                                )

                with col_reject:
                    if st.button(
                        "❌ Rejeitar / Arquivar",
                        key=f"reject_{doc_id}",
                        use_container_width=True,
                    ):
                        update_status(conn, doc_id, "rejected")
                        st.warning("Documentação rejeitada e arquivada.", icon="🗑️")
                        st.rerun()

    # ── Footer ──────────────────────────────────────────────────────────
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.caption(
        "Code Review & Documentation Generator • "
        "Powered by n8n + Streamlit + IA Generativa"
    )


if __name__ == "__main__":
    main()
