import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score
)

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
    page_title="Matriz de Confusão",
    page_icon="📈",
    layout="wide"
)
carregar_css()

st.title("Dashboard de Matriz de Confusão")

# =====================================================
# DATASET
# =====================================================

if not dataset_existe():

    st.error("Faça upload na Home.")

    st.stop()

df = carregar_dataset()

df = transformar(df)

# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("Filtros")

faixa = st.sidebar.selectbox(
    "Faixa Etária",
    sorted(df["Faixa Etária"].unique())
)

imc = st.sidebar.selectbox(
    "Categoria IMC",
    sorted(df["Categoria IMC"].unique())
)

medicamento = st.sidebar.selectbox(
    "Medicamento",
    sorted(df["Medicamento"].unique())
)

# =====================================================
# FILTRO FINAL
# =====================================================

grupo = df[
    (df["Faixa Etária"] == faixa) &
    (df["Categoria IMC"] == imc) &
    (df["Medicamento"] == medicamento)
]

# =====================================================
# KPIS
# =====================================================

st.header("Grupo Selecionado")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Faixa Etária", faixa)
c2.metric("IMC", imc)
c3.metric("Medicamento", medicamento)
c4.metric("Pacientes", len(grupo))

# =====================================================
# VALIDAÇÃO
# =====================================================

if len(grupo) < 5:

    st.warning(
        "Poucos dados para gerar matriz confiável."
    )

    st.stop()

# =====================================================
# REAL
# =====================================================

y_true = (
    grupo["Eficácia do Medicamento"] >= 70
).astype(int)

# =====================================================
# PREDIÇÃO
# =====================================================

y_pred = (
    (
        grupo["Adesão ao tratamento (%)"] >= 70
    ) &
    (
        grupo["Dose de Medicamento (mg/dia)"] >=
        grupo["Dose de Medicamento (mg/dia)"].median()
    )
).astype(int)

# =====================================================
# MATRIZ
# =====================================================

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1]
)

tn, fp, fn, tp = cm.ravel()

# =====================================================
# MÉTRICAS
# =====================================================

acc = accuracy_score(y_true, y_pred)

prec = precision_score(
    y_true,
    y_pred,
    zero_division=0
)

rec = recall_score(
    y_true,
    y_pred,
    zero_division=0
)

# =====================================================
# DASHBOARD MATRIZ
# =====================================================

st.header("Matriz de Confusão")

fig = go.Figure(
    data=go.Heatmap(

        # Aqui os números controlam APENAS a cor da célula
        # 0 = pior/vermelho
        # 1 = médio/amarelo
        # 2 = intermediário/amarelo claro
        # 3 = melhor/verde
        z=[
            [2, 3],  # VN | VP
            [0, 1]   # FN | FP
        ],

        x=[
            "Predito Negativo",
            "Predito Positivo"
        ],

        y=[
            "Real Negativo",
            "Real Positivo"
        ],

        text=[
            [
                f"VN<br>{tn}",
                f"VP<br>{tp}"
            ],
            [
                f"FN<br>{fn}",
                f"FP<br>{fp}"
            ]
        ],

        texttemplate="%{text}",

        textfont=dict(
            size=28,
            color="black"
        ),

        colorscale=[
            [0.00, "#ff9e9e"],
            [0.24, "#ff9e9e"],

            [0.25, "#ffe89a"],
            [0.49, "#ffe89a"],

            [0.50, "#fff0a8"],
            [0.74, "#fff0a8"],

            [0.75, "#b9ef9d"],
            [1.00, "#b9ef9d"]
        ],

        zmin=0,
        zmax=3,

        showscale=True,

        colorbar=dict(
            title="",
            tickvals=[0, 3],
            ticktext=["Pior", "Melhor"]
        )
    )
)

fig.update_layout(

    height=600,

    title="Dashboard da Matriz de Confusão",

    xaxis_title="Valor Predito",

    yaxis_title="Valor Real",

    font=dict(size=18),

    yaxis=dict(
        autorange="reversed"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# MÉTRICAS
# =====================================================

st.header("Métricas do Modelo")

k1, k2, k3 = st.columns(3)

k1.metric(
    "Acurácia",
    f"{round(acc * 100, 2)}%"
)

k2.metric(
    "Precisão",
    f"{round(prec * 100, 2)}%"
)

k3.metric(
    "Recall",
    f"{round(rec * 100, 2)}%"
)

# =====================================================
# LEGENDA
# =====================================================

st.header("Legenda")

l1, l2 = st.columns(2)

with l1:

    st.success("VP → Verdadeiro Positivo")

    st.success("VN → Verdadeiro Negativo")

with l2:

    st.error("FP → Falso Positivo")

    st.error("FN → Falso Negativo")

# =====================================================
# INTERPRETAÇÃO
# =====================================================

st.header("Interpretação Analítica")

st.markdown(f"""
### Verdadeiros Positivos (VP)

O modelo classificou corretamente
**{tp} pacientes**
como sucesso terapêutico.

---

### Verdadeiros Negativos (VN)

O modelo classificou corretamente
**{tn} pacientes**
como insucesso terapêutico.

---

### Falsos Positivos (FP)

O modelo classificou incorretamente
**{fp} pacientes**
como sucesso terapêutico.

---

### Falsos Negativos (FN)

O modelo classificou incorretamente
**{fn} pacientes**
como insucesso terapêutico.

Esse é o erro mais crítico,
pois pacientes potencialmente responsivos
podem deixar de receber tratamento adequado.
""")