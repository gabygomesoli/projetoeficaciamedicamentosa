# =====================================================
# ÉPICO 3 — MINERAÇÃO DE DADOS COMPLETA
# =====================================================

import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    carregar_css,
    carregar_dataset,
    dataset_existe,
    transformar
)

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Mineração de Dados",
    page_icon="⛏️",
    layout="wide"
)

carregar_css()

st.title("Mineração de Dados")

# =====================================================
# VALIDAÇÃO
# =====================================================

if not dataset_existe():

    st.error("Faça upload na Home.")

    st.stop()

# =====================================================
# CARREGAMENTO
# =====================================================

df = carregar_dataset()

df = transformar(df)

# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("Filtros")

faixa_filtro = st.sidebar.multiselect(
    "Faixa Etária",
    sorted(df["Faixa Etária"].unique()),
    default=sorted(df["Faixa Etária"].unique())
)

imc_filtro = st.sidebar.multiselect(
    "Categoria IMC",
    sorted(df["Categoria IMC"].unique()),
    default=sorted(df["Categoria IMC"].unique())
)

med_filtro = st.sidebar.multiselect(
    "Medicamento",
    sorted(df["Medicamento"].unique()),
    default=sorted(df["Medicamento"].unique())
)

# =====================================================
# FILTRO FINAL
# =====================================================

df = df[
    (df["Faixa Etária"].isin(faixa_filtro)) &
    (df["Categoria IMC"].isin(imc_filtro)) &
    (df["Medicamento"].isin(med_filtro))
]

# =====================================================
# KPIS
# =====================================================

st.header("Indicadores Gerais")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Pacientes",
    len(df)
)

c2.metric(
    "Medicamentos",
    df["Medicamento"].nunique()
)

c3.metric(
    "Eficácia Média",
    f"{round(df['Eficácia do Medicamento'].mean(),2)}%"
)

c4.metric(
    "Dose Média",
    round(df["Dose de Medicamento (mg/dia)"].mean(),2)
)

# =====================================================
# AGRUPAMENTO
# =====================================================

resultado = (
    df.groupby([
        "Faixa Etária",
        "Categoria IMC",
        "Medicamento"
    ])
    .agg({

        "Eficácia do Medicamento":"mean",

        "Dose de Medicamento (mg/dia)":"mean",

        "Adesão ao tratamento (%)":"mean",

        "Idade":"count"

    })
    .reset_index()
)

resultado.rename(columns={

    "Eficácia do Medicamento":"Eficácia Média",

    "Dose de Medicamento (mg/dia)":"Dose Média",

    "Adesão ao tratamento (%)":"Adesão Média",

    "Idade":"Qtd Pacientes"

}, inplace=True)

# =====================================================
# RANKING
# =====================================================

resultado = resultado.sort_values(
    "Eficácia Média",
    ascending=False
)

# =====================================================
# MELHORES MEDICAMENTOS
# =====================================================

melhores = (
    resultado.groupby([
        "Faixa Etária",
        "Categoria IMC"
    ])
    .first()
    .reset_index()
)

# =====================================================
# MATRIZ DAS 16 COMBINAÇÕES
# =====================================================

st.header("Matriz de Decisão — 16 Combinações")

faixas = [
    "18–29 anos",
    "30–44 anos",
    "45–59 anos",
    "≥60 anos"
]

imcs = [
    "Baixo peso",
    "Peso normal",
    "Sobrepeso",
    "Obesidade"
]

for faixa in faixas:

    st.subheader(f"{faixa}")

    cols = st.columns(4)

    for i, imc in enumerate(imcs):

        dados = melhores[
            (melhores["Faixa Etária"] == faixa) &
            (melhores["Categoria IMC"] == imc)
        ]

        with cols[i]:

            st.markdown(f"{imc}")

            if len(dados) > 0:

                med = dados.iloc[0]["Medicamento"]

                eficacia = round(
                    dados.iloc[0]["Eficácia Média"],
                    2
                )

                dose = round(
                    dados.iloc[0]["Dose Média"],
                    2
                )

                adesao = round(
                    dados.iloc[0]["Adesão Média"],
                    2
                )

                pacientes = int(
                    dados.iloc[0]["Qtd Pacientes"]
                )

                st.success(f"{med}")

                st.metric(
                    "Eficácia",
                    f"{eficacia}%"
                )

                st.metric(
                    "Dose Média",
                    f"{dose} mg"
                )

                st.metric(
                    "Adesão",
                    f"{adesao}%"
                )

                st.metric(
                    "Pacientes",
                    pacientes
                )

            else:

                st.error("Sem amostra")

