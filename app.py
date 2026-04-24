import math
import unicodedata
from io import BytesIO

import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white


st.set_page_config(page_title="Solarizando", layout="wide")


# =========================================================
# BASES INICIAIS
# =========================================================

IRRADIACAO_REFERENCIA = {
    ("PI", "Teresina"): {"jan": 4.93, "fev": 5.12, "mar": 5.14, "abr": 5.13, "mai": 5.23, "jun": 5.41, "jul": 5.69, "ago": 6.19, "set": 6.49, "out": 6.25, "nov": 5.97, "dez": 5.43},
    ("PI", "Parnaíba"): {"jan": 5.15, "fev": 5.27, "mar": 5.22, "abr": 5.14, "mai": 5.21, "jun": 5.36, "jul": 5.58, "ago": 5.95, "set": 6.08, "out": 5.96, "nov": 5.71, "dez": 5.39},
    ("PI", "Picos"): {"jan": 5.08, "fev": 5.20, "mar": 5.18, "abr": 5.16, "mai": 5.25, "jun": 5.44, "jul": 5.73, "ago": 6.14, "set": 6.38, "out": 6.16, "nov": 5.91, "dez": 5.47},
    ("MA", "São Luís"): {"jan": 5.02, "fev": 5.10, "mar": 5.00, "abr": 4.95, "mai": 5.05, "jun": 5.20, "jul": 5.45, "ago": 5.90, "set": 6.10, "out": 6.00, "nov": 5.70, "dez": 5.30},
    ("MA", "Imperatriz"): {"jan": 5.18, "fev": 5.24, "mar": 5.11, "abr": 5.02, "mai": 5.12, "jun": 5.31, "jul": 5.59, "ago": 6.02, "set": 6.22, "out": 6.07, "nov": 5.74, "dez": 5.36},
    ("MA", "Balsas"): {"jan": 5.22, "fev": 5.26, "mar": 5.12, "abr": 5.03, "mai": 5.14, "jun": 5.34, "jul": 5.63, "ago": 6.08, "set": 6.29, "out": 6.11, "nov": 5.78, "dez": 5.39},
    ("MA", "Caxias"): {"jan": 4.97, "fev": 5.08, "mar": 5.06, "abr": 5.04, "mai": 5.14, "jun": 5.31, "jul": 5.58, "ago": 6.05, "set": 6.29, "out": 6.08, "nov": 5.80, "dez": 5.34},
    ("MA", "Timon"): {"jan": 4.93, "fev": 5.12, "mar": 5.14, "abr": 5.13, "mai": 5.23, "jun": 5.41, "jul": 5.69, "ago": 6.19, "set": 6.49, "out": 6.25, "nov": 5.97, "dez": 5.43},
}

