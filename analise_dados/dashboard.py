"""
Dashboard Interativo - Global Cost of Living
Análise visual do custo de vida global usando Streamlit e Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

import google.generativeai as genai

# ── Configuração da Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="🌍 Global Cost of Living Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS Customizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Aplica a fonte Inter apenas em elementos de texto, preservando os ícones nativos do Streamlit */
    html, body, p, h1, h2, h3, h4, h5, h6, li, label, div.stMarkdown, div.stText, div.stMetric, div.stDataFrame {
        font-family: 'Inter', sans-serif;
    }

    /* Fundo principal */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a3e 0%, #16163a 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e0ff;
    }

    /* KPI Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(79, 70, 229, 0.25);
        border-color: rgba(139, 92, 246, 0.3);
    }

    div[data-testid="stMetric"] label {
        color: #a5b4fc !important;
        font-weight: 500;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f0f0ff !important;
        font-weight: 700;
        font-size: 1.8rem;
    }

    /* Títulos */
    .main .stMarkdown h1 {
        color: #e0e0ff;
        font-weight: 700;
        letter-spacing: -0.02em;
    }

    .main .stMarkdown h2 {
        color: #c4b5fd;
        font-weight: 600;
        border-bottom: 2px solid rgba(139, 92, 246, 0.3);
        padding-bottom: 8px;
    }

    .main .stMarkdown h3 {
        color: #a5b4fc;
        font-weight: 600;
    }

    .main .stMarkdown p, .main .stMarkdown li {
        color: #c8c8e8;
    }

    /* Plotly charts container */
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 8px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }

    /* Divider */
    hr {
        border-color: rgba(139, 92, 246, 0.2) !important;
    }

    /* Multiselect & Checkbox styling */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: rgba(139, 92, 246, 0.3) !important;
        border: 1px solid rgba(139, 92, 246, 0.5) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.02);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(139, 92, 246, 0.3);
        border-radius: 4px;
    }

    /* Esconder tooltip "Press Enter to submit form" */
    .stTextInput div[data-testid="InputInstructions"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Carregar Dados ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "dados", "cost-of-living_clean.csv")
    df = pd.read_csv(csv_path)
    return df

df = load_data()

# ── Barra Lateral (Filtros) ─────────────────────────────────────────────────
st.sidebar.markdown("# 🌍 Filtros")
st.sidebar.markdown("---")

# Filtro de qualidade de dados
quality_filter = st.sidebar.checkbox(
    "✅ Apenas dados de alta qualidade",
    value=False,
    help="Filtra apenas cidades onde data_quality == 1 (dados confiáveis segundo o Numbeo)"
)

# Aplicar filtro de qualidade
df_filtered = df.copy()
if quality_filter:
    df_filtered = df_filtered[df_filtered["data_quality"] == 1]

# Filtro por país (multiselect)
countries_available = sorted(df_filtered["country"].unique())
selected_countries = st.sidebar.multiselect(
    "🏳️ Selecione os Países",
    options=countries_available,
    default=[],
    help="Deixe vazio para exibir todos os países",
    placeholder="Todos os países..."
)

if selected_countries:
    df_filtered = df_filtered[df_filtered["country"].isin(selected_countries)]

# Info no sidebar
st.sidebar.markdown("---")
st.sidebar.markdown(f"### 📊 Resumo dos Filtros")
st.sidebar.markdown(f"- **Cidades:** `{len(df_filtered)}`")
st.sidebar.markdown(f"- **Países:** `{df_filtered['country'].nunique()}`")
st.sidebar.markdown(f"- **Qualidade:** {'Alta' if quality_filter else 'Todas'}")

# ── Chat com Gemini AI (Sidebar) ────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Pergunte à IA")

# Configurar Gemini
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
gemini_key = None
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip().startswith("gemini_api_key="):
                gemini_key = line.strip().split("=", 1)[1]

if not gemini_key:
    st.sidebar.warning("⚠️ Chave Gemini não encontrada no .env")
else:
    genai.configure(api_key=gemini_key)

    @st.cache_data
    def build_data_context(_df):
        stats = _df.describe().to_string()
        cols_info = (
            "x1: Refeição simples | x2: Refeição p/2 | x3: McMeal | "
            "x9-x22: Itens supermercado (leite,pão,arroz,ovos,queijo,frango,carne,frutas,vegetais) | "
            "x28: Passagem local | x29: Passe mensal | x36: Utilidades 85m² | "
            "x38: Internet | x39: Academia | x41: Cinema | "
            "x48: Aluguel 1qto centro | x49: Aluguel 1qto fora | "
            "x50: Aluguel 3qtos centro | x51: Aluguel 3qtos fora | "
            "x52: Preço m² centro | x53: Preço m² fora | "
            "x54: Salário médio líquido | x55: Taxa hipoteca | "
            "data_quality: 1=confiável, 0=precisa mais dados"
        )
        sample = _df.head(3).to_string()
        countries = ", ".join(sorted(_df["country"].unique())[:20])
        return f"""Assistente de análise do dataset "Global Cost of Living". Responda em português brasileiro, conciso.
