"""
==========================================================================
  API Receiver — Recebe dados do n8n e insere no SQLite
  Roda junto com o Streamlit para receber as análises da IA.
==========================================================================
"""

from flask import Flask, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
DATABASE_PATH = Path(__file__).parent / "database.db"


def get_connection():
    """Retorna conexão ao banco SQLite."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Cria a tabela se não existir."""
    conn = get_connection()
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
    conn.close()


@app.route("/insert-doc", methods=["POST"])
def insert_documentation():
    """
    Recebe os dados do n8n via POST e insere no banco SQLite.
    
    Body esperado (JSON):
    {
        "repo_name": "owner/repo",
        "commit_sha": "abc123...",
        "contextual_analysis": "{...}",
        "generated_docs": "# Markdown..." ou null,
        "status": "pending"
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Corpo da requisição vazio"}), 400

    repo_name = data.get("repo_name", "unknown")
    commit_sha = data.get("commit_sha", "unknown")
    contextual_analysis = data.get("contextual_analysis", "")
    generated_docs = data.get("generated_docs")
    status = data.get("status", "pending")

    try:
        conn = get_connection()
        conn.execute(
            """INSERT INTO documentations 
               (repo_name, commit_sha, contextual_analysis, generated_docs, status)
               VALUES (?, ?, ?, ?, ?)""",
            (repo_name, commit_sha, contextual_analysis, generated_docs, status),
        )
        conn.commit()
        doc_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()

        return jsonify({
            "success": True,
            "message": "Documentação inserida com sucesso.",
            "doc_id": doc_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    init_database()
    print("🚀 API Receiver rodando em http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