CIDADES_POR_UF = {
    "PI": [
        "Acauã", "Agricolândia", "Água Branca", "Alagoinha do Piauí", "Alegrete do Piauí",
        "Alto Longá", "Altos", "Alvorada do Gurguéia", "Amarante", "Angical do Piauí",
        "Anísio de Abreu", "Antônio Almeida", "Aroazes", "Aroeiras do Itaim", "Arraial",
        "Assunção do Piauí", "Avelino Lopes", "Baixa Grande do Ribeiro", "Barra d'Alcântara",
        "Barras", "Barreiras do Piauí", "Barro Duro", "Batalha", "Bela Vista do Piauí",
        "Belém do Piauí", "Beneditinos", "Bertolínia", "Betânia do Piauí", "Boa Hora",
        "Bocaina", "Bom Jesus", "Bom Princípio do Piauí", "Bonfim do Piauí", "Boqueirão do Piauí",
        "Brasileira", "Brejo do Piauí", "Buriti dos Lopes", "Buriti dos Montes", "Cabeceiras do Piauí",
        "Cajazeiras do Piauí", "Cajueiro da Praia", "Caldeirão Grande do Piauí", "Campinas do Piauí",
        "Campo Alegre do Fidalgo", "Campo Grande do Piauí", "Campo Largo do Piauí", "Campo Maior",
        "Canavieira", "Canto do Buriti", "Capitão de Campos", "Capitão Gervásio Oliveira",
        "Caracol", "Caraúbas do Piauí", "Caridade do Piauí", "Castelo do Piauí", "Caxingó",
        "Cocal", "Cocal de Telha", "Cocal dos Alves", "Coivaras", "Colônia do Gurguéia",
        "Colônia do Piauí", "Conceição do Canindé", "Coronel José Dias", "Corrente",
        "Cristalândia do Piauí", "Cristino Castro", "Curimatá", "Currais", "Curral Novo do Piauí",
        "Curralinhos", "Demerval Lobão", "Dirceu Arcoverde", "Dom Expedito Lopes",
        "Domingos Mourão", "Dom Inocêncio", "Elesbão Veloso", "Eliseu Martins",
        "Esperantina", "Fartura do Piauí", "Flores do Piauí", "Floresta do Piauí", "Floriano",
        "Francinópolis", "Francisco Ayres", "Francisco Macedo", "Francisco Santos",
        "Fronteiras", "Geminiano", "Gilbués", "Guadalupe", "Guaribas", "Hugo Napoleão",
        "Ilha Grande", "Inhuma", "Ipiranga do Piauí", "Isaías Coelho", "Itainópolis",
        "Itaueira", "Jacobina do Piauí", "Jaicós", "Jardim do Mulato", "Jatobá do Piauí",
        "Jerumenha", "João Costa", "Joaquim Pires", "Joca Marques", "José de Freitas",
        "Juazeiro do Piauí", "Júlio Borges", "Jurema", "Lagoa Alegre", "Lagoa de São Francisco",
        "Lagoa do Barro do Piauí", "Lagoa do Piauí", "Lagoa do Sítio", "Lagoinha do Piauí",
        "Landri Sales", "Luís Correia", "Luzilândia", "Madeiro", "Manoel Emídio", "Marcolândia",
        "Marcos Parente", "Massapê do Piauí", "Matias Olímpio", "Miguel Alves", "Miguel Leão",
        "Milton Brandão", "Monsenhor Gil", "Monsenhor Hipólito", "Monte Alegre do Piauí",
        "Morro Cabeça no Tempo", "Morro do Chapéu do Piauí", "Murici dos Portelas",
        "Nazaré do Piauí", "Nazária", "Nossa Senhora de Nazaré", "Nossa Senhora dos Remédios",
        "Novo Oriente do Piauí", "Novo Santo Antônio", "Oeiras", "Olho d'Água do Piauí",
        "Padre Marcos", "Paes Landim", "Pajeú do Piauí", "Palmeira do Piauí", "Palmeirais",
        "Paquetá", "Parnaguá", "Parnaíba", "Passagem Franca do Piauí", "Patos do Piauí",
        "Pau d'Arco do Piauí", "Paulistana", "Pavussu", "Pedro II", "Pedro Laurentino",
        "Picos", "Pimenteiras", "Pio IX", "Piracuruca", "Piripiri", "Porto", "Porto Alegre do Piauí",
        "Prata do Piauí", "Queimada Nova", "Redenção do Gurguéia", "Regeneração",
        "Riacho Frio", "Ribeira do Piauí", "Ribeiro Gonçalves", "Rio Grande do Piauí",
        "Santa Cruz do Piauí", "Santa Cruz dos Milagres", "Santa Filomena", "Santa Luz",
        "Santana do Piauí", "Santa Rosa do Piauí", "Santo Antônio de Lisboa",
        "Santo Antônio dos Milagres", "Santo Inácio do Piauí", "São Braz do Piauí",
        "São Félix do Piauí", "São Francisco de Assis do Piauí", "São Francisco do Piauí",
        "São Gonçalo do Gurguéia", "São Gonçalo do Piauí", "São João da Canabrava",
        "São João da Fronteira", "São João da Serra", "São João da Varjota", "São João do Arraial",
        "São João do Piauí", "São José do Divino", "São José do Peixe", "São José do Piauí",
        "São Julião", "São Lourenço do Piauí", "São Luis do Piauí", "São Miguel da Baixa Grande",
        "São Miguel do Fidalgo", "São Miguel do Tapuio", "São Pedro do Piauí",
        "São Raimundo Nonato", "Sebastião Barros", "Sebastião Leal", "Sigefredo Pacheco",
        "Simões", "Simplício Mendes", "Socorro do Piauí", "Sussuapara", "Tamboril do Piauí",
        "Tanque do Piauí", "Teresina", "União", "Uruçuí", "Valença do Piauí", "Várzea Branca",
        "Várzea Grande", "Vera Mendes", "Vila Nova do Piauí", "Wall Ferraz"
    ],
    "MA": [
        "Açailândia", "Afonso Cunha", "Água Doce do Maranhão", "Alcântara", "Aldeias Altas",
        "Altamira do Maranhão", "Alto Alegre do Maranhão", "Alto Alegre do Pindaré",
        "Alto Parnaíba", "Amapá do Maranhão", "Amarante do Maranhão", "Anajatuba", "Anapurus",
        "Apicum-Açu", "Araguanã", "Araioses", "Arame", "Arari", "Axixá", "Bacabal", "Bacabeira",
        "Bacuri", "Bacurituba", "Balsas", "Barão de Grajaú", "Barra do Corda", "Barreirinhas",
        "Bela Vista do Maranhão", "Belágua", "Benedito Leite", "Bequimão", "Bernardo do Mearim",
        "Boa Vista do Gurupi", "Bom Jardim", "Bom Jesus das Selvas", "Bom Lugar", "Brejo",
        "Brejo de Areia", "Buriti", "Buriti Bravo", "Buriticupu", "Buritirana", "Cachoeira Grande",
        "Cajapió", "Cajari", "Campestre do Maranhão", "Cândido Mendes", "Cantanhede",
        "Capinzal do Norte", "Carolina", "Carutapera", "Caxias", "Cedral", "Central do Maranhão",
        "Centro do Guilherme", "Centro Novo do Maranhão", "Chapadinha", "Cidelândia", "Codó",
        "Coelho Neto", "Colinas", "Conceição do Lago-Açu", "Coroatá", "Cururupu", "Davinópolis",
        "Dom Pedro", "Duque Bacelar", "Esperantinópolis", "Estreito", "Feira Nova do Maranhão",
        "Fernando Falcão", "Formosa da Serra Negra", "Fortaleza dos Nogueiras", "Fortuna",
        "Godofredo Viana", "Gonçalves Dias", "Governador Archer", "Governador Edison Lobão",
        "Governador Eugênio Barros", "Governador Luiz Rocha", "Governador Newton Bello",
        "Governador Nunes Freire", "Graça Aranha", "Grajaú", "Guimarães", "Humberto de Campos",
        "Icatu", "Igarapé do Meio", "Igarapé Grande", "Imperatriz", "Itaipava do Grajaú",
        "Itapecuru Mirim", "Itinga do Maranhão", "Jatobá", "Jenipapo dos Vieiras", "João Lisboa",
        "Joselândia", "Junco do Maranhão", "Lagoa do Mato", "Lago dos Rodrigues",
        "Lago Verde", "Lagoa Grande do Maranhão", "Lajeado Novo", "Lima Campos", "Loreto",
        "Luís Domingues", "Magalhães de Almeida", "Maracaçumé", "Marajá do Sena", "Maranhãozinho",
        "Mata Roma", "Matinha", "Matões", "Matões do Norte", "Milagres do Maranhão",
        "Mirador", "Miranda do Norte", "Mirinzal", "Monção", "Montes Altos", "Morros",
        "Nina Rodrigues", "Nova Colinas", "Nova Iorque", "Nova Olinda do Maranhão",
        "Olho d'Água das Cunhãs", "Olinda Nova do Maranhão", "Paço do Lumiar", "Palmeirândia",
        "Paraibano", "Parnarama", "Passagem Franca", "Pastos Bons", "Paulino Neves", "Paulo Ramos",
        "Pedreiras", "Pedro do Rosário", "Penalva", "Peri Mirim", "Peritoró", "Pindaré-Mirim",
        "Pinheiro", "Pio XII", "Pirapemas", "Poção de Pedras", "Porto Franco", "Porto Rico do Maranhão",
        "Presidente Dutra", "Presidente Juscelino", "Presidente Médici", "Presidente Sarney",
        "Presidente Vargas", "Primeira Cruz", "Raposa", "Riachão", "Ribamar Fiquene",
        "Rosário", "Sambaíba", "Santa Filomena do Maranhão", "Santa Helena", "Santa Inês",
        "Santa Luzia", "Santa Luzia do Paruá", "Santa Quitéria do Maranhão", "Santa Rita",
        "Santana do Maranhão", "Santo Amaro do Maranhão", "Santo Antônio dos Lopes",
        "São Benedito do Rio Preto", "São Bento", "São Bernardo", "São Domingos do Azeitão",
        "São Domingos do Maranhão", "São Félix de Balsas", "São Francisco do Brejão",
        "São Francisco do Maranhão", "São João Batista", "São João do Carú", "São João do Paraíso",
        "São João do Soter", "São João dos Patos", "São José de Ribamar", "São José dos Basílios",
        "São Luís", "São Luís Gonzaga do Maranhão", "São Mateus do Maranhão",
        "São Pedro da Água Branca", "São Pedro dos Crentes", "São Raimundo das Mangabeiras",
        "São Raimundo do Doca Bezerra", "São Roberto", "São Vicente Ferrer", "Satubinha",
        "Senador Alexandre Costa", "Senador La Rocque", "Serrano do Maranhão", "Sítio Novo",
        "Sucupira do Norte", "Sucupira do Riachão", "Tasso Fragoso", "Timbiras", "Timon",
        "Trizidela do Vale", "Tufilândia", "Tuntum", "Turiaçu", "Turilândia", "Tutóia", "Urbano Santos",
        "Vargem Grande", "Viana", "Vila Nova dos Martírios", "Vitória do Mearim", "Vitorino Freire",
        "Zé Doca"
    ]
}

