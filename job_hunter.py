from datetime import datetime
from urllib.parse import quote

from config import (
    CARGOS,
    LOCALIZACOES,
    SALARIO_MINIMO,
    SALARIO_ALVO,
    REGIMES,
    NIVEL,
    SITES,
)


print("=" * 60)
print("JOB HUNTER - ENGENHEIRO ORÇAMENTISTA")
print("=" * 60)

print(f"\nRobô executado em: {datetime.now()}")

print("\nPERFIL DE BUSCA")
print("-" * 60)

for cargo in CARGOS:
    print(f"- {cargo}")

print("\nLOCALIZAÇÕES")
print("-" * 60)

for local in LOCALIZACOES:
    print(f"- {local}")

print("\nCONDIÇÕES")
print("-" * 60)

print(f"- Salário mínimo para considerar: R$ {SALARIO_MINIMO:,.0f}")
print(f"- Salário alvo: R$ {SALARIO_ALVO:,.0f}")
print(f"- Regimes: {', '.join(REGIMES)}")
print(f"- Níveis: {', '.join(NIVEL)}")


# Sites e respectivos domínios
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


print("\n")
print("=" * 60)
print("LINKS DE BUSCA")
print("=" * 60)


# Vamos criar pesquisas para cada combinação de cargo/local
for site in SITES:

    dominio = DOMINIOS.get(site)

    if not dominio:
        continue

    print(f"\n🌐 {site}")
    print("-" * 60)

    # Usamos os cargos principais para não gerar centenas de links
    for cargo in CARGOS[:5]:

        for local in LOCALIZACOES[:3]:

            pesquisa = f'"{cargo}" "{local}"'

            url = (
                "https://www.google.com/search?q="
                + quote(f"site:{dominio} {pesquisa}")
            )

            print(f"\n{cargo} - {local}")
            print(url)


print("\n")
print("=" * 60)
print("JOB HUNTER EXECUTADO COM SUCESSO")
print("=" * 60)