COLUNAS: city, country, {cols_info}
PAÍSES (amostra): {countries} | CIDADES: {len(_df)} | PAÍSES: {_df['country'].nunique()}
ESTATÍSTICAS:\n{stats}\nAMOSTRA:\n{sample}"""

    system_prompt = build_data_context(df_filtered)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Área de mensagens
    chat_container = st.sidebar.container(height=350)
    with chat_container:
        if not st.session_state.chat_messages:
            st.markdown(
                "<p style='color:#666; font-size:0.8rem; text-align:center; margin-top:100px;'>"
                "Faça uma pergunta sobre<br>o custo de vida global</p>",
                unsafe_allow_html=True
            )
        for msg in st.session_state.chat_messages:
            icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
            align = "right" if msg["role"] == "user" else "left"
            bg = "rgba(139,92,246,0.15)" if msg["role"] == "user" else "rgba(255,255,255,0.05)"
            st.markdown(
                f"<div style='text-align:{align}; margin:4px 0;'>"
                f"<span style='background:{bg}; padding:6px 10px; border-radius:10px; "
                f"font-size:0.85rem; display:inline-block; max-width:95%; text-align:left;'>"
                f"{icon} {msg['content']}</span></div>",
                unsafe_allow_html=True
            )

    # Input (form para Enter enviar direto)
    with st.sidebar.form(key="chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            user_input = st.text_input("Pergunta", placeholder="Ex: Maior salário?", label_visibility="collapsed")
        with col_btn:
            send = st.form_submit_button("➤", use_container_width=True)

    if send and user_input:
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            history = [
                {"role": "user", "parts": [system_prompt + "\n\nDiga olá."]},
                {"role": "model", "parts": ["Olá! Pergunte sobre os dados!"]}
            ]
            for msg in st.session_state.chat_messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            chat = model.start_chat(history=history)
            response = chat.send_message(user_input)
            st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.chat_messages.append({"role": "assistant", "content": f"❌ Erro: {e}"})
        st.rerun()

    # Botão limpar
    if st.session_state.chat_messages:
        if st.sidebar.button("🗑️ Limpar conversa", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

st.sidebar.markdown(
    "<p style='color:#888; font-size:0.75rem; text-align:center;'>"
    "Dados: Numbeo Cost of Living<br>Dashboard por Kensei CyberAI</p>",
    unsafe_allow_html=True
)

# ── Cabeçalho Principal ─────────────────────────────────────────────────────
st.markdown("# 🌍 Global Cost of Living Dashboard")
st.markdown(
    "<p style='color:#a5b4fc; font-size:1.1rem; margin-top:-10px;'>"
    "Análise interativa do custo de vida em cidades ao redor do mundo</p>",
    unsafe_allow_html=True
)

# ── KPIs ────────────────────────────────────────────────────────────────────
st.markdown("---")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

avg_salary = df_filtered["x54"].mean()
avg_rent_1br = df_filtered["x48"].mean()
avg_meal = df_filtered["x1"].mean()
avg_utilities = df_filtered["x36"].mean()

with kpi1:
    st.metric(
        label="💰 Salário Médio Mensal",
        value=f"$ {avg_salary:,.0f}",
    )

with kpi2:
    st.metric(
        label="🏠 Aluguel Médio (1 quarto, centro)",
        value=f"$ {avg_rent_1br:,.0f}",
    )

with kpi3:
    st.metric(
        label="🍽️ Refeição Média (restaurante simples)",
        value=f"$ {avg_meal:,.1f}",
    )

with kpi4:
    st.metric(
        label="⚡ Utilidades Básicas (85m²)",
        value=f"$ {avg_utilities:,.0f}",
    )

st.markdown("")

# ── Tema Plotly Padrão ──────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#c8c8e8"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#a5b4fc"),
    ),
    margin=dict(l=40, r=40, t=10, b=40),
)

# ── Gráfico 1: Mapa Choropleth – Salário Médio por País ────────────────────
st.markdown("## 🗺️ Salário Médio Líquido por País")

# Agrupar por país
salary_by_country = (
    df_filtered.groupby("country", as_index=False)["x54"]
    .mean()
    .rename(columns={"x54": "avg_salary"})
    .sort_values("avg_salary", ascending=False)
)

fig_map = px.choropleth(
    salary_by_country,
    locations="country",
    locationmode="country names",
    color="avg_salary",
    hover_name="country",
    color_continuous_scale=[
        [0, "#1a1a3e"],
        [0.2, "#3b1f8e"],
        [0.4, "#6d28d9"],
        [0.6, "#8b5cf6"],
        [0.8, "#a78bfa"],
        [1, "#c4b5fd"],
    ],
    labels={"avg_salary": "Salário Médio (USD)", "country": "País"},

)

fig_map.update_layout(
    **PLOTLY_LAYOUT,
    geo=dict(
        bgcolor="rgba(0,0,0,0)",
        lakecolor="rgba(0,0,0,0)",
        landcolor="#1a1a3e",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#3b3b6b",
        countrycolor="#3b3b6b",
        showocean=True,
        oceancolor="#0f0c29",
        projection_type="natural earth",
    ),
    coloraxis_colorbar=dict(
        title="USD",
        tickfont=dict(color="#a5b4fc"),
        title_font=dict(color="#a5b4fc"),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
    ),
    height=520,
)

st.plotly_chart(fig_map, use_container_width=True, key="choropleth_map")

# ── Gráfico 2: Scatter – Salário vs. Aluguel ───────────────────────────────
st.markdown("## 📈 Salário vs. Aluguel (1 quarto no centro)")

fig_scatter = px.scatter(
    df_filtered,
    x="x54",
    y="x48",
    hover_name="city",
    hover_data={
        "country": True,
        "x54": ":.0f",
        "x48": ":.0f",
    },
    color="country" if df_filtered["country"].nunique() <= 20 else None,
    labels={
        "x54": "Salário Médio Mensal (USD)",
        "x48": "Aluguel 1 Quarto Centro (USD)",
        "country": "País",
    },

    opacity=0.8,
)

# Estilo dos pontos
if df_filtered["country"].nunique() > 20:
    fig_scatter.update_traces(
        marker=dict(
            size=8,
            color="#8b5cf6",
            line=dict(width=1, color="#c4b5fd"),
        ),
    )
else:
    fig_scatter.update_traces(
        marker=dict(
            size=9,
            line=dict(width=1, color="rgba(255,255,255,0.3)"),
        ),
    )

fig_scatter.update_layout(
    **PLOTLY_LAYOUT,
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        title_font=dict(color="#a5b4fc"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        title_font=dict(color="#a5b4fc"),
    ),
    height=520,
    showlegend=df_filtered["country"].nunique() <= 20,
)

st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_salary_rent")

# ── Gráfico 3: Barras – Top 10 Cidades Mais Caras ──────────────────────────
st.markdown("## 🏙️ Top 10 Cidades Mais Caras (Itens Básicos)")
st.markdown(
    "<p style='color:#888; font-size:0.85rem; margin-top:-10px;'>"
    "Baseado na soma de itens básicos de supermercado: Leite, Pão, Arroz, Ovos, "
    "Queijo, Frango, Carne, Maçãs, Banana, Laranjas, Tomate, Batata, Cebola, Alface (x9 a x22)</p>",
    unsafe_allow_html=True
)

basic_items_cols = [f"x{i}" for i in range(9, 23)]  # x9 to x22
df_filtered_cost = df_filtered.copy()
df_filtered_cost["basic_cost"] = df_filtered_cost[basic_items_cols].sum(axis=1)
df_filtered_cost["city_country"] = df_filtered_cost["city"] + ", " + df_filtered_cost["country"]

top10 = df_filtered_cost.nlargest(10, "basic_cost")[["city_country", "basic_cost", "city", "country"]].reset_index(drop=True)

fig_bar = go.Figure()

# Gradient effect via individual bar colors
n = len(top10)
colors = [
    f"rgba({139 + int(i * 10)}, {92 + int(i * 8)}, {246 - int(i * 5)}, 0.85)"
    for i in range(n)
]

fig_bar.add_trace(go.Bar(
    x=top10["basic_cost"],
    y=top10["city_country"],
    orientation="h",
    marker=dict(
        color=colors[::-1],
        line=dict(color="rgba(255,255,255,0.1)", width=1),
        cornerradius=6,
    ),
    text=[f"$ {v:,.1f}" for v in top10["basic_cost"]],
    textposition="outside",
    textfont=dict(color="#c4b5fd", size=12, family="Inter"),
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Custo Básico: $ %{x:,.2f}<br>"
        "<extra></extra>"
    ),
))

fig_bar.update_layout(
    **PLOTLY_LAYOUT,
    xaxis=dict(
        title="Soma dos Itens Básicos (USD)",
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        title_font=dict(color="#a5b4fc"),
    ),
    yaxis=dict(
        autorange="reversed",
        title="",
        tickfont=dict(size=12),
    ),
    height=480,
    showlegend=False,
)

st.plotly_chart(fig_bar, use_container_width=True, key="top10_bar_chart")

# ── Rodapé ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#666; font-size:0.8rem;'>"
    "🌍 Global Cost of Living Dashboard — Dados: Numbeo | "
    "Desenvolvido com Streamlit & Plotly | Kensei CyberAI © 2026</p>",
    unsafe_allow_html=True,
)
