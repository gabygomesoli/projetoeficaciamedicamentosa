import streamlit as st

from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
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
    page_title="Matrizes",
    page_icon="📊",
    layout="wide"
)

carregar_css()

st.title("Matrizes de Confusão")

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
# COMBINAÇÕES
# =====================================================

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

st.info("""
Esta página apresenta todas as combinações possíveis
entre Faixa Etária e Categoria IMC.
""")

# =====================================================
# GERAÇÃO DAS 16 MATRIZES
# =====================================================

for faixa in faixas:

    st.header(f"Faixa Etária: {faixa}")

    cols = st.columns(4)

    for i, imc in enumerate(imcs):

        with cols[i]:

            st.subheader(imc)

            grupo = df[
                (df["Faixa Etária"] == faixa) &
                (df["Categoria IMC"] == imc)
            ]

            st.metric(
                "Pacientes",
                len(grupo)
            )

            if len(grupo) < 5:

                st.warning(
                    "Sem amostra suficiente."
                )

            else:

                # ==================================
                # MATRIZ
                # ==================================

                y_true = (
                    grupo["Eficácia do Medicamento"] >= 70
                ).astype(int)

                y_pred = (
                    grupo["Adesão ao tratamento (%)"] >= 80
                ).astype(int)

                cm = confusion_matrix(
                    y_true,
                    y_pred,
                    labels=[0, 1]
                )

                tn, fp, fn, tp = cm.ravel()

                st.markdown(f"""
<div style="
display:grid;
grid-template-columns:1fr 1fr;
gap:8px;
margin-top:10px;
margin-bottom:10px;
">

<div style="
background:#F4D03F;
padding:18px;
border-radius:12px;
text-align:center;
color:black;
font-weight:bold;
">
VN
<br>
<h2>{tn}</h2>
</div>

<div style="
background:#2ECC71;
padding:18px;
border-radius:12px;
text-align:center;
color:white;
font-weight:bold;
">
VP
<br>
<h2>{tp}</h2>
</div>

<div style="
background:#E74C3C;
padding:18px;
border-radius:12px;
text-align:center;
color:white;
font-weight:bold;
">
FN
<br>
<h2>{fn}</h2>
</div>

<div style="
background:#F39C12;
padding:18px;
border-radius:12px;
text-align:center;
color:white;
font-weight:bold;
">
FP
<br>
<h2>{fp}</h2>
</div>

</div>
""", unsafe_allow_html=True)

                # ==================================
                # MÉTRICAS
                # ==================================

                acc = accuracy_score(
                    y_true,
                    y_pred
                )

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

                f1 = f1_score(
                    y_true,
                    y_pred,
                    zero_division=0
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "Acurácia",
                    f"{round(acc*100,2)}%"
                )

                c2.metric(
                    "Precisão",
                    f"{round(prec*100,2)}%"
                )

                c1.metric(
                    "Recall",
                    f"{round(rec*100,2)}%"
                )

                c2.metric(
                    "F1",
                    f"{round(f1*100,2)}%"
                )

                st.divider()