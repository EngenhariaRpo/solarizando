import math
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

IRRADIACAO_CIDADES = {
    ("PI", "Teresina"): {"jan": 4.93, "fev": 5.12, "mar": 5.14, "abr": 5.13, "mai": 5.23, "jun": 5.41, "jul": 5.69, "ago": 6.19, "set": 6.49, "out": 6.25, "nov": 5.97, "dez": 5.43},
    ("PI", "Parnaíba"): {"jan": 5.15, "fev": 5.27, "mar": 5.22, "abr": 5.14, "mai": 5.21, "jun": 5.36, "jul": 5.58, "ago": 5.95, "set": 6.08, "out": 5.96, "nov": 5.71, "dez": 5.39},
    ("PI", "Picos"): {"jan": 5.08, "fev": 5.20, "mar": 5.18, "abr": 5.16, "mai": 5.25, "jun": 5.44, "jul": 5.73, "ago": 6.14, "set": 6.38, "out": 6.16, "nov": 5.91, "dez": 5.47},

    ("MA", "São Luís"): {"jan": 5.02, "fev": 5.10, "mar": 5.00, "abr": 4.95, "mai": 5.05, "jun": 5.20, "jul": 5.45, "ago": 5.90, "set": 6.10, "out": 6.00, "nov": 5.70, "dez": 5.30},
    ("MA", "Imperatriz"): {"jan": 5.18, "fev": 5.24, "mar": 5.11, "abr": 5.02, "mai": 5.12, "jun": 5.31, "jul": 5.59, "ago": 6.02, "set": 6.22, "out": 6.07, "nov": 5.74, "dez": 5.36},
    ("MA", "Balsas"): {"jan": 5.22, "fev": 5.26, "mar": 5.12, "abr": 5.03, "mai": 5.14, "jun": 5.34, "jul": 5.63, "ago": 6.08, "set": 6.29, "out": 6.11, "nov": 5.78, "dez": 5.39},
    ("MA", "Caxias"): {"jan": 4.97, "fev": 5.08, "mar": 5.06, "abr": 5.04, "mai": 5.14, "jun": 5.31, "jul": 5.58, "ago": 6.05, "set": 6.29, "out": 6.08, "nov": 5.80, "dez": 5.34},
    ("MA", "Timon"): {"jan": 4.93, "fev": 5.12, "mar": 5.14, "abr": 5.13, "mai": 5.23, "jun": 5.41, "jul": 5.69, "ago": 6.19, "set": 6.49, "out": 6.25, "nov": 5.97, "dez": 5.43},

    ("CE", "Fortaleza"): {"jan": 5.60, "fev": 5.75, "mar": 5.65, "abr": 5.45, "mai": 5.55, "jun": 5.80, "jul": 6.05, "ago": 6.30, "set": 6.45, "out": 6.35, "nov": 6.10, "dez": 5.85},
    ("CE", "Juazeiro do Norte"): {"jan": 5.42, "fev": 5.50, "mar": 5.41, "abr": 5.31, "mai": 5.39, "jun": 5.58, "jul": 5.88, "ago": 6.24, "set": 6.41, "out": 6.20, "nov": 5.93, "dez": 5.56},
    ("CE", "Sobral"): {"jan": 5.47, "fev": 5.60, "mar": 5.52, "abr": 5.36, "mai": 5.45, "jun": 5.67, "jul": 5.93, "ago": 6.25, "set": 6.39, "out": 6.22, "nov": 5.96, "dez": 5.61},

    ("PE", "Recife"): {"jan": 5.30, "fev": 5.45, "mar": 5.35, "abr": 5.10, "mai": 4.95, "jun": 4.80, "jul": 4.95, "ago": 5.20, "set": 5.55, "out": 5.70, "nov": 5.75, "dez": 5.60},
    ("PE", "Caruaru"): {"jan": 5.26, "fev": 5.36, "mar": 5.28, "abr": 5.12, "mai": 4.98, "jun": 4.86, "jul": 5.01, "ago": 5.29, "set": 5.62, "out": 5.78, "nov": 5.80, "dez": 5.63},
    ("PE", "Petrolina"): {"jan": 5.55, "fev": 5.61, "mar": 5.49, "abr": 5.36, "mai": 5.41, "jun": 5.58, "jul": 5.85, "ago": 6.19, "set": 6.35, "out": 6.18, "nov": 5.96, "dez": 5.63},

    ("BA", "Salvador"): {"jan": 5.10, "fev": 5.25, "mar": 5.10, "abr": 4.85, "mai": 4.70, "jun": 4.60, "jul": 4.85, "ago": 5.15, "set": 5.35, "out": 5.45, "nov": 5.50, "dez": 5.35},
    ("BA", "Feira de Santana"): {"jan": 5.26, "fev": 5.34, "mar": 5.20, "abr": 4.98, "mai": 4.83, "jun": 4.71, "jul": 4.93, "ago": 5.21, "set": 5.43, "out": 5.56, "nov": 5.60, "dez": 5.42},
    ("BA", "Barreiras"): {"jan": 5.38, "fev": 5.41, "mar": 5.26, "abr": 5.03, "mai": 4.96, "jun": 4.88, "jul": 5.09, "ago": 5.38, "set": 5.62, "out": 5.73, "nov": 5.75, "dez": 5.55},
}