CONCESSIONARIAS = [
    {"nome": "Equatorial Piauí", "uf": "PI", "te": 0.36, "tusd": 0.42, "fio_b": 0.24, "custo_disponibilidade_mono": 30, "custo_disponibilidade_bi": 50, "custo_disponibilidade_tri": 100},
    {"nome": "Equatorial Maranhão", "uf": "MA", "te": 0.35, "tusd": 0.41, "fio_b": 0.23, "custo_disponibilidade_mono": 30, "custo_disponibilidade_bi": 50, "custo_disponibilidade_tri": 100},
]

ICMS_POR_UF = {
    "PI": 0.22,
    "MA": 0.22,
}

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
MESES_LABEL = {
    "jan": "Jan", "fev": "Fev", "mar": "Mar", "abr": "Abr", "mai": "Mai", "jun": "Jun",
    "jul": "Jul", "ago": "Ago", "set": "Set", "out": "Out", "nov": "Nov", "dez": "Dez"
}

CATALOGO_MODULOS = {
    "530 W": {"potencia_wp": 530, "largura_mm": 1134, "altura_mm": 2094},
    "545 W": {"potencia_wp": 545, "largura_mm": 1134, "altura_mm": 2278},
    "585 W": {"potencia_wp": 585, "largura_mm": 1134, "altura_mm": 2278},
    "610 W": {"potencia_wp": 610, "largura_mm": 1134, "altura_mm": 2382},
    "630 W": {"potencia_wp": 630, "largura_mm": 1134, "altura_mm": 2382},
    "700 W": {"potencia_wp": 700, "largura_mm": 1303, "altura_mm": 2384},
}


# =========================================================
# CORES
# =========================================================

COR_PRINCIPAL_HEX = "#b32025"
COR_PRINCIPAL = HexColor(COR_PRINCIPAL_HEX)
COR_TEXTO = HexColor("#374151")
COR_CLARA = HexColor("#f8fafc")
COR_CAIXA = HexColor("#f1f5f9")
COR_LINHA = HexColor("#cbd5e1")
COR_VERMELHO = COR_PRINCIPAL_HEX
COR_VERMELHO_ESCURO = "#8f1d22"
COR_VERMELHO_CLARO = HexColor("#fff1f2")
COR_CINZA_TEXTO = HexColor("#6b7280")
COR_LARANJA_DESTAQUE = COR_PRINCIPAL


# =========================================================
# FUNÇÕES GERAIS
# =========================================================

def normalizar_texto(txt):
    if not txt:
        return ""
    txt = unicodedata.normalize("NFKD", str(txt))
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    return txt.strip().lower()


def obter_ufs():
    return sorted(CIDADES_POR_UF.keys())


def obter_cidades_por_uf(uf):
    return sorted(CIDADES_POR_UF.get(uf, []))


def obter_concessionarias_por_uf(uf):
    return sorted([item["nome"] for item in CONCESSIONARIAS if item["uf"] == uf])


def buscar_concessionaria(nome):
    for item in CONCESSIONARIAS:
        if item["nome"] == nome:
            return item
    return None


def custo_disponibilidade_por_fase(conc, fase):
    if fase == "Monofásico":
        return conc["custo_disponibilidade_mono"]
    if fase == "Bifásico":
        return conc["custo_disponibilidade_bi"]
    return conc["custo_disponibilidade_tri"]


def media_irradiacao_anual(irradiacao_cidade):
    return sum(irradiacao_cidade.values()) / 12


def calcular_potencia_necessaria_kwp(consumo_medio, irradiacao_media, perdas):
    fator = irradiacao_media * 30 * (1 - perdas)
    if fator <= 0:
        return 0
    return consumo_medio / fator


def calcular_numero_modulos(potencia_kwp, potencia_modulo_wp):
    if potencia_modulo_wp <= 0:
        return 0
    return math.ceil((potencia_kwp * 1000) / potencia_modulo_wp)


def calcular_geracao_mensal(num_modulos, potencia_modulo_wp, irradiacao_cidade, perdas):
    potencia_total_kwp = (num_modulos * potencia_modulo_wp) / 1000
    geracao = {}
    for mes in MESES:
        geracao[mes] = potencia_total_kwp * irradiacao_cidade[mes] * 30 * (1 - perdas)
    return geracao


def calcular_tarifa_cheia(te, tusd, icms):
    return (te + tusd) * (1 + icms)


def calcular_tarifa_credito(te, tusd, fio_b, percentual_fio_b, icms):
    base = te + tusd - (fio_b * percentual_fio_b)
    return max(base, 0) * (1 + icms)


def calcular_economia_mensal(consumo_medio, geracao_mensal, simultaneidade, tarifa_cheia, tarifa_credito, custo_disponibilidade):
    economia = {}
    for mes in MESES:
        geracao = geracao_mensal[mes]
        energia_instantanea = min(geracao * simultaneidade, consumo_medio)
        sobra_apos_instante = max(geracao - energia_instantanea, 0)
        consumo_restante = max(consumo_medio - energia_instantanea, 0)
        energia_creditada = min(sobra_apos_instante, consumo_restante)
        valor_economia = (energia_instantanea * tarifa_cheia) + (energia_creditada * tarifa_credito)
        economia[mes] = max(valor_economia - custo_disponibilidade, 0)
    return economia


def montar_df_resultado(consumo_medio, geracao_mensal, economia_mensal):
    linhas = []
    for mes in MESES:
        linhas.append({
            "Mês": MESES_LABEL[mes],
            "Consumo (kWh)": round(consumo_medio, 2),
            "Geração do sistema (kWh)": round(geracao_mensal[mes], 2),
            "Economia estimada (R$)": round(economia_mensal[mes], 2),
        })
    return pd.DataFrame(linhas)


def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_area_modulo_m2(largura_mm, altura_mm):
    return (largura_mm / 1000) * (altura_mm / 1000)


def texto_maiusculo_seguro(txt):
    return txt.strip().upper() if txt and str(txt).strip() else ""


def quebrar_linha_manual(texto, tamanho=70):
    if not texto:
        return [""]
    palavras = texto.split()
    linhas = []
    linha = ""
    for palavra in palavras:
        teste = f"{linha} {palavra}".strip()
        if len(teste) <= tamanho:
            linha = teste
        else:
            linhas.append(linha)
            linha = palavra
    if linha:
        linhas.append(linha)
    return linhas


def desenhar_texto_quebrado(c, texto, x, y, largura_max, font_name="Helvetica", font_size=11, cor=COR_TEXTO, espacamento=16):
    c.setFont(font_name, font_size)
    c.setFillColor(cor)

    palavras = texto.split()
    linha = ""
    linhas = []

    for palavra in palavras:
        teste = f"{linha} {palavra}".strip()
        if c.stringWidth(teste, font_name, font_size) <= largura_max:
            linha = teste
        else:
            linhas.append(linha)
            linha = palavra

    if linha:
        linhas.append(linha)

    y_atual = y
    for item in linhas:
        c.drawString(x, y_atual, item)
        y_atual -= espacamento

    return y_atual


def desenhar_secao_titulo(c, titulo, x, y):
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(COR_PRINCIPAL)
    c.drawString(x, y, titulo)
    return y - 16


def desenhar_paragrafo_pdf(c, texto, x, y, largura=495, tamanho=10, espacamento=14):
    return desenhar_texto_quebrado(
        c,
        texto,
        x,
        y,
        largura,
        font_name="Helvetica",
        font_size=tamanho,
        cor=COR_TEXTO,
        espacamento=espacamento,
    )


