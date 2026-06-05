import streamlit as st
import pandas as pd

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
    page_title="Transformação",
    page_icon="🔄",
    layout="wide"
)
carregar_css()

st.title("Transformação dos Dados")

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

st.success("Transformação concluída!")

# =====================================================
# VERIFICAÇÃO DAS CATEGORIAS DE IMC
# =====================================================

st.header("Verificação das Categorias de IMC")

contagem_imc = (
    df["Categoria IMC"]
    .value_counts()
    .reset_index()
)

contagem_imc.columns = [
    "Categoria IMC",
    "Quantidade"
]

st.dataframe(
    contagem_imc,
    use_container_width=True
)

st.info("""
Essa tabela mostra quantos pacientes existem em cada categoria de IMC.""")

# =====================================================
# DATASET
# =====================================================

st.header("Dataset Transformado")

st.dataframe(
    df.head(20),
    use_container_width=True
)

# =====================================================
# DISTRIBUIÇÕES
# =====================================================

c1, c2 = st.columns(2)

with c1:

    st.subheader("👥 Faixa Etária")

    faixa = (
        df["Faixa Etária"]
        .value_counts()
        .reset_index()
    )

    faixa.columns = [
        "Faixa",
        "Quantidade"
    ]

    st.dataframe(
        faixa,
        use_container_width=True
    )

with c2:

    st.subheader("⚖️ Categoria IMC")

    imc = (
        df["Categoria IMC"]
        .value_counts()
        .reset_index()
    )

    imc.columns = [
        "IMC",
        "Quantidade"
    ]

    st.dataframe(
        imc,
        use_container_width=True
    )

# =====================================================
# 16 COMBINAÇÕES
# =====================================================

st.header("Matriz das 16 Combinações")

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

# =====================================================
# GERAÇÃO DAS 16 COMBINAÇÕES
# =====================================================

combinacoes = []

for faixa in faixas:

    for imc in imcs:

        grupo = df[
            (df["Faixa Etária"] == faixa) &
            (df["Categoria IMC"] == imc)
        ]

        qtd = len(grupo)

        if qtd > 0:

            ranking = (
                grupo.groupby("Medicamento")[
                    "Eficácia do Medicamento"
                ]
                .mean()
                .sort_values(ascending=False)
            )

            melhor_medicamento = ranking.index[0]

            eficacia = round(
                ranking.iloc[0],
                2
            )

        else:

            melhor_medicamento = "Sem amostra"

            eficacia = 0

        combinacoes.append({

            "Faixa Etária": faixa,

            "Categoria IMC": imc,

            "Qtd Pacientes": qtd,

            "Melhor Medicamento": melhor_medicamento,

            "Eficácia Média (%)": eficacia

        })

# =====================================================
# DATAFRAME FINAL
# =====================================================

comb = pd.DataFrame(combinacoes)

# =====================================================
# EXIBIÇÃO TABELA
# =====================================================

st.dataframe(
    comb,
    use_container_width=True
)

# =====================================================
# MATRIZ VISUAL
# =====================================================

st.header("Visualização das 16 Combinações")

for faixa in faixas:

    st.subheader(f"👥 {faixa}")

    cols = st.columns(4)

    for i, imc in enumerate(imcs):

        dados = comb[
            (comb["Faixa Etária"] == faixa) &
            (comb["Categoria IMC"] == imc)
        ]

        with cols[i]:

            st.markdown(f"### {imc}")

            if len(dados) > 0:

                med = dados.iloc[0][
                    "Melhor Medicamento"
                ]

                qtd = dados.iloc[0][
                    "Qtd Pacientes"
                ]

                ef = dados.iloc[0][
                    "Eficácia Média (%)"
                ]

                if qtd > 0:

                    st.success(f"💊 {med}")

                    st.metric(
                        "Eficácia",
                        f"{ef}%"
                    )

                    st.metric(
                        "Pacientes",
                        int(qtd)
                    )

                else:

                    st.error("Sem amostra")

# =====================================================
# DOWNLOAD
# =====================================================

st.header("Download")

csv = comb.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Baixar Combinações",
    data=csv,
    file_name="16_combinacoes.csv",
    mime="text/csv"
)