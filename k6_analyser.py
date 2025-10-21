import json
import pandas as pd

# Altere aqui o caminho para o arquivo JSON que você quer analisar
file_path = "resultados_com_tags.json"

# Carregar o arquivo
with open(file_path, "r") as f:
    lines = f.readlines()

# Converter para dicionários
records = [json.loads(line) for line in lines if line.strip()]

# Filtrar apenas pontos (metric data)
points = [r for r in records if r.get("type") == "Point"]

# Criar DataFrame
df = pd.DataFrame([
    {
        "metric": r["metric"],
        "time": r["data"]["time"],
        "value": r["data"]["value"],
        **r["data"]["tags"]
    }
    for r in points
])

# Filtrar apenas métricas http
df_http = df[df["metric"].str.startswith("http_")]

# Montar tabela consolidada por endpoint
result_table = []
for endpoint, group in df_http.groupby("endpoint"):
    durations = group.loc[group["metric"] == "http_req_duration", "value"]
    fails = group.loc[group["metric"] == "http_req_failed", "value"].sum()
    total_reqs = len(durations)
    if total_reqs > 0:
        result_table.append({
            "Endpoint": endpoint,
            "Requisições Totais": total_reqs,
            "Falhas": int(fails),
            "Taxa de Falha": round(fails / total_reqs, 4),
            "Latência Média (ms)": round(durations.mean(), 2),
            "Latência Max (ms)": round(durations.max(), 2),
            "Latência Min (ms)": round(durations.min(), 2),
            "Latência p95 (ms)": round(durations.quantile(0.95), 2)
        })

# Criar DataFrame final
tabela_final = pd.DataFrame(result_table)

# Mostrar tabela
print(tabela_final.to_string(index=False))