def linhas_produtos(dados):
    lista = []

    linha_inversor = (
        f"01 INVERSOR {texto_maiusculo_seguro(dados['marca_inversor'])} "
        f"{texto_maiusculo_seguro(dados['modelo_inversor'])} "
        f"{dados['potencia_inversor_kw']:.0f}KW "
        f"{texto_maiusculo_seguro(dados['tensao_inversor'])} "
        f"{texto_maiusculo_seguro(dados['observacao_inversor'])}"
    ).strip()
    lista.append(" ".join(linha_inversor.split()))

    linha_modulos = (
        f"{dados['num_modulos']:02d} MÓDULOS "
        f"{texto_maiusculo_seguro(dados['marca_modulo'])} "
        f"{dados['potencia_modulo_wp']}W "
        f"{texto_maiusculo_seguro(dados['tecnologia_modulo'])}"
    ).strip()
    lista.append(" ".join(linha_modulos.split()))

    if dados["produtos_extras"]:
        for item in dados["produtos_extras"]:
            lista.append(texto_maiusculo_seguro(item))

    lista.append(f"ESTRUTURA DE FIXAÇÃO PARA TELHADO {texto_maiusculo_seguro(dados['telhado'])}")
    lista.append("MÃO DE OBRA E MATERIAL DE INSTALAÇÃO")
    lista.append(f"PROJETO APROVADO NA {texto_maiusculo_seguro(dados['concessionaria'])}")

    return lista


def obter_irradiacao_cidade(uf, cidade):
    cidade_norm = normalizar_texto(cidade)

    mapa_pi = {
        "parnaiba": "Parnaíba",
        "luis correia": "Parnaíba",
        "ilha grande": "Parnaíba",
        "cajueiro da praia": "Parnaíba",
        "buriti dos lopes": "Parnaíba",
        "cocal": "Parnaíba",
        "cocal dos alves": "Parnaíba",
        "piracuruca": "Parnaíba",
        "piripiri": "Parnaíba",
        "barras": "Parnaíba",
        "esperantina": "Parnaíba",
        "batalha": "Parnaíba",
        "campo maior": "Teresina",
        "altos": "Teresina",
        "demerval lobao": "Teresina",
        "jose de freitas": "Teresina",
        "uniao": "Teresina",
        "agua branca": "Teresina",
        "amarante": "Teresina",
        "monsenhor gil": "Teresina",
        "nazaria": "Teresina",
        "teresina": "Teresina",
        "picos": "Picos",
        "geminiano": "Picos",
        "itainopolis": "Picos",
        "sussuapara": "Picos",
        "paqueta": "Picos",
        "francisco santos": "Picos",
        "jaicos": "Picos",
        "dom expedito lopes": "Picos",
        "inhuma": "Picos",
        "ipiranga do piaui": "Picos",
        "oeiras": "Picos",
        "floriano": "Picos",
        "bom jesus": "Picos",
        "urucui": "Picos",
        "corrente": "Picos",
        "sao raimundo nonato": "Picos",
        "paulistana": "Picos",
        "pio ix": "Picos",
        "fronteiras": "Picos",
        "simplicio mendes": "Picos",
        "valenca do piaui": "Picos",
    }

    mapa_ma = {
        "sao luis": "São Luís",
        "sao jose de ribamar": "São Luís",
        "paco do lumiar": "São Luís",
        "raposa": "São Luís",
        "rosario": "São Luís",
        "icatu": "São Luís",
        "morros": "São Luís",
        "humberto de campos": "São Luís",
        "barreirinhas": "São Luís",
        "chapadinha": "São Luís",
        "santa ines": "Caxias",
        "bacabal": "Caxias",
        "coroata": "Caxias",
        "timbiras": "Caxias",
        "codo": "Caxias",
        "coelho neto": "Caxias",
        "caxias": "Caxias",
        "timon": "Timon",
        "parnarama": "Timon",
        "matoes": "Timon",
        "imperatriz": "Imperatriz",
        "acailandia": "Imperatriz",
        "joao lisboa": "Imperatriz",
        "porto franco": "Imperatriz",
        "estreito": "Imperatriz",
        "amarante do maranhao": "Imperatriz",
        "balsas": "Balsas",
        "tasso fragoso": "Balsas",
        "alto parnaiba": "Balsas",
        "riachao": "Balsas",
        "sao raimundo das mangabeiras": "Balsas",
    }

    if uf == "PI":
        cidade_ref = mapa_pi.get(cidade_norm, "Teresina")
        return IRRADIACAO_REFERENCIA[("PI", cidade_ref)]

    if uf == "MA":
        cidade_ref = mapa_ma.get(cidade_norm, "São Luís")
        return IRRADIACAO_REFERENCIA[("MA", cidade_ref)]

    raise ValueError(f"UF não suportada: {uf}")


# =========================================================
# GRÁFICOS
# =========================================================

def gerar_imagem_grafico_geracao(df_geracao):
    fig, ax = plt.subplots(figsize=(8.0, 3.6))

    barras = ax.bar(
        df_geracao["Mês"],
        df_geracao["Geração (kWh)"],
        color=COR_VERMELHO,
        width=0.55
    )

    ax.set_title("Geração estimada por mês", fontsize=14, fontweight="bold", pad=10)
    ax.set_ylabel("kWh", fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.25)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")

    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)

    for barra in barras:
        altura = barra.get_height()
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura + 5,
            f"{int(altura)}",
            ha="center",
            va="bottom",
            fontsize=8,
            color=COR_VERMELHO_ESCURO,
            fontweight="bold"
        )

    buffer = BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buffer.seek(0)
    return buffer


# =========================================================
# FUNÇÕES DE DESIGN PDF
# =========================================================

def desenhar_fundo_padrao(c, largura, altura):
    c.setFillColor(COR_CLARA)
    c.rect(0, 0, largura, altura, fill=1, stroke=0)

    c.setFillColor(HexColor("#e2e8f0"))
    c.rect(0, altura - 75, largura, 75, fill=1, stroke=0)

    c.setFillColor(COR_PRINCIPAL)
    c.rect(0, altura - 75, 14, 75, fill=1, stroke=0)


