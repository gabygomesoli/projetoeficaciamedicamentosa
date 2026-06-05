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
    page_title="Dashboard Analítico",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

carregar_css()

st.title("Dashboard Analítico de Eficácia Terapêutica")

# =====================================================
# VALIDAÇÃO
# =====================================================

if not dataset_existe():

    st.error("Faça upload do dataset na Home.")

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

med = st.sidebar.multiselect(
    "Medicamentos",
    sorted(df["Medicamento"].unique()),
    default=sorted(df["Medicamento"].unique())
)

faixa = st.sidebar.multiselect(
    "Faixas Etárias",
    sorted(df["Faixa Etária"].unique()),
    default=sorted(df["Faixa Etária"].unique())
)

imc = st.sidebar.multiselect(
    "Categoria IMC",
    sorted(df["Categoria IMC"].unique()),
    default=sorted(df["Categoria IMC"].unique())
)

df = df[
    (df["Medicamento"].isin(med)) &
    (df["Faixa Etária"].isin(faixa)) &
    (df["Categoria IMC"].isin(imc))
]

# =====================================================
# DASHBOARD DF
# =====================================================

dashboard_df = df.copy()

dashboard_df = dashboard_df.dropna(
    subset=[
        "Dose de Medicamento (mg/dia)",
        "Eficácia do Medicamento",
        "Adesão ao tratamento (%)"
    ]
)

# =====================================================
# KPIS
# =====================================================

st.header("Indicadores Gerais")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Pacientes",
    len(dashboard_df)
)

k2.metric(
    "Eficácia Média",
    f"{round(dashboard_df['Eficácia do Medicamento'].mean(),2)}%"
)

k3.metric(
    "Dose Média",
    f"{round(dashboard_df['Dose de Medicamento (mg/dia)'].mean(),2)} mg"
)

k4.metric(
    "Adesão Média",
    f"{round(dashboard_df['Adesão ao tratamento (%)'].mean(),2)}%"
)

# =====================================================
# RESULTADO AGRUPADO
# =====================================================

resultado = (
    dashboard_df.groupby([
        "Faixa Etária",
        "Categoria IMC",
        "Medicamento"
    ])
    .agg({
        "Eficácia do Medicamento": "mean",
        "Dose de Medicamento (mg/dia)": "mean",
        "Adesão ao tratamento (%)": "mean",
        "Idade": "count"
    })
    .reset_index()
)

resultado.rename(columns={
    "Eficácia do Medicamento": "Eficácia Média",
    "Dose de Medicamento (mg/dia)": "Dose Média",
    "Adesão ao tratamento (%)": "Adesão Média",
    "Idade": "Qtd Pacientes"
}, inplace=True)

# =====================================================
# TABS
# =====================================================

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dose x Eficácia",
    "Ranking",
    "Dose",
    "Faixa Etária",
    "Heatmap",
    "Análises"
])

# =====================================================
# TAB 0 — DOSE X EFICÁCIA
# =====================================================

with tab0:

    st.subheader("Relação entre Dose e Eficácia")

    scatter_df = dashboard_df.copy()

    scatter_df = scatter_df.dropna(
        subset=[
            "Adesão ao tratamento (%)",
            "Dose de Medicamento (mg/dia)",
            "Eficácia do Medicamento"
        ]
    )

    scatter_df["Adesão ao tratamento (%)"] = pd.to_numeric(
        scatter_df["Adesão ao tratamento (%)"],
        errors="coerce"
    )

    scatter_df = scatter_df.dropna(
        subset=["Adesão ao tratamento (%)"]
    )

    scatter = px.scatter(
        scatter_df,
        x="Dose de Medicamento (mg/dia)",
        y="Eficácia do Medicamento",
        color="Medicamento",
        size="Adesão ao tratamento (%)",
        hover_data=[
            "Faixa Etária",
            "Categoria IMC"
        ],
        title="Relação entre Dose e Eficácia",
        size_max=35
    )

    scatter.update_layout(
        height=700,
        title_x=0.5,
        xaxis_title="Dose do Medicamento (mg/dia)",
        yaxis_title="Eficácia (%)",
        legend_title="Medicamento"
    )

    scatter.update_traces(
        opacity=0.8
    )

    st.plotly_chart(
        scatter,
        use_container_width=True
    )

# =====================================================
# TAB 1 — RANKING
# =====================================================

