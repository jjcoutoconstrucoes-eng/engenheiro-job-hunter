from datetime import datetime
from urllib.parse import quote, urlparse, parse_qs, unquote
import csv
import time
import requests
from bs4 import BeautifulSoup

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
# ETAPA 5 - COLETA DE RESULTADOS
# ============================================================

print("=" * 70)
print("JOB HUNTER - ENGENHEIRO ORÇAMENTISTA")
print("ETAPA 5 - COLETA DE RESULTADOS")
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
# SITES
# ============================================================

DOMINIOS = {
    "LinkedIn": "linkedin.com/jobs",
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
# CONFIGURAÇÃO HTTP
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# FUNÇÕES
# ============================================================

def limpar_url(url):
    """Remove redirecionamentos do Google quando possível."""

    if not url:
        return ""

    if url.startswith("/url?"):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        if "q" in params:
            return unquote(params["q"][0])

        if "url" in params:
            return unquote(params["url"][0])

    return url


def eh_resultado_valido(url):
    """Verifica se o link parece ser uma página externa válida."""

    if not url:
        return False

    url = limpar_url(url)

    if not url.startswith("http"):
        return False

    dominios_ignorados = [
        "google.com",
        "googleusercontent.com",
        "gstatic.com",
        "youtube.com",
    ]

    dominio = urlparse(url).netloc.lower()

    for ignorado in dominios_ignorados:
        if ignorado in dominio:
            return False

    return True


def extrair_resultados_google(html, site):
    """Extrai resultados básicos da página do Google."""

    soup = BeautifulSoup(html, "html.parser")

    resultados = []

    # Estrutura mais comum do Google
    blocos = soup.select("div.MjjYud")

    # Fallback para estruturas diferentes
    if not blocos:
        blocos = soup.select("div.g")

    for bloco in blocos:

        titulo_tag = bloco.find("h3")

        if not titulo_tag:
            continue

        titulo = titulo_tag.get_text(" ", strip=True)

        link_tag = titulo_tag.find_parent("a")

        if not link_tag:
            continue

        url = limpar_url(link_tag.get("href", ""))

        if not eh_resultado_valido(url):
            continue

        # Tenta encontrar descrição/snippet
        snippet = ""

        for seletor in [
            "div.VwiC3b",
            "div.IsZvec",
            "span.aCOpRe",
        ]:
            elemento = bloco.select_one(seletor)

            if elemento:
                snippet = elemento.get_text(" ", strip=True)
                break

        resultados.append({
            "titulo": titulo,
            "site": site,
            "url": url,
            "snippet": snippet,
        })

    return resultados


def consultar_google(site, dominio, local):
    """Executa uma pesquisa agrupando todos os cargos."""

    cargos_busca = " OR ".join(
        f'"{cargo}"' for cargo in CARGOS
    )

    pesquisa = (
        f"site:{dominio} ({cargos_busca}) "
        f'"{local}"'
    )

    url = (
        "https://www.google.com/search?"
        + "q="
        + quote(pesquisa)
        + "&num=10"
    )

    print(f"\n🔎 {site} | {local}")
    print(f"Consulta: {pesquisa}")

    try:
        resposta = session.get(
            url,
            timeout=20,
        )

        print(f"Status HTTP: {resposta.status_code}")

        if resposta.status_code != 200:
            print("⚠️ Google não retornou uma página válida.")
            return []

        resultados = extrair_resultados_google(
            resposta.text,
            site,
        )

        print(f"Resultados encontrados: {len(resultados)}")

        return resultados

    except requests.RequestException as erro:
        print(f"❌ Erro na consulta: {erro}")
        return []


# ============================================================
# COLETA
# ============================================================

print("\n")
print("=" * 70)
print("INICIANDO COLETA DE RESULTADOS")
print("=" * 70)

todos_resultados = []

total_buscas = 0

for site in SITES:

    dominio = DOMINIOS.get(site)

    if not dominio:
        print(f"\n⚠️ Domínio não configurado: {site}")
        continue

    for local in LOCALIZACOES:

        total_buscas += 1

        resultados = consultar_google(
            site,
            dominio,
            local,
        )

        for resultado in resultados:

            resultado["localidade_busca"] = local
            resultado["data_coleta"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            todos_resultados.append(resultado)

        # Pequena pausa para evitar excesso de requisições
        time.sleep(1.5)


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
    resultados_unicos.append(resultado)


# ============================================================
# SALVAR CSV
# ============================================================

arquivo_csv = "vagas_encontradas.csv"

campos = [
    "titulo",
    "site",
    "url",
    "localidade_busca",
    "snippet",
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

    escritor.writerows(resultados_unicos)


# ============================================================
# RESUMO
# ============================================================

print("\n")
print("=" * 70)
print("RESUMO DA EXECUÇÃO")
print("=" * 70)

print(f"- Sites configurados: {len(SITES)}")
print(f"- Localizações: {len(LOCALIZACOES)}")
print(f"- Buscas realizadas: {total_buscas}")
print(f"- Resultados brutos: {len(todos_resultados)}")
print(f"- Resultados únicos: {len(resultados_unicos)}")
print(f"- Arquivo gerado: {arquivo_csv}")

print("\n")
print("=" * 70)
print("JOB HUNTER EXECUTADO COM SUCESSO")
print("=" * 70)
