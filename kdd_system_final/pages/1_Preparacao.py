import streamlit as st
import pandas as pd
from utils import salvar_dataset, carregar_css

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Preparação Completa",
    page_icon="📂",
    layout="wide"
)

carregar_css()


st.title("Preparação Completa")

# =====================================================
# UPLOAD
# =====================================================

arquivo = st.file_uploader(
    "Selecione o dataset",
    type=["xlsx", "csv"]
)

if arquivo:

    # =====================================================
    # LEITURA
    # =====================================================

    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)

    # =====================================================
    # SALVAR DATASET
    # =====================================================

    salvar_dataset(df)

    st.success("Dataset salvo com sucesso!")

    # =====================================================
    # INDICADORES GERAIS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Registros", len(df))
    c2.metric("Colunas", len(df.columns))
    c3.metric("Nulos", int(df.isnull().sum().sum()))
    c4.metric("Duplicados", int(df.duplicated().sum()))

    # =====================================================
    # PRÉVIA
    # =====================================================

    st.header("Prévia do Dataset")

    st.dataframe(
        df.head(20),
        use_container_width=True
    )

    # =====================================================
    # DADOS FALTANTES
    # =====================================================

    st.header("Dados Faltantes")

    nulos = pd.DataFrame({
        "Coluna": df.columns,
        "Qtd Nulos": df.isnull().sum().values,
        "% Nulos": (
            (df.isnull().sum() / len(df)) * 100
        ).round(2).values
    })

    st.dataframe(
        nulos,
        use_container_width=True
    )

    # =====================================================
    # ESTATÍSTICAS
    # =====================================================

    st.header("Estatísticas Descritivas")

    st.dataframe(
        df.describe(),
        use_container_width=True
    )

    # =====================================================
    # MOSTRAR NOMES DAS COLUNAS
    # =====================================================

    st.header("Colunas encontradas no Dataset")

    st.write(df.columns.tolist())

    # =====================================================
    # IDENTIFICAR COLUNA DE IMC AUTOMATICAMENTE
    # =====================================================

    colunas_possiveis_imc = [
        "Índice_de_Massa_Corporal_IMC",
        "Índice de Massa Corporal (IMC)",
        "Indice_de_Massa_Corporal_IMC",
        "Indice de Massa Corporal (IMC)",
        "IMC",
        "imc"
    ]

    coluna_imc = None

    for coluna in colunas_possiveis_imc:
        if coluna in df.columns:
            coluna_imc = coluna
            break

    # =====================================================
    # QUANTIDADE POR CATEGORIA IMC — ANTES DA TRANSFORMAÇÃO
    # =====================================================

    st.header("Quantidade de Pacientes por Categoria IMC")

    if coluna_imc is not None:

        df[coluna_imc] = pd.to_numeric(
            df[coluna_imc],
            errors="coerce"
        )

        abaixo_peso = (
            df[coluna_imc] < 18.5
        ).sum()

        peso_normal = (
            (
                df[coluna_imc] >= 18.5
            ) &
            (
                df[coluna_imc] < 25
            )
        ).sum()

        sobrepeso = (
            (
                df[coluna_imc] >= 25
            ) &
            (
                df[coluna_imc] < 30
            )
        ).sum()

        obesidade = (
            df[coluna_imc] >= 30
        ).sum()

        st.markdown(f"""
###Distribuição de IMC antes da transformação

- Abaixo do Peso: **{int(abaixo_peso)}**
- Peso Normal: **{int(peso_normal)}**
- Sobrepeso: **{int(sobrepeso)}**
- Obesidade: **{int(obesidade)}**
""")

        categorias_imc = pd.DataFrame({
            "Categoria": [
                "Abaixo do Peso",
                "Peso Normal",
                "Sobrepeso",
                "Obesidade"
            ],
            "Quantidade": [
                int(abaixo_peso),
                int(peso_normal),
                int(sobrepeso),
                int(obesidade)
            ]
        })

        st.dataframe(
            categorias_imc,
            use_container_width=True
        )

        st.bar_chart(
            categorias_imc.set_index("Categoria")
        )

        st.info(f"""
A coluna utilizada para calcular o IMC foi: **{coluna_imc}**.""")

    else:

        st.error("""
Nenhuma coluna de IMC foi encontrada automaticamente.

Verifique o nome da coluna na lista exibida acima e ajuste no código.
""")

    # =====================================================
    # DISTRIBUIÇÃO DE IDADE — ANTES DA TRANSFORMAÇÃO
    # =====================================================

    st.header("Distribuição de Idade")

    if "Idade" in df.columns:

        df["Idade"] = pd.to_numeric(
            df["Idade"],
            errors="coerce"
        )

        idade_min = df["Idade"].min()
        idade_max = df["Idade"].max()

        c1, c2 = st.columns(2)

        c1.metric(
            "Idade Mínima",
            int(idade_min)
        )

        c2.metric(
            "Idade Máxima",
            int(idade_max)
        )

        st.bar_chart(
            df["Idade"]
        )

    else:

        st.warning("Coluna Idade não encontrada no dataset.")

else:

    st.info("Faça upload do dataset para iniciar.")