CONCESSIONARIAS = [
    {"nome": "Equatorial Piauí", "uf": "PI", "te": 0.36, "tusd": 0.42, "fio_b": 0.24, "custo_disponibilidade_mono": 30, "custo_disponibilidade_bi": 50, "custo_disponibilidade_tri": 100},
    {"nome": "Equatorial Maranhão", "uf": "MA", "te": 0.35, "tusd": 0.41, "fio_b": 0.23, "custo_disponibilidade_mono": 30, "custo_disponibilidade_bi": 50, "custo_disponibilidade_tri": 100},
    {"nome": "Neoenergia Pernambuco", "uf": "PE", "te": 0.37, "tusd": 0.43, "fio_b": 0.25, "custo_disponibilidade_mono": 30, "custo_disponibilidade_bi": 50, "custo_disponibilidade_tri": 100},
    {"nome": "Neoenergia Coelba", "uf": "BA", "te": 0.36, "tusd": 0.42, "fio_b": 0.24, "custo_disponibilidade_mono": 30, "custo_disponibilidade_bi": 50, "custo_disponibilidade_tri": 100},
    {"nome": "Enel Ceará", "uf": "CE", "te": 0.37, "tusd": 0.44, "fio_b": 0.25, "custo_disponibilidade_mono": 30, "custo_disponibilidade_bi": 50, "custo_disponibilidade_tri": 100},
]

