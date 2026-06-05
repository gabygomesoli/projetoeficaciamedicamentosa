import streamlit as st
import pandas as pd
import plotly.express as px

from utils import (
    carregar_css,
    carregar_dataset,
    dataset_existe,
    transformar
)

st.set_page_config(
    page_title="Hipóteses",
    page_icon="🧠",
    layout="wide"
)

carregar_css()

st.title("Hipóteses Analíticas")

if not dataset_existe():
    st.error("Faça upload na Home.")
    st.stop()

df = carregar_dataset()
df = transformar(df)

st.sidebar.header("Filtros")

medicamento = st.sidebar.selectbox(
    "Medicamento",
    sorted(df["Medicamento"].unique())
)

faixa = st.sidebar.selectbox(
    "Faixa Etária",
    sorted(df["Faixa Etária"].unique())
)

imc = st.sidebar.selectbox(
    "Categoria IMC",
    sorted(df["Categoria IMC"].unique())
)

grupo = df[
    (df["Medicamento"] == medicamento) &
    (df["Faixa Etária"] == faixa) &
    (df["Categoria IMC"] == imc)
]

st.header("Perfil Selecionado")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Medicamento", medicamento)
c2.metric("Faixa Etária", faixa)
c3.metric("IMC", imc)
c4.metric("Pacientes", len(grupo))

if len(grupo) == 0:
    st.warning("Não há pacientes para essa combinação.")
    st.stop()

eficacia_media = round(grupo["Eficácia do Medicamento"].mean(), 2)
dose_media = round(grupo["Dose de Medicamento (mg/dia)"].mean(), 2)
adesao_media = round(grupo["Adesão ao tratamento (%)"].mean(), 2)

st.header("Indicadores do Grupo")

k1, k2, k3 = st.columns(3)

k1.metric("Eficácia Média", f"{eficacia_media}%")
k2.metric("Dose Média", f"{dose_media} mg")
k3.metric("Adesão Média", f"{adesao_media}%")

st.header("Hipóteses do Resultado")

hipoteses = []

if adesao_media >= 75:
    hipoteses.append(
        "A alta adesão ao tratamento pode ter contribuído para uma melhor eficácia terapêutica."
    )
else:
    hipoteses.append(
        "A adesão ao tratamento abaixo do ideal pode ter limitado a eficácia do medicamento."
    )

if "Obesidade" in imc or "Sobrepeso" in imc:
    hipoteses.append(
        "Pacientes com maior IMC podem apresentar diferenças metabólicas que influenciam a absorção e a resposta ao medicamento."
    )

if "Baixo peso" in imc:
    hipoteses.append(
        "Pacientes com baixo peso podem responder de forma diferente devido à menor massa corporal e possível maior sensibilidade à dose."
    )

if "≥60" in faixa:
    hipoteses.append(
        "Pacientes idosos podem apresentar alterações fisiológicas, como metabolismo mais lento, o que pode influenciar a resposta terapêutica."
    )

if "18–29" in faixa:
    hipoteses.append(
        "Pacientes mais jovens podem apresentar melhor resposta devido a maior estabilidade metabólica e menor presença de comorbidades."
    )

if dose_media >= df["Dose de Medicamento (mg/dia)"].median():
    hipoteses.append(
        "A dose média administrada está acima ou próxima da mediana da base, podendo contribuir para maior resposta terapêutica."
    )
else:
    hipoteses.append(
        "A dose média administrada está abaixo da mediana da base, o que pode explicar uma eficácia mais moderada."
    )

for i, h in enumerate(hipoteses, start=1):
    st.markdown(f"**Hipótese {i}:** {h}")

st.header("Comparação com a Média Geral")

media_geral = round(df["Eficácia do Medicamento"].mean(), 2)

comparacao = pd.DataFrame({
    "Indicador": ["Eficácia do Grupo", "Eficácia Geral"],
    "Valor": [eficacia_media, media_geral]
})

fig = px.bar(
    comparacao,
    x="Indicador",
    y="Valor",
    color="Indicador",
    text_auto=".2f",
    title="Comparação da Eficácia"
)

fig.update_layout(
    height=500,
    title_x=0.5,
    yaxis_title="Eficácia (%)"
)

st.plotly_chart(fig, use_container_width=True)

st.header("Interpretação Final")

if eficacia_media > media_geral:
    st.success(f"""
O medicamento **{medicamento}** apresentou desempenho acima da média geral para pacientes da faixa **{faixa}** com perfil de IMC **{imc}**.

Isso sugere que esse medicamento pode ser mais adequado para esse perfil específico de paciente, possivelmente devido à combinação entre dose, adesão e características fisiológicas.
""")
else:
    st.warning(f"""
O medicamento **{medicamento}** apresentou desempenho abaixo ou próximo da média geral para pacientes da faixa **{faixa}** com perfil de IMC **{imc}**.

Isso indica que esse perfil pode exigir maior atenção, ajuste de dose ou avaliação de outros medicamentos com melhor resposta terapêutica.
""")

st.header("Dados do Grupo")

st.dataframe(
    grupo[
        [
            "Idade",
            "Categoria IMC",
            "Medicamento",
            "Dose de Medicamento (mg/dia)",
            "Adesão ao tratamento (%)",
            "Eficácia do Medicamento"
        ]
    ],
    use_container_width=True
)