from datetime import datetime
from urllib.parse import quote
import csv
import re
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
# ETAPA 7 - FILTRAGEM E PONTUAÇÃO
# ============================================================

print("=" * 70)
print("JOB HUNTER - ENGENHEIRO ORÇAMENTISTA")
print("ETAPA 7 - FILTRAGEM E PONTUAÇÃO")
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
# FUNÇÕES DE COLETA
# ============================================================

def montar_consulta(cargo, local, dominio):
    """
    Monta a consulta para o Google News RSS.
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
# NORMALIZAÇÃO DE TEXTO
# ============================================================

def normalizar_texto(texto):
    """
    Converte o texto para uma forma mais fácil de analisar.
    """

    texto = str(texto or "").lower()

    substituicoes = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "í": "i",
        "ì": "i",
        "î": "i",
        "ï": "i",
        "ó": "o",
        "ò": "o",
        "õ": "o",
        "ô": "o",
        "ö": "o",
        "ú": "u",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }

    for origem, destino in substituicoes.items():
        texto = texto.replace(
            origem,
            destino,
        )

    return texto


# ============================================================
# PALAVRAS-CHAVE
# ============================================================

PALAVRAS_POSITIVAS = [
    "engenheiro orcamentista",
    "engenheiro de custos",
    "engenheiro de planejamento",
    "orcamentista de obras",
    "analista de orcamento",
    "analista de custos",
    "engenheiro civil",
    "planejamento e controle de obras",
    "orcamento de obras",
    "custos de obras",
    "planejamento de obras",
    "controle de obras",
    "gestao de obras",
    "construcao civil",
    "engenharia civil",
    "bim",
    "ms project",
    "project",
    "revit",
    "autocad",
    "sienge",
    "mega",
    "totvs",
]


PALAVRAS_NEGATIVAS = [
    "estagio",
    "estagiario",
    "estagiaria",
    "jovem aprendiz",
    "aprendiz",
    "assistente administrativo",
    "auxiliar administrativo",
    "vendedor",
    "vendedora",
    "corretor de imoveis",
    "corretora de imoveis",
    "eletricista",
    "encanador",
    "pedreiro",
    "servente",
    "motorista",
    "tecnico de enfermagem",
    "enfermeiro",
    "enfermeira",
    "professor",
    "professora",
    "arquiteto junior",
    "arquiteta junior",
]


PALAVRAS_NIVEL = [
    "pleno",
    "senior",
    "sr",
    "especialista",
    "coordenador",
    "coordenadora",
    "gerente",
]


PALAVRAS_CLT = [
    "clt",
    "efetivo",
    "efetiva",
    "carteira assinada",
]


PALAVRAS_PJ = [
    "pj",
    "pessoa juridica",
    "prestador de servicos",
    "prestacao de servicos",
]


PALAVRAS_LOCAL = {
    "Rio de Janeiro": [
        "rio de janeiro",
        "rj",
    ],
    "Niterói": [
        "niteroi",
    ],
    "São Gonçalo": [
        "sao goncalo",
    ],
}


# ============================================================
# SALÁRIO
# ============================================================

def extrair_salarios(texto):
    """
    Tenta encontrar valores salariais no título/snippet.
    """

    texto = normalizar_texto(texto)

    padroes = [
        r"r\$\s*([\d\.\,]+)",
        r"salario\s*(?:de|:)?\s*r?\$?\s*([\d\.\,]+)",
        r"remuneracao\s*(?:de|:)?\s*r?\$?\s*([\d\.\,]+)",
    ]

    valores = []

    for padrao in padroes:

        encontrados = re.findall(
            padrao,
            texto,
            flags=re.IGNORECASE,
        )

        for valor in encontrados:

            valor = valor.replace(
                ".",
                "",
            )

            valor = valor.replace(
                ",",
                ".",
            )

            try:

                numero = float(valor)

                if numero >= 1000:
                    valores.append(
                        numero
                    )

            except ValueError:
                continue

    return valores


# ============================================================
# ANÁLISE DE REGIME
# ============================================================

def identificar_regime(texto):

    texto = normalizar_texto(texto)

    encontrou_clt = any(
        palavra in texto
        for palavra in PALAVRAS_CLT
    )

    encontrou_pj = any(
        palavra in texto
        for palavra in PALAVRAS_PJ
    )

    if encontrou_clt and encontrou_pj:
        return "CLT/PJ"

    if encontrou_clt:
        return "CLT"

    if encontrou_pj:
        return "PJ"

    return "Não informado"


# ============================================================
# ANÁLISE DE NÍVEL
# ============================================================

def identificar_nivel(texto):

    texto = normalizar_texto(texto)

    encontrados = []

    for palavra in PALAVRAS_NIVEL:

        if palavra in texto:
            encontrados.append(
                palavra
            )

    if not encontrados:
        return "Não informado"

    if (
        "senior" in encontrados
        or "sr" in encontrados
    ):
        return "Sênior"

    if "pleno" in encontrados:
        return "Pleno"

    return encontrados[0].title()


# ============================================================
# ANÁLISE DE LOCALIZAÇÃO
# ============================================================

def identificar_local(texto, local_busca):

    texto = normalizar_texto(texto)

    locais_encontrados = []

    for local, palavras in PALAVRAS_LOCAL.items():

        for palavra in palavras:

            if palavra in texto:

                if local not in locais_encontrados:
                    locais_encontrados.append(
                        local
                    )

                break

    if locais_encontrados:
        return ", ".join(
            locais_encontrados
        )

    return local_busca


# ============================================================
# SCORE
# ============================================================

def calcular_score(resultado):

    titulo = normalizar_texto(
        resultado["titulo"]
    )

    snippet = normalizar_texto(
        resultado["snippet"]
    )

    texto = f"{titulo} {snippet}"

    score = 0

    motivos = []

    # --------------------------------------------------------
    # CARGO
    # --------------------------------------------------------

    cargos_fortes = [
        "engenheiro orcamentista",
        "engenheiro de custos",
        "engenheiro de planejamento",
        "orcamentista de obras",
        "analista de orcamento",
        "analista de custos",
    ]

    cargo_forte_encontrado = False

    for palavra in cargos_fortes:

        if palavra in texto:

            score += 30
            motivos.append(
                f"Cargo compatível: {palavra}"
            )

            cargo_forte_encontrado = True
            break

    if not cargo_forte_encontrado:

        if "engenheiro civil" in texto:
            score += 18
            motivos.append(
                "Engenheiro Civil"
            )

    # --------------------------------------------------------
    # ÁREA
    # --------------------------------------------------------

    areas = [
        "orcamento",
        "orcamentista",
        "custos",
        "planejamento",
        "controle de obras",
        "construcao civil",
        "engenharia civil",
        "gestao de obras",
    ]

    pontos_area = 0

    for palavra in areas:

        if palavra in texto:
            pontos_area += 4

    pontos_area = min(
        pontos_area,
        20,
    )

    if pontos_area > 0:

        score += pontos_area

        motivos.append(
            f"Área de atuação compatível (+{pontos_area})"
        )

    # --------------------------------------------------------
    # NÍVEL
    # --------------------------------------------------------

    nivel = identificar_nivel(
        texto
    )

    if nivel == "Sênior":

        score += 15

        motivos.append(
            "Nível Sênior"
        )

    elif nivel == "Pleno":

        score += 12

        motivos.append(
            "Nível Pleno"
        )

    elif nivel in [
        "Especialista",
        "Coordenador",
        "Gerente",
    ]:

        score += 8

        motivos.append(
            f"Nível {nivel}"
        )

    # --------------------------------------------------------
    # REGIME
    # --------------------------------------------------------

    regime = identificar_regime(
        texto
    )

    if regime in [
        "CLT",
        "PJ",
        "CLT/PJ",
    ]:

        score += 5

        motivos.append(
            f"Regime identificado: {regime}"
        )

    # --------------------------------------------------------
    # LOCALIZAÇÃO
    # --------------------------------------------------------

    local = identificar_local(
        texto,
        resultado["localidade_busca"],
    )

    if local in LOCALIZACOES:

        score += 5

        motivos.append(
            f"Local compatível: {local}"
        )

    # --------------------------------------------------------
    # SALÁRIO
    # --------------------------------------------------------

    salarios = extrair_salarios(
        texto
    )

    salario_detectado = ""

    if salarios:

        salario_maximo = max(
            salarios
        )

        salario_detectado = (
            f"R$ {salario_maximo:,.0f}"
        )

        if salario_maximo >= SALARIO_ALVO:

            score += 15

            motivos.append(
                "Salário igual ou superior ao alvo"
            )

        elif salario_maximo >= SALARIO_MINIMO:

            score += 10

            motivos.append(
                "Salário igual ou superior ao mínimo"
            )

        else:

            score += 2

            motivos.append(
                "Salário abaixo do mínimo"
            )

    # --------------------------------------------------------
    # PALAVRAS POSITIVAS ADICIONAIS
    # --------------------------------------------------------

    palavras_encontradas = 0

    for palavra in PALAVRAS_POSITIVAS:

        if palavra in texto:
            palavras_encontradas += 1

    bonus = min(
        palavras_encontradas * 1,
        5,
    )

    score += bonus

    # --------------------------------------------------------
    # PENALIDADES
    # --------------------------------------------------------

    palavras_negativas_encontradas = []

    for palavra in PALAVRAS_NEGATIVAS:

        if palavra in texto:

            palavras_negativas_encontradas.append(
                palavra
            )

    penalidade = min(
        len(palavras_negativas_encontradas) * 20,
        60,
    )

    if penalidade > 0:

        score -= penalidade

        motivos.append(
            "Termos incompatíveis encontrados"
        )

    # --------------------------------------------------------
    # LIMITES
    # --------------------------------------------------------

    score = max(
        0,
        min(
            score,
            100,
        ),
    )

    # --------------------------------------------------------
    # CLASSIFICAÇÃO
    # --------------------------------------------------------

    if score >= 75:
        classificacao = "ALTA PRIORIDADE"

    elif score >= 55:
        classificacao = "BOA OPORTUNIDADE"

    elif score >= 35:
        classificacao = "BAIXA PRIORIDADE"

    else:
        classificacao = "DESCARTAR"

    return {
        "score": score,
        "classificacao": classificacao,
        "regime": regime,
        "nivel": nivel,
        "localizacao_identificada": local,
        "salario_detectado": salario_detectado,
        "motivos": " | ".join(motivos),
    }


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

    # Mantemos os 6 cargos da Etapa 6.
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
# SALVAR ARQUIVO ORIGINAL
# ============================================================

arquivo_original = (
    "vagas_encontradas.csv"
)

campos_originais = [
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
    arquivo_original,
    "w",
    newline="",
    encoding="utf-8-sig",
) as arquivo:

    escritor = csv.DictWriter(
        arquivo,
        fieldnames=campos_originais,
    )

    escritor.writeheader()

    escritor.writerows(
        resultados_unicos
    )


# ============================================================
# ETAPA 7 - FILTRAGEM
# ============================================================

print("\n")
print("=" * 70)
print("ETAPA 7 - ANALISANDO E PONTUANDO VAGAS")
print("=" * 70)

vagas_analisadas = []

for resultado in resultados_unicos:

    analise = calcular_score(
        resultado
    )

    vaga = resultado.copy()

    vaga.update(
        analise
    )

    vagas_analisadas.append(
        vaga
    )


# ============================================================
# ORDENAR POR SCORE
# ============================================================

vagas_analisadas.sort(
    key=lambda x: x["score"],
    reverse=True,
)


# ============================================================
# CONTADORES
# ============================================================

alta_prioridade = 0
boa_oportunidade = 0
baixa_prioridade = 0
descartar = 0

for vaga in vagas_analisadas:

    classificacao = vaga[
        "classificacao"
    ]

    if classificacao == "ALTA PRIORIDADE":
        alta_prioridade += 1

    elif classificacao == "BOA OPORTUNIDADE":
        boa_oportunidade += 1

    elif classificacao == "BAIXA PRIORIDADE":
        baixa_prioridade += 1

    elif classificacao == "DESCARTAR":
        descartar += 1


# ============================================================
# SALVAR RESULTADO FILTRADO
# ============================================================

arquivo_filtrado = (
    "vagas_filtradas.csv"
)

campos_filtrados = [
    "score",
    "classificacao",
    "titulo",
    "site",
    "url",
    "localidade_busca",
    "localizacao_identificada",
    "cargo_busca",
    "nivel",
    "regime",
    "salario_detectado",
    "snippet",
    "data_publicacao",
    "data_coleta",
    "motivos",
]

with open(
    arquivo_filtrado,
    "w",
    newline="",
    encoding="utf-8-sig",
) as arquivo:

    escritor = csv.DictWriter(
        arquivo,
        fieldnames=campos_filtrados,
    )

    escritor.writeheader()

    escritor.writerows(
        vagas_analisadas
    )


# ============================================================
# MOSTRAR TOP 20
# ============================================================

print("\n")
print("=" * 70)
print("TOP 20 VAGAS")
print("=" * 70)

for indice, vaga in enumerate(
    vagas_analisadas[:20],
    start=1,
):

    print(
        f"\n{indice}. "
        f"[{vaga['score']}/100] "
        f"{vaga['classificacao']}"
    )

    print(
        f"   {vaga['titulo']}"
    )

    print(
        f"   Site: {vaga['site']}"
    )

    print(
        f"   Local: "
        f"{vaga['localizacao_identificada']}"
    )

    print(
        f"   Nível: "
        f"{vaga['nivel']}"
    )

    print(
        f"   Regime: "
        f"{vaga['regime']}"
    )

    if vaga["salario_detectado"]:

        print(
            f"   Salário: "
            f"{vaga['salario_detectado']}"
        )

    print(
        f"   URL: {vaga['url']}"
    )


# ============================================================
# RESUMO
# ============================================================

print("\n")
print("=" * 70)
print("RESUMO DA EXECUÇÃO")
print("=" * 70)

print(
    f"- Sites configurados: "
    f"{len(SITES)}"
)

print(
    f"- Localizações: "
    f"{len(LOCALIZACOES)}"
)

print(
    f"- Cargos utilizados: "
    f"{len(CARGOS[:6])}"
)

print(
    f"- Buscas realizadas: "
    f"{total_buscas}"
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
    f"- Alta prioridade: "
    f"{alta_prioridade}"
)

print(
    f"- Boa oportunidade: "
    f"{boa_oportunidade}"
)

print(
    f"- Baixa prioridade: "
    f"{baixa_prioridade}"
)

print(
    f"- Descartar: "
    f"{descartar}"
)

print(
    f"- Arquivo original: "
    f"{arquivo_original}"
)

print(
    f"- Arquivo filtrado: "
    f"{arquivo_filtrado}"
)

print("\n")
print("=" * 70)
print("JOB HUNTER - ETAPA 7 CONCLUÍDA")
print("=" * 70)
