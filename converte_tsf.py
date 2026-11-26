import pandas as pd

caminho_tsf = "dataset/pedestrian_counts_dataset.tsf"
caminho_csv = "dataset/pedestrian_drift.csv"

series_list = []
lendo_dados = False

with open(caminho_tsf, "r", encoding="utf-8", errors="ignore") as f:
    for linha in f:
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        if linha.startswith("@data"):
            lendo_dados = True
            continue
        if lendo_dados:
            partes = linha.split(":")
            nome = partes[0]
            inicio = partes[1]
            valores = [float(x) if x != "?" else None for x in partes[2].split(",")]
            
            idx = pd.date_range(start=inicio, periods=len(valores), freq="1h")
            s = pd.Series(valores, index=idx, name=nome)
            series_list.append(s)

# Seleciona os 10 sensores com maior quantidade de registros válidos, para maior abrangência sem precisar pegar tudo
series_list.sort(key=lambda s: s.notna().sum(), reverse=True)
top_series = series_list[:10]

# Junta pelo índice temporal real e recorta o período onde todos têm cobertura (2016 a 2021)
df = pd.concat(top_series, axis=1)
df = df.loc["2016-01-01":"2021-04-30"]  # pega 4 anos de comportamento normal + choque de 2020/2021
df = df.ffill().bfill()

# Formata no padrão exato esperado pelo Dataset_Custom do TimeAlign
df.index.name = "date"
df.reset_index(inplace=True)
df.to_csv(caminho_csv, index=False)

print(f"CSV gerado com sucesso! Shape: {df.shape}")
print(f"Período: {df['date'].min()} até {df['date'].max()}")
print(df.head(3))