def desenhar_capa_fallback(c, largura, altura, nome_cliente):
    c.setFillColor(HexColor("#eef2f7"))
    c.rect(0, 0, largura, altura, fill=1, stroke=0)

    c.setFillColor(COR_PRINCIPAL)
    c.rect(0, 0, largura, 180, fill=1, stroke=0)

    c.setFillColor(HexColor("#e5e7eb"))
    c.circle(470, 690, 180, fill=1, stroke=0)
    c.setFillColor(HexColor("#f3f4f6"))
    c.circle(520, 610, 110, fill=1, stroke=0)

    c.setFillColor(HexColor("#d1d5db"))
    c.rect(70, 285, 460, 220, fill=1, stroke=0)

    c.setFillColor(HexColor("#9ca3af"))
    c.rect(85, 300, 430, 8, fill=1, stroke=0)
    c.rect(85, 325, 410, 8, fill=1, stroke=0)
    c.rect(85, 350, 360, 8, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(white)
    c.drawString(60, 110, "PROPOSTA COMERCIAL")

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(530, 85, texto_maiusculo_seguro(nome_cliente) or "CLIENTE")


def desenhar_titulo_pagina(c, titulo):
    c.setFont("Helvetica-Bold", 19)
    c.setFillColor(COR_PRINCIPAL)
    c.drawString(45, 800, titulo)


def desenhar_rodape(c, pagina=None, total_paginas=None):
    c.setStrokeColor(COR_LINHA)
    c.line(40, 35, 555, 35)
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#64748b"))
    c.drawString(40, 20, "RPO Serviços - Proposta Comercial")

    if pagina is not None and total_paginas is not None:
        c.drawRightString(555, 20, f"Página {pagina} de {total_paginas}")


def desenhar_bloco_titulo_texto(c, titulo, linhas, x, y_inicial):
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(COR_PRINCIPAL)
    c.drawString(x, y_inicial, titulo)

    y = y_inicial - 18
    c.setFont("Helvetica", 10.5)
    c.setFillColor(COR_TEXTO)

    for linha in linhas:
        c.drawString(x, y, linha)
        y -= 16

    return y


def desenhar_pagina_producao(c, largura, altura, dados, img_geracao_buffer, pagina, total_paginas):
    fundo = COR_CLARA
    vermelho = COR_PRINCIPAL
    vermelho_claro = COR_VERMELHO_CLARO
    azul_texto = HexColor("#1f2937")
    cinza = COR_CINZA_TEXTO

    c.setFillColor(fundo)
    c.rect(0, 0, largura, altura, fill=1, stroke=0)

    c.setFillColor(vermelho)
    c.rect(0, altura - 80, largura, 80, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(white)
    c.drawString(40, 805, "Produção do sistema")

    c.setFillColor(white)
    c.roundRect(30, 60, largura - 60, altura - 130, 18, fill=1, stroke=0)

    c.setFillColor(vermelho_claro)
    c.roundRect(50, 690, 220, 68, 12, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(vermelho)
    c.drawString(65, 730, "Produção média")

    prod_media = f"{dados['geracao_media']:,.0f}".replace(",", ".")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(azul_texto)
    c.drawString(65, 705, f"{prod_media} kWh/mês")

    c.setFillColor(HexColor("#eff6ff"))
    c.roundRect(300, 690, 220, 68, 12, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(HexColor("#1d4ed8"))
    c.drawString(315, 730, "Geração anual")

    prod_anual = f"{dados['geracao_anual']:,.0f}".replace(",", ".")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(azul_texto)
    c.drawString(315, 705, f"{prod_anual} kWh/ano")

    c.setFont("Helvetica-Bold", 17)
    c.setFillColor(vermelho)
    c.drawCentredString(largura / 2, 650, "Geração mensal do sistema")

    c.setFont("Helvetica", 10)
    c.setFillColor(cinza)
    c.drawCentredString(largura / 2, 633, "Estimativa média de produção ao longo dos meses")

    c.drawImage(
        ImageReader(img_geracao_buffer),
        50,
        300,
        width=490,
        height=290,
        preserveAspectRatio=True,
        mask='auto'
    )

    c.setFont("Helvetica", 10.5)
    c.setFillColor(COR_TEXTO)
    c.drawString(50, 255, "A produção do sistema é estimada com base na radiação solar da região, perdas do sistema")
    c.drawString(50, 240, "e dimensionamento do gerador fotovoltaico informado nesta proposta.")

    c.drawString(50, 210, f"Potência estimada do sistema: {dados['potencia_kwp']:.2f} kWp")
    c.drawString(50, 174, f"Área estimada ocupada: {dados['area_total']:.2f} m²")

    desenhar_rodape(c, pagina, total_paginas)


# =========================================================
# PDF
# =========================================================

def gerar_pdf_proposta(dados, img_geracao_buffer):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    total_paginas = 8

    # PÁGINA 1 - CAPA
    try:
        capa = ImageReader("capa.png")
        c.drawImage(capa, 0, 0, width=largura, height=altura)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(COR_PRINCIPAL)
        c.drawRightString(530, 83, texto_maiusculo_seguro(dados["nome_cliente"]) or "CLIENTE")
    except Exception:
        desenhar_capa_fallback(c, largura, altura, dados["nome_cliente"])
    desenhar_rodape(c, 1, total_paginas)
    c.showPage()

    # PÁGINA 2 - SOBRE A EMPRESA
    desenhar_fundo_padrao(c, largura, altura)
    desenhar_titulo_pagina(c, "Sobre a empresa")

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(COR_PRINCIPAL)
    c.drawString(50, 770, "RPO SERVIÇOS")

    intro = (
        "A RPO Serviços atua na elaboração de projetos e execução de instalações elétricas, "
        "sistemas fotovoltaicos, consultorias em eficiência energética e manutenções."
    )
    desenhar_texto_quebrado(c, intro, 50, 744, 470, font_size=10.5, espacamento=16)

    y_blocos = 690

    y_blocos = desenhar_bloco_titulo_texto(
        c,
        "Missão",
        [
            "Executar serviços em instalações elétricas e sistemas fotovoltaicos com excelência,",
            "atendendo às normas de qualidade, segurança e meio ambiente."
        ],
        50,
        y_blocos
    )
    y_blocos -= 20

    y_blocos = desenhar_bloco_titulo_texto(
        c,
        "Visão",
        [
            "Ser referência na execução de serviços em instalações elétricas, com estrutura",
            "condizente para enfrentar novos desafios e superar as expectativas dos clientes."
        ],
        50,
        y_blocos
    )
    y_blocos -= 20

    y_blocos = desenhar_bloco_titulo_texto(
        c,
        "Valores",
        [
            "Ética e transparência;",
            "Satisfação do cliente;",
            "Qualidade;",
            "Valorização dos colaboradores;",
            "Sustentabilidade."
        ],
        50,
        y_blocos
    )
    y_blocos -= 20

    desenhar_bloco_titulo_texto(
        c,
        "Dados da empresa",
        [
            "RPO SERVICOS DE ENGENHARIA ELETRICA LTDA",
            "CNPJ: 46.981.138/0001-10",
            "Rua Rui Barbosa, 2207, Sala 01, Pirajá",
            "Teresina, PI",
            "Telefone: (86) 98822-3936",
            "Email: rpoengenhariapi@gmail.com",
        ],
        50,
        y_blocos
    )

    desenhar_rodape(c, 2, total_paginas)
    c.showPage()

        # PÁGINA 3 - FUNCIONAMENTO DO SISTEMA SOLAR
    desenhar_fundo_padrao(c, largura, altura)
    desenhar_titulo_pagina(c, "Funcionamento do sistema solar")

    c.setFont("Helvetica", 10.5)
    c.setFillColor(COR_TEXTO)
    c.drawString(50, 770, "Entenda de forma visual como a energia solar funciona no sistema fotovoltaico.")

    try:
        img_funcionamento = ImageReader("solar.png")
        c.drawImage(
            img_funcionamento,
            45,
            400,
            width=505,
            height=300,
            preserveAspectRatio=True,
            mask='auto'
        )
    except Exception:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(COR_PRINCIPAL)
        c.drawString(50, 720, "Imagem solar.png não encontrada")

    y = 370

    def titulo_funcionamento(txt, y):
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(COR_PRINCIPAL)
        c.drawString(50, y, txt)
        c.setStrokeColor(COR_PRINCIPAL)
        c.setLineWidth(1)
        c.line(50, y - 3, 545, y - 3)
        return y - 16

    y = titulo_funcionamento("1. PAINÉIS SOLARES", y)
    y = desenhar_paragrafo_pdf(
        c,
        "Captam a luz do sol e a transformam em energia elétrica (em corrente contínua).",
        50,
        y
    )
    y -= 10

    y = titulo_funcionamento("2. INVERSOR", y)
    y = desenhar_paragrafo_pdf(
        c,
        "O inversor converte a energia de corrente contínua (CC) dos painéis em corrente alternada (CA), que pode ser usada na casa.",
        50,
        y
    )
    y -= 10

    y = titulo_funcionamento("3. QUADRO DE LUZ", y)
    y = desenhar_paragrafo_pdf(
        c,
        "A energia já em corrente alternada é distribuída pelo quadro de luz para os circuitos da casa.",
        50,
        y
    )
    y -= 10

    y = titulo_funcionamento("4. CONSUMO NA RESIDÊNCIA", y)
    y = desenhar_paragrafo_pdf(
        c,
        "A energia produzida abastece os aparelhos e equipamentos da casa: lâmpadas, geladeira, máquina de lavar, chuveiro, tomadas, etc.",
        50,
        y
    )
    y -= 10

    y = titulo_funcionamento("5. REDE ELÉTRICA", y)
    y = desenhar_paragrafo_pdf(
        c,
        "Se a produção dos painéis for maior que o consumo, o excesso de energia é enviado para a rede elétrica.",
        50,
        y
    )
    y = desenhar_paragrafo_pdf(
        c,
        "Se for menor, a energia necessária é complementada pela rede.",
        50,
        y - 2
    )

    desenhar_rodape(c, 3, total_paginas)
    c.showPage()

    # PÁGINA 4 - PROCESSO DOS SERVIÇOS
    desenhar_fundo_padrao(c, largura, altura)
    desenhar_titulo_pagina(c, "Etapas do Projeto")

    y = 760

    y = desenhar_paragrafo_pdf(
        c,
        "A empresa oferece uma solução completa em sistemas de energia solar fotovoltaica, "
        "contemplando todas as etapas necessárias para a correta implantação e funcionamento do sistema.",
        50, y, largura=490
    )
    y -= 12

    y = desenhar_secao_titulo(c, "Vistoria Técnica", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "Realização de análise técnica no local, com o objetivo de verificar as condições de instalação, "
        "incluindo estrutura, área disponível e incidência solar.",
        50, y, largura=490
    )
    y -= 12

    y = desenhar_secao_titulo(c, "Projeto e Execução", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "Elaboração do projeto técnico por equipe de engenharia especializada, bem como a execução completa "
        "da instalação do sistema fotovoltaico, em conformidade com as normas técnicas e padrões de segurança.",
        50, y, largura=490
    )
    y -= 12

    y = desenhar_secao_titulo(c, "Homologação do Projeto", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "Responsabilidade pelo protocolo e acompanhamento do processo de aprovação junto à concessionária "
        "de energia, como por exemplo a Equatorial Energia.",
        50, y, largura=490
    )
    y -= 12

    y = desenhar_secao_titulo(c, "Ativação do Sistema", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "Após a conclusão da instalação, é realizada a solicitação junto à concessionária para os procedimentos "
        "necessários à conexão do sistema, incluindo a substituição do medidor convencional por medidor "
        "bidirecional e liberação para operação.",
        50, y, largura=490
    )
    y -= 12

    y = desenhar_secao_titulo(c, "Acompanhamento e Garantia", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "A empresa realizará o acompanhamento do funcionamento do sistema pelo período de 12 (doze) meses, "
        "correspondente à garantia da instalação, assegurando o correto desempenho e prestando suporte técnico "
        "quando necessário.",
        50, y, largura=490
    )

    desenhar_rodape(c, 4, total_paginas)
    c.showPage()

    # PÁGINA 5 - PRODUÇÃO
    desenhar_pagina_producao(c, largura, altura, dados, img_geracao_buffer, 5, total_paginas)
    c.showPage()

    # PÁGINA 6 - GARANTIAS E CONDIÇÕES
    desenhar_fundo_padrao(c, largura, altura)
    desenhar_titulo_pagina(c, "Garantias e condições")

    y = 760

    y = desenhar_secao_titulo(c, "Garantias do sistema", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "Os módulos fotovoltaicos foram projetados para oferecer desempenho duradouro, com garantia de "
        "performance de até 25 anos, assegurando no mínimo 80% da capacidade original de geração ao longo do período.",
        50, y, largura=490
    )
    y = desenhar_paragrafo_pdf(
        c,
        "Os módulos solares contam com 12 anos de garantia contra defeitos de fabricação, conforme as condições "
        "fornecidas pelo fabricante.",
        50, y - 4, largura=490
    )
    y = desenhar_paragrafo_pdf(
        c,
        "O inversor possui 10 anos de garantia contra defeitos de fabricação, proporcionando mais segurança e "
        "confiabilidade ao sistema instalado.",
        50, y - 4, largura=490
    )
    y -= 12

    y = desenhar_secao_titulo(c, "Prazo de instalação", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "A instalação do sistema poderá ser concluída em até 60 dias após a confirmação do pagamento, "
        "seguindo o planejamento técnico do projeto.",
        50, y, largura=490
    )
    y -= 12

    y = desenhar_secao_titulo(c, "Observações importantes", 50, y)
    y = desenhar_paragrafo_pdf(
        c,
        "• O prazo para análise e aprovação do projeto é de responsabilidade exclusiva da concessionária de energia.",
        50, y, largura=490
    )
    y = desenhar_paragrafo_pdf(
        c,
        "• A substituição do medidor por modelo bidirecional é realizada pela concessionária, mediante solicitação.",
        50, y - 2, largura=490
    )
    y = desenhar_paragrafo_pdf(
        c,
        "• O padrão de entrada da unidade consumidora deverá estar em conformidade com as exigências da "
        "concessionária, sendo condição indispensável para aprovação e conexão do sistema.",
        50, y - 2, largura=490
    )

    desenhar_rodape(c, 6, total_paginas)
    c.showPage()

    # PÁGINA 7 - PRODUTOS
    desenhar_fundo_padrao(c, largura, altura)
    desenhar_titulo_pagina(c, "Os produtos")

    c.setFont("Helvetica", 10.5)
    c.setFillColor(COR_TEXTO)
    c.drawString(50, 770, "Lista de produtos orçados nesta proposta comercial.")

    c.setFillColor(COR_CAIXA)
    c.roundRect(45, 710, 500, 30, 8, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COR_PRINCIPAL)
    c.drawString(55, 720, "Produto")
    c.drawString(230, 720, "Qtde")
    c.drawString(300, 720, "Valor unit.")
    c.drawString(430, 720, "Valor total")

    c.setFont("Helvetica", 10)
    c.setFillColor(COR_TEXTO)
    c.drawString(55, 680, f"KIT Fotovoltaico {dados['potencia_kwp']:.2f} kWp")
    c.drawString(230, 680, "1")
    c.drawString(300, 680, formatar_moeda(dados["valor_proposta"]))
    c.drawString(430, 680, formatar_moeda(dados["valor_proposta"]))

    produtos = linhas_produtos(dados)

    c.setFillColor(white)
    c.roundRect(45, 410, 500, 230, 10, fill=1, stroke=1)

    y = 620
    for item in produtos:
        for linha in quebrar_linha_manual(item, 62):
            c.setFont("Helvetica", 10)
            c.setFillColor(COR_TEXTO)
            c.drawString(58, y, linha)
            y -= 15
        y -= 4

    c.setFillColor(COR_CAIXA)
    c.roundRect(320, 320, 225, 78, 10, fill=1, stroke=0)
    c.setFont("Helvetica", 11)
    c.setFillColor(COR_TEXTO)
    c.drawString(338, 365, "Valor total da proposta:")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(COR_PRINCIPAL)
    c.drawString(338, 337, formatar_moeda(dados["valor_proposta"]))

    desenhar_rodape(c, 7, total_paginas)
    c.showPage()

    # PÁGINA 8 - ACEITE
    desenhar_fundo_padrao(c, largura, altura)
    desenhar_titulo_pagina(c, "Aceite da proposta")

    texto_aceite = (
        "Estando de acordo com os produtos, valores e termos relatados nesta proposta, "
        "as partes firmam o aceite comercial."
    )

    desenhar_texto_quebrado(
        c,
        texto_aceite,
        x=45,
        y=748,
        largura_max=500,
        font_name="Helvetica",
        font_size=10.5,
        cor=COR_TEXTO,
        espacamento=18,
    )

    c.setStrokeColor(HexColor("#2c2c2c"))
    c.setLineWidth(1)
    c.rect(35, 145, 495, 500, fill=0, stroke=1)

    campos = [
        "Nome do cliente:",
        "CPF / CNPJ:",
        "RG:",
        "Endereço:",
        "Cidade:",
        "UF:",
        "Email:",
        "Telefone:",
    ]

    y = 590
    for campo in campos:
        c.setFont("Helvetica", 10.5)
        c.setFillColor(COR_PRINCIPAL)
        c.drawString(50, y, campo)
        c.setStrokeColor(COR_LINHA)
        c.line(175, y - 2, 490, y - 2)
        y -= 38

    c.setStrokeColor(COR_LINHA)
    c.line(70, 95, 240, 95)
    c.line(325, 95, 495, 95)

    c.setFont("Helvetica", 10)
    c.setFillColor(COR_TEXTO)
    c.drawCentredString(155, 80, "RPO SERVIÇOS")

    nome_ass = dados["nome_cliente"] if dados["nome_cliente"] else "Cliente"
    cpf_ass = dados["cpf_cliente"] if dados["cpf_cliente"] else "CPF"

    c.drawCentredString(410, 80, nome_ass)
    c.drawCentredString(410, 66, cpf_ass)

    desenhar_rodape(c, 8, total_paginas)
    c.save()
    buffer.seek(0)
    return buffer


# =========================================================
# INTERFACE
# =========================================================

st.title("Solarizando ☀️")
st.caption("Sistema de proposta solar com PDF, cálculo automático e gráficos")

st.sidebar.header("Configurações")

ano_regra = st.sidebar.selectbox("Ano da regra do Fio B", [2024, 2025, 2026, 2027, 2028], index=2)
percentuais_padrao = {2024: 0.30, 2025: 0.45, 2026: 0.60, 2027: 0.75, 2028: 0.90}

percentual_fio_b = st.sidebar.number_input(
    "Percentual aplicado sobre o Fio B",
    min_value=0.0, max_value=1.0,
    value=float(percentuais_padrao[ano_regra]),
    step=0.05, format="%.2f"
)

perdas = st.sidebar.number_input(
    "Perdas do sistema",
    min_value=0.0, max_value=0.50,
    value=0.22, step=0.01, format="%.2f"
)

simultaneidade = st.sidebar.number_input(
    "Simultaneidade",
    min_value=0.0, max_value=1.0,
    value=0.60, step=0.05, format="%.2f"
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Dados do cliente")
    nome_cliente = st.text_input("Nome do cliente")
    cpf_cliente = st.text_input("CPF do cliente")
    endereco_cliente = st.text_input("Endereço do cliente")
    uf = st.selectbox("Estado", obter_ufs())
    cidade = st.selectbox("Cidade", obter_cidades_por_uf(uf))
    concessionaria_nome = st.selectbox("Concessionária", obter_concessionarias_por_uf(uf))
    fase = st.selectbox("Fase", ["Monofásico", "Bifásico", "Trifásico"])
    telhado = st.selectbox("Tipo de telhado", ["Cerâmico", "Metálico", "Fibrocimento", "Laje"])

with col2:
    st.subheader("Dados técnicos e comerciais")
    consumo_medio = st.number_input("Consumo médio mensal (kWh)", min_value=0.0, value=1000.0, step=50.0)

    st.markdown("**Módulos**")
    modulo_base = st.selectbox("Potência base do módulo", list(CATALOGO_MODULOS.keys()))
    dados_modulo_base = CATALOGO_MODULOS[modulo_base]

    marca_modulo = st.text_input("Marca do módulo", value="JETION")
    tecnologia_modulo = st.text_input("Tecnologia do módulo", value="BIFACIAL N-TYPE HJT")

    potencia_modulo_wp = dados_modulo_base["potencia_wp"]
    largura_mm = dados_modulo_base["largura_mm"]
    altura_mm = dados_modulo_base["altura_mm"]
    area_por_modulo = calcular_area_modulo_m2(largura_mm, altura_mm)

    st.write(f"**Potência do módulo:** {potencia_modulo_wp} Wp")
    st.write(f"**Dimensões do módulo:** {altura_mm} x {largura_mm} mm")
    st.write(f"**Área útil por módulo:** {area_por_modulo:.2f} m²")

    st.markdown("---")
    st.markdown("**Inversor**")

    marca_inversor = st.text_input("Marca do inversor", value="SOLPLANET")
    modelo_inversor = st.text_input("Modelo do inversor", value="ASW5000-S-G2")
    potencia_inversor_kw = st.number_input("Potência do inversor (kW)", min_value=0.0, value=5.0, step=0.5)
    tensao_inversor = st.text_input("Tensão do inversor", value="220V")
    observacao_inversor = st.text_input("Observação do inversor", value="AFCI")

    st.markdown("---")

    produtos_extras_texto = st.text_area(
        "Produtos extras (1 por linha)",
        value="01 STRINGBOX CLAMPER SOLAR",
        height=120,
    )

    valor_proposta = st.number_input("Valor da proposta (R$)", min_value=0.0, value=17500.0, step=500.0)


if st.button("Calcular proposta", use_container_width=True):
    irradiacao_cidade = obter_irradiacao_cidade(uf, cidade)
    irradiacao_media = media_irradiacao_anual(irradiacao_cidade)

    conc = buscar_concessionaria(concessionaria_nome)
    icms = ICMS_POR_UF.get(uf, 0.18)

    te = conc["te"]
    tusd = conc["tusd"]
    fio_b = conc["fio_b"]
    custo_disponibilidade = custo_disponibilidade_por_fase(conc, fase)

    tarifa_cheia = calcular_tarifa_cheia(te, tusd, icms)
    tarifa_credito = calcular_tarifa_credito(te, tusd, fio_b, percentual_fio_b, icms)

    potencia_kwp = calcular_potencia_necessaria_kwp(consumo_medio, irradiacao_media, perdas)
    num_modulos = calcular_numero_modulos(potencia_kwp, potencia_modulo_wp)
    area_total = num_modulos * area_por_modulo

    geracao_mensal = calcular_geracao_mensal(num_modulos, potencia_modulo_wp, irradiacao_cidade, perdas)
    geracao_media = sum(geracao_mensal.values()) / 12
    geracao_anual = sum(geracao_mensal.values())

    economia_mensal = calcular_economia_mensal(
        consumo_medio,
        geracao_mensal,
        simultaneidade,
        tarifa_cheia,
        tarifa_credito,
        custo_disponibilidade,
    )

    economia_media_mensal = sum(economia_mensal.values()) / 12
    economia_anual = economia_media_mensal * 12

    produtos_extras = [linha.strip() for linha in produtos_extras_texto.splitlines() if linha.strip()]

    st.success("Proposta calculada com sucesso!")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Potência estimada", f"{potencia_kwp:.2f} kWp")
    m2.metric("Módulos", f"{num_modulos} un.")
    m3.metric("Geração média", f"{geracao_media:.0f} kWh/mês")
    m4.metric("Economia média", formatar_moeda(economia_media_mensal))

    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Economia anual", formatar_moeda(economia_anual))
    n2.metric("Área estimada", f"{area_total:.2f} m²")
    n3.metric("Irradiação média", f"{irradiacao_media:.2f} kWh/m².dia")
    n4.metric("Tarifa cheia", f"{formatar_moeda(tarifa_cheia)}/kWh")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Resumo técnico")
        st.write(f"**Cliente:** {nome_cliente if nome_cliente else '-'}")
        st.write(f"**CPF:** {cpf_cliente if cpf_cliente else '-'}")
        st.write(f"**Endereço:** {endereco_cliente if endereco_cliente else '-'}")
        st.write(f"**Cidade/UF:** {cidade}/{uf}")
        st.write(f"**Concessionária:** {concessionaria_nome}")
        st.write(f"**Telhado:** {telhado}")
        st.write(f"**Fase:** {fase}")
        st.write(f"**Marca do módulo:** {marca_modulo}")
        st.write(f"**Potência do módulo:** {potencia_modulo_wp} Wp")
        st.write(f"**Tecnologia do módulo:** {tecnologia_modulo}")
        st.write(f"**Área por módulo:** {area_por_modulo:.2f} m²")
        st.write(f"**Marca do inversor:** {marca_inversor}")
        st.write(f"**Modelo do inversor:** {modelo_inversor}")
        st.write(f"**Potência do inversor:** {potencia_inversor_kw:.2f} kW")

    with c2:
        st.subheader("Resumo tarifário")
        st.write(f"**TE:** {formatar_moeda(te)} / kWh")
        st.write(f"**TUSD:** {formatar_moeda(tusd)} / kWh")
        st.write(f"**Fio B base:** {formatar_moeda(fio_b)} / kWh")
        st.write(f"**Percentual Fio B aplicado:** {percentual_fio_b:.0%}")
        st.write(f"**ICMS estimado:** {icms:.0%}")
        st.write(f"**Tarifa cheia estimada:** {formatar_moeda(tarifa_cheia)} / kWh")
        st.write(f"**Tarifa crédito estimada:** {formatar_moeda(tarifa_credito)} / kWh")
        st.write(f"**Custo de disponibilidade:** {custo_disponibilidade} kWh")

    st.divider()

    df_resultado = montar_df_resultado(consumo_medio, geracao_mensal, economia_mensal)
    st.subheader("Estimativa mês a mês")
    st.dataframe(df_resultado, use_container_width=True)

    df_chart = df_resultado.melt(
        id_vars="Mês",
        value_vars=["Consumo (kWh)", "Geração do sistema (kWh)"],
        var_name="Tipo",
        value_name="kWh",
    )

    grafico_barras = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X("Mês:N", sort=list(MESES_LABEL.values())),
        y=alt.Y("kWh:Q", title="kWh"),
        color=alt.Color("Tipo:N", title="Legenda"),
        xOffset="Tipo:N",
        tooltip=["Mês", "Tipo", "kWh"],
    ).properties(
        title="Estimativa de Consumo vs. Geração mês a mês",
        height=360,
    )

    st.altair_chart(grafico_barras, use_container_width=True)

    df_geracao = pd.DataFrame({
        "Mês": [MESES_LABEL[m] for m in MESES],
        "Geração (kWh)": [round(geracao_mensal[m], 2) for m in MESES],
    })

    grafico_geracao = alt.Chart(df_geracao).mark_bar(
        color=COR_VERMELHO,
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        x=alt.X("Mês:N", sort=list(MESES_LABEL.values())),
        y=alt.Y("Geração (kWh):Q", title="Geração (kWh)"),
        tooltip=["Mês", "Geração (kWh)"],
    ).properties(
        title="Geração estimada por mês",
        height=360,
    )

    st.altair_chart(grafico_geracao, use_container_width=True)

    img_geracao_buffer = gerar_imagem_grafico_geracao(df_geracao)

    dados_pdf = {
        "nome_cliente": nome_cliente,
        "cpf_cliente": cpf_cliente,
        "endereco_cliente": endereco_cliente,
        "cidade": cidade,
        "uf": uf,
        "concessionaria": concessionaria_nome,
        "telhado": telhado,
        "fase": fase,
        "marca_modulo": marca_modulo,
        "potencia_modulo_wp": potencia_modulo_wp,
        "tecnologia_modulo": tecnologia_modulo,
        "marca_inversor": marca_inversor,
        "modelo_inversor": modelo_inversor,
        "potencia_inversor_kw": potencia_inversor_kw,
        "tensao_inversor": tensao_inversor,
        "observacao_inversor": observacao_inversor,
        "produtos_extras": produtos_extras,
        "irradiacao_media": irradiacao_media,
        "potencia_kwp": potencia_kwp,
        "num_modulos": num_modulos,
        "geracao_media": geracao_media,
        "geracao_anual": geracao_anual,
        "area_total": area_total,
        "valor_proposta": valor_proposta,
    }

    pdf_buffer = gerar_pdf_proposta(dados_pdf, img_geracao_buffer)
    nome_arquivo = nome_cliente.strip().replace(" ", "_").lower() if nome_cliente else "solar"

    st.download_button(
        label="📄 Baixar proposta em PDF",
        data=pdf_buffer,
        file_name=f"proposta_{nome_arquivo}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

else:
    st.info("Preencha os campos e clique em **Calcular proposta**.")