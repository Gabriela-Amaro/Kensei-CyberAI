# 🌍 Global Cost of Living Dashboard

Este projeto faz parte dos estudos das **Semanas 3 e 4** do curso Kensei CyberAI. O objetivo foi criar uma aplicação web interativa de análise de dados, integrando Inteligência Artificial para facilitar o acesso à informação e exploração.

## 📌 Visão Geral

Desenvolvemos um Dashboard interativo focado na análise do Custo de Vida Global (Global Cost of Living). A aplicação permite filtrar dados de diversos países e exibir as principais métricas econômicas globais, incluindo salários médios, custos de aluguel e despesas em utilidades básicas.

Além das visualizações ricas de mapas e gráficos de correlação, o sistema conta com um **assistente virtual baseado no Google Gemini (IA Generativa)** embutido na barra lateral. Isso permite que o usuário faça consultas e análises complexas sobre a base de dados utilizando linguagem natural.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3
- **Interface Web:** Streamlit
- **Manipulação de Dados:** Pandas
- **Visualização Gráfica:** Plotly (Express e Graph Objects)
- **Inteligência Artificial:** Google Generative AI (Gemini 2.5 Flash)

## 🗂️ Estrutura do Diretório

```text
analise_dados/
│
├── dados/
│   ├── cost-of-living_clean.csv    # Dataset higienizado utilizado na aplicação
│   └── dicionario_dados.md         # Descrição detalhada de todas as colunas (x1 a x55)
│
├── .streamlit/
│   └── config.toml                 # Configurações de tema (Dark Mode forçado)
│
├── dashboard.py                    # Script principal da aplicação web interativa
├── limpar_dados.py                 # Script de higienização inicial de dados faltantes/ruins
└── chat_gemini.py             # Script exploratório de integração com Gemini API
```

## 🚀 Como Executar Localmente

### 1. Configurar as Credenciais da IA
Na raiz principal do repositório (uma pasta antes de `analise_dados`), crie ou edite o arquivo `.env` e insira sua chave da API do Gemini (Google AI Studio):
```env
gemini_api_key=SUA_CHAVE_AQUI
```

### 2. Preparar o Ambiente Virtual
Navegue até a pasta do projeto de dados e crie um ambiente virtual para isolar as bibliotecas:
```bash
cd analise_dados
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências
Com o ambiente ativado (você verá um `(.venv)` no terminal), instale os pacotes a partir do arquivo de requisitos localizado na raiz do projeto:
```bash
pip install -r ../requirements.txt
```

### 4. Rodar o Dashboard
Inicie a aplicação utilizando o Streamlit:
```bash
streamlit run dashboard.py
```
A aplicação abrirá no seu navegador, no endereço padrão `http://localhost:8501`.

## 🧠 Chat Integrado com Gemini AI

Para transformar o dashboard numa experiência "conversa-com-dados", há um chat embutido na barra lateral esquerda. 

Por trás das cortinas, o **Gemini** recebe dinamicamente um *system prompt* rico, contendo o dicionário dos dados em português, resumo estatístico (médias, min, max, quartis) da tabela atualmente filtrada e amostras brutas. Dessa forma, você pode fazer perguntas diretas como:
- *"Qual cidade tem o aluguel mais caro no centro comparado ao salário?"*
- *"Quais são os países mais baratos da amostra para se morar?"*