with tab1:

    st.subheader("Ranking de Medicamentos")

    ranking = (
        dashboard_df.groupby("Medicamento")[
            "Eficácia do Medicamento"
        ]
        .mean()
        .sort_values(ascending=False)
    )

    fig1 = px.bar(
        ranking.reset_index(),
        x="Medicamento",
        y="Eficácia do Medicamento",
        color="Eficácia do Medicamento",
        text_auto=".2f",
        title="Ranking Geral de Eficácia"
    )

    fig1.update_layout(
        height=650,
        title_x=0.5
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

# =====================================================
# TAB 2 — DOSE
# =====================================================

with tab2:

    st.subheader("Dose Média por Medicamento")

    dose_med = (
        dashboard_df.groupby("Medicamento")[
            "Dose de Medicamento (mg/dia)"
        ]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig2 = px.line(
        dose_med,
        x="Medicamento",
        y="Dose de Medicamento (mg/dia)",
        markers=True,
        title="Dose Média Utilizada"
    )

    fig2.update_layout(
        height=600,
        title_x=0.5,
        xaxis_title="Medicamento",
        yaxis_title="Dose Média (mg)"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# =====================================================
# TAB 3 — FAIXA ETÁRIA
# =====================================================

with tab3:

    st.subheader("Eficácia por Faixa Etária")

    faixa_df = (
        dashboard_df.groupby([
            "Faixa Etária",
            "Medicamento"
        ])[
            "Eficácia do Medicamento"
        ]
        .mean()
        .reset_index()
    )

    fig3 = px.bar(
        faixa_df,
        x="Faixa Etária",
        y="Eficácia do Medicamento",
        color="Medicamento",
        barmode="group",
        title="Comparação de Eficácia por Idade"
    )

    fig3.update_layout(
        height=650,
        title_x=0.5,
        xaxis_title="Faixa Etária",
        yaxis_title="Eficácia Média (%)"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# =====================================================
# TAB 4 — HEATMAP
# =====================================================

with tab4:

    st.subheader("Heatmap de Correlação")

    corr_df = dashboard_df.select_dtypes(
        include="number"
    ).corr()

    heat = px.imshow(
        corr_df,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale=[
            [0.0, "#8B0000"],
            [0.5, "#F5F5F5"],
            [1.0, "#003C8F"]
        ],
        zmin=-1,
        zmax=1,
        title="Correlação entre Variáveis"
    )

    heat.update_layout(
        height=750,
        title_x=0.5,
        font=dict(
            size=16
        ),
        coloraxis_colorbar=dict(
            title="Correlação",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=[
                "-1",
                "-0.5",
                "0",
                "0.5",
                "1"
            ]
        )
    )

    heat.update_traces(
        hovertemplate=
        "<b>%{x}</b> x <b>%{y}</b><br>" +
        "Correlação: %{z:.2f}<extra></extra>"
    )

    st.plotly_chart(
        heat,
        use_container_width=True
    )

    st.info("""
Vermelho → Correlação negativa

Branco → Sem correlação

Azul → Correlação positiva

Quanto mais próximo de:
- +1 → relação positiva forte
- -1 → relação negativa forte
- 0 → pouca relação
""")

# =====================================================
# TAB 5 — ANÁLISES
# =====================================================

with tab5:

    # =====================================================
    # INSIGHTS
    # =====================================================

    st.header("Insights Automáticos")

    melhor_med = (
        dashboard_df.groupby("Medicamento")[
            "Eficácia do Medicamento"
        ]
        .mean()
        .idxmax()
    )

    melhor_ef = round(
        dashboard_df.groupby("Medicamento")[
            "Eficácia do Medicamento"
        ]
        .mean()
        .max(),
        2
    )

    melhor_faixa = (
        dashboard_df.groupby("Faixa Etária")[
            "Eficácia do Medicamento"
        ]
        .mean()
        .idxmax()
    )

    st.success(f"""
O medicamento com melhor desempenho geral foi:

{melhor_med}

Eficácia média:

{melhor_ef}%

Melhor faixa etária:

{melhor_faixa}
""")

    # =====================================================
    # TOP 10
    # =====================================================

    st.header("Top 10 Combinações Mais Eficientes")

    top10 = (
        resultado.sort_values(
            "Eficácia Média",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top10,
        use_container_width=True
    )

    # =====================================================
    # INTERPRETAÇÃO
    # =====================================================

    st.header("Interpretação Analítica")

    ranking_geral = (
        dashboard_df.groupby("Medicamento")[
            "Eficácia do Medicamento"
        ]
        .mean()
        .sort_values(ascending=False)
    )

    for med in ranking_geral.index:

        dados_med = dashboard_df[
            dashboard_df["Medicamento"] == med
        ]

        eficacia = round(
            dados_med[
                "Eficácia do Medicamento"
            ].mean(),
            2
        )

        dose_media = round(
            dados_med[
                "Dose de Medicamento (mg/dia)"
            ].mean(),
            2
        )

        adesao = round(
            dados_med[
                "Adesão ao tratamento (%)"
            ].mean(),
            2
        )

        melhor_faixa = (
            dados_med.groupby(
                "Faixa Etária"
            )[
                "Eficácia do Medicamento"
            ]
            .mean()
            .idxmax()
        )

        melhor_imc = (
            dados_med.groupby(
                "Categoria IMC"
            )[
                "Eficácia do Medicamento"
            ]
            .mean()
            .idxmax()
        )

        pior_faixa = (
            dados_med.groupby(
                "Faixa Etária"
            )[
                "Eficácia do Medicamento"
            ]
            .mean()
            .idxmin()
        )

        st.markdown(f"""
---
# Medicamento {med}

## Indicadores Gerais

- Eficácia média: **{eficacia}%**
- Dose média: **{dose_media} mg**
- Adesão média: **{adesao}%**

---

## Melhor Desempenho

- Melhor faixa etária:
  **{melhor_faixa}**

- Melhor categoria IMC:
  **{melhor_imc}**

O medicamento **{med}** demonstrou maior desempenho terapêutico principalmente nesses grupos.

---

## Menor Desempenho

A faixa etária com menor eficácia foi:

**{pior_faixa}**

Isso pode indicar:
- menor resposta fisiológica;
- necessidade de ajuste de dose;
- influência metabólica.

---

## Interpretação Clínica

Os dados indicam que:
- idade influencia a resposta terapêutica;
- IMC impacta absorção e metabolismo;
- adesão ao tratamento altera eficácia;
- dose adequada melhora resultados.
""")

# =====================================================
# EXPORTAÇÃO
# =====================================================

st.header("Exportação")

csv = resultado.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Baixar Resultado da Mineração",
    data=csv,
    file_name="mineracao_kdd.csv",
    mime="text/csv"
)