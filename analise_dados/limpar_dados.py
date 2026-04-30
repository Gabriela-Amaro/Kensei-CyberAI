import pandas as pd
import numpy as np

print("Iniciando a limpeza dos dados...")

# Carregar os dados
df = pd.read_csv('dados/cost-of-living.csv')
print(f"Linhas originais: {len(df)}")

# 1. Remover coluna de índice original
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

# 2. Remover duplicados
df = df.drop_duplicates()
print(f"Linhas após remover duplicados: {len(df)}")

# 3. Remover dados inválidos
# As colunas x1 até x55 representam preços/custos, logo não devem ser <= 0.
colunas_preco = [f"x{i}" for i in range(1, 56)]

for col in colunas_preco:
    if col in df.columns:
        # Substitui os <= 0 (inválidos) por NaN para tratá-los junto com os nulos
        df.loc[df[col] <= 0, col] = np.nan

# 4. Preencher nulos (e os inválidos que viraram nulos)
# Agruparemos pela mediana de cada país, para ser mais preciso
# Se algum país inteiro não tiver dados para uma coluna, completamos com a mediana global.
for col in colunas_preco:
    if col in df.columns:
        # Mediana por país
        df[col] = df.groupby('country')[col].transform(lambda x: x.fillna(x.median()))
        # Se ainda sobrarem vazios, usar a global
        global_median = df[col].median()
        df[col] = df[col].fillna(global_median)

print("Valores ausentes (nulos e inválidos) preenchidos com sucesso usando a mediana (por país e, caso necessário, global).")

# 5. Converter datas
# O dataset e o dicionário não possuem colunas de data.
print("Aviso de Data: Não foram encontradas colunas de data no dataset para conversão (conforme o dicionário).")

# Salvar o dataset limpo
output_file = 'dados/cost-of-living_clean.csv'
df.to_csv(output_file, index=False)
print(f"Dataset salvo com sucesso em '{output_file}'!")

print("\n--- INFO DO DATASET LIMPO ---")
print(df.info())
