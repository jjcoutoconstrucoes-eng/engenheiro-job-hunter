from datetime import datetime
from urllib.parse import quote
import csv
import time
import requests
import feedparser

from config import (
    CARGOS,
    LOCALIZACOES,
    SALARIO_MINIMO,
    SALARIO_ALVO,
    REGIMES,
    NIVEL,
    SITES,
)


# ============================================================
# JOB HUNTER - ENGENHEIRO ORÇAMENTISTA
# ETAPA 6 - COLETA VIA RSS
# ============================================================

print("=" * 70)
print("JOB HUNTER - ENGENHEIRO ORÇAMENTISTA")
print("ETAPA 6 - COLETA VIA RSS")
print("=" * 70)

print(f"\nRobô executado em: {datetime.now()}")

print("\nPERFIL DE BUSCA")
print("-" * 70)

for cargo in CARGOS:
    print(f"- {cargo}")

print("\nLOCALIZAÇÕES")
print("-" * 70)

for local in LOCALIZACOES:
    print(f"- {local}")

print("\nCONDIÇÕES")
print("-" * 70)

print(f"- Salário mínimo: R$ {SALARIO_MINIMO:,.0f}")
print(f"- Salário alvo: R$ {SALARIO_ALVO:,.0f}")
print(f"- Regimes: {', '.join(REGIMES)}")
print(f"- Níveis: {', '.join(NIVEL)}")


# ============================================================
# DOMÍNIOS
# ============================================================

DOMINIOS = {
    "LinkedIn": "linkedin.com",
    "Indeed": "br.indeed.com",
    "Gupy": "gupy.io",
    "InfoJobs": "infojobs.com.br",
    "Catho": "catho.com.br",
    "Glassdoor": "glassdoor.com.br",
    "Riovagas": "riovagas.com.br",
    "Jobbol": "jobbol.com.br",
    "Robert Half": "roberthalf.com.br",
    "Bebee": "br.bebee.com",
    "Sólides": "solides.com.br",
}


# ============================================================
# HTTP
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# FUNÇÕES
# ============================================================

def montar_consulta(cargo, local, dominio):
    """
    Monta a consulta para o RSS.

    Usamos o domínio do site para tentar manter
    os resultados relacionados à fonte desejada.
    """

    consulta = (
        f'"{cargo}" '
        f'"{local}" '
        f'site:{dominio}'
    )

    return consulta


def consultar_rss(cargo, local, site, dominio):
    """
    Consulta o Google News RSS.
    """

    consulta = montar_consulta(
        cargo,
        local,
        dominio,
    )

    url = (
        "https://news.google.com/rss/search?"
        + "q="
        + quote(consulta)
        + "&hl=pt-BR"
        + "&gl=BR"
        + "&ceid=BR:pt-419"
    )

    print(f"\n🔎 {site} | {cargo} | {local}")
    print(f"Consulta: {consulta}")

    try:

        resposta = session.get(
            url,
            timeout=20,
        )

        print(f"Status HTTP: {resposta.status_code}")

        if resposta.status_code != 200:
            print(
                "⚠️ RSS não retornou uma página válida."
            )
            return []

        feed = feedparser.parse(
            resposta.content
        )

        resultados = []

        for item in feed.entries:

            titulo = item.get(
                "title",
                "",
            ).strip()

            link = item.get(
                "link",
                "",
            ).strip()

            resumo = item.get(
                "summary",
                "",
            ).strip()

            data_publicacao = item.get(
                "published",
                "",
            ).strip()

            if not titulo or not link:
                continue

            resultados.append({
                "titulo": titulo,
                "site": site,
                "url": link,
                "localidade_busca": local,
                "snippet": resumo,
                "data_publicacao": data_publicacao,
                "cargo_busca": cargo,
                "data_coleta": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            })

        print(
            f"Resultados encontrados: "
            f"{len(resultados)}"
        )

        return resultados

    except requests.RequestException as erro:

        print(
            f"❌ Erro na consulta RSS: {erro}"
        )

        return []


# ============================================================
# COLETA
# ============================================================

print("\n")
print("=" * 70)
print("INICIANDO COLETA VIA RSS")
print("=" * 70)

todos_resultados = []

total_buscas = 0

for site in SITES:

    dominio = DOMINIOS.get(site)

    if not dominio:

        print(
            f"\n⚠️ Domínio não configurado: {site}"
        )

        continue

    # Nesta primeira versão usamos os cargos
    # mais importantes para evitar excesso de consultas.
    cargos_busca = CARGOS[:6]

    for cargo in cargos_busca:

        for local in LOCALIZACOES:

            total_buscas += 1

            resultados = consultar_rss(
                cargo,
                local,
                site,
                dominio,
            )

            todos_resultados.extend(
                resultados
            )

            # Pequena pausa entre consultas
            time.sleep(1)


# ============================================================
# REMOVER DUPLICIDADES
# ============================================================

print("\n")
print("=" * 70)
print("REMOVENDO DUPLICIDADES")
print("=" * 70)

resultados_unicos = []

urls_vistas = set()

for resultado in todos_resultados:

    url = resultado["url"]

    if url in urls_vistas:
        continue

    urls_vistas.add(url)

    resultados_unicos.append(
        resultado
    )


# ============================================================
# SALVAR CSV
# ============================================================

arquivo_csv = "vagas_encontradas.csv"

campos = [
    "titulo",
    "site",
    "url",
    "localidade_busca",
    "cargo_busca",
    "snippet",
    "data_publicacao",
    "data_coleta",
]

with open(
    arquivo_csv,
    "w",
    newline="",
    encoding="utf-8-sig",
) as arquivo:

    escritor = csv.DictWriter(
        arquivo,
        fieldnames=campos,
    )

    escritor.writeheader()

    escritor.writerows(
        resultados_unicos
    )


# ============================================================
# RESUMO
# ============================================================

print("\n")
print("=" * 70)
print("RESUMO DA EXECUÇÃO")
print("=" * 70)

print(
    f"- Sites configurados: {len(SITES)}"
)

print(
    f"- Localizações: {len(LOCALIZACOES)}"
)

print(
    f"- Cargos utilizados: {len(CARGOS[:6])}"
)

print(
    f"- Buscas realizadas: {total_buscas}"
)

print(
    f"- Resultados brutos: "
    f"{len(todos_resultados)}"
)

print(
    f"- Resultados únicos: "
    f"{len(resultados_unicos)}"
)

print(
    f"- Arquivo gerado: {arquivo_csv}"
)

print("\n")
print("=" * 70)
print("JOB HUNTER EXECUTADO COM SUCESSO")
print("=" * 70)