ICMS_POR_UF = {
    "PI": 0.22,
    "MA": 0.22,
    "PE": 0.20,
    "BA": 0.20,
    "CE": 0.20,
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
COR_AZUL = HexColor("#0f172a")
COR_VERMELHO = COR_PRINCIPAL_HEX
COR_VERMELHO_ESCURO = "#8f1d22"
COR_VERMELHO_CLARO = HexColor("#fff1f2")
COR_CINZA_TEXTO = HexColor("#6b7280")
COR_LARANJA_DESTAQUE = COR_PRINCIPAL


# =========================================================
# FUNÇÕES GERAIS
# =========================================================

def obter_ufs():
    return sorted({uf for (uf, _) in IRRADIACAO_CIDADES.keys()})


def obter_cidades_por_uf(uf):
    return sorted([cidade for (uf_base, cidade) in IRRADIACAO_CIDADES.keys() if uf_base == uf])


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


def desenhar_rodape(c):
    c.setStrokeColor(COR_LINHA)
    c.line(40, 35, 555, 35)
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#64748b"))
    c.drawString(40, 20, "RPO Serviços - Proposta Comercial")


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


def desenhar_pagina_producao(c, largura, altura, dados, img_geracao_buffer):
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

    nome = dados["nome_cliente"] or "-"
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(azul_texto)
    c.drawString(50, 735, nome)

    c.setFont("Helvetica", 11)
    c.setFillColor(cinza)
    c.drawString(50, 715, f"{dados['cidade']}/{dados['uf']}")

    c.setFillColor(vermelho_claro)
    c.roundRect(50, 650, 210, 65, 12, fill=1, stroke=0)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(vermelho)
    c.drawString(65, 690, "Produção média")

    prod_media = f"{dados['geracao_media']:,.0f}".replace(",", ".")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(azul_texto)
    c.drawString(65, 665, f"{prod_media} kWh/mês")

    c.setFont("Helvetica-Bold", 17)
    c.setFillColor(vermelho)
    c.drawCentredString(largura / 2, 615, "Geração mensal do sistema")

    c.setFont("Helvetica", 10)
    c.setFillColor(cinza)
    c.drawCentredString(largura / 2, 598, "Estimativa média de produção ao longo dos meses")

    c.drawImage(
        ImageReader(img_geracao_buffer),
        50,
        310,
        width=490,
        height=260,
        preserveAspectRatio=True,
        mask='auto'
    )

    y_base = 270

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(COR_LARANJA_DESTAQUE)
    c.drawString(50, y_base, "GARANTIAS DO SISTEMA")

    c.setFillColor(COR_LARANJA_DESTAQUE)
    c.rect(50, y_base - 6, 490, 2, fill=1, stroke=0)

    texto1 = (
        "Os módulos fotovoltaicos foram projetados para oferecer desempenho duradouro, "
        "com garantia de performance de até 25 anos, assegurando no mínimo 80% da capacidade "
        "original de geração ao longo do período."
    )

    texto2 = (
        "Os módulos solares contam com 12 anos de garantia contra defeitos de fabricação, "
        "conforme as condições fornecidas pelo fabricante."
    )

    texto3 = (
        "O inversor possui 10 anos de garantia contra defeitos de fabricação, proporcionando "
        "mais segurança e confiabilidade ao sistema instalado."
    )

    y = desenhar_texto_quebrado(c, texto1, 50, y_base - 22, 480)
    y = desenhar_texto_quebrado(c, texto2, 50, y - 5, 480)
    y = desenhar_texto_quebrado(c, texto3, 50, y - 5, 480)

    y -= 15

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(COR_LARANJA_DESTAQUE)
    c.drawString(50, y, "PRAZO DE INSTALAÇÃO")

    c.rect(50, y - 6, 490, 2, fill=1, stroke=0)

    texto4 = (
        "A instalação do sistema poderá ser concluída em até 60 dias após a confirmação "
        "do pagamento, seguindo o planejamento técnico do projeto."
    )

    desenhar_texto_quebrado(c, texto4, 50, y - 22, 480)


# =========================================================
# PDF
# =========================================================

def gerar_pdf_proposta(dados, img_geracao_buffer):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    # PÁGINA 1 - CAPA
    try:
        capa = ImageReader("capa.png")
        c.drawImage(capa, 0, 0, width=largura, height=altura)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(COR_PRINCIPAL)
        c.drawRightString(530, 83, texto_maiusculo_seguro(dados["nome_cliente"]) or "CLIENTE")
    except Exception:
        desenhar_capa_fallback(c, largura, altura, dados["nome_cliente"])
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

    desenhar_rodape(c)
    c.showPage()

    # PÁGINA 3 - FUNCIONAMENTO DO SISTEMA SOLAR
    desenhar_fundo_padrao(c, largura, altura)
    desenhar_titulo_pagina(c, "Funcionamento do sistema solar")

    c.setFont("Helvetica", 10.5)
    c.setFillColor(COR_TEXTO)
    c.drawString(50, 770, "Entenda de forma visual como a energia solar funciona no sistema fotovoltaico.")

    try:
        img_funcionamento = ImageReader("solar.png")
        area_x = 40
        area_y = 70
        area_w = largura - 80
        area_h = altura - 170

        c.drawImage(
            img_funcionamento,
            area_x,
            area_y,
            width=area_w,
            height=area_h,
            preserveAspectRatio=True,
            mask='auto'
        )
    except Exception:
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(COR_PRINCIPAL)
        c.drawString(50, 720, "Não foi possível carregar a imagem solar.png")
        c.setFont("Helvetica", 10)
        c.setFillColor(COR_TEXTO)
        c.drawString(50, 700, "Confira se o arquivo solar.png está na mesma pasta do app.py")

    desenhar_rodape(c)
    c.showPage()

    # PÁGINA 4 - PRODUÇÃO
    desenhar_pagina_producao(c, largura, altura, dados, img_geracao_buffer)
    c.showPage()

    # PÁGINA 5 - PRODUTOS
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

    desenhar_rodape(c)
    c.showPage()

    # PÁGINA 6 - ACEITE
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

    desenhar_rodape(c)
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
    irradiacao_cidade = IRRADIACAO_CIDADES[(uf, cidade)]
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