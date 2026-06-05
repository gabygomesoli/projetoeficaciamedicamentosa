import streamlit as st

from utils import carregar_css

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.set_page_config(
    page_title="Home",
    page_icon="💊",
    layout="wide"
)


carregar_css()

# =====================================================
# HOME
# =====================================================

st.title("Sistema KDD — Eficácia Medicamentosa")

st.markdown("""
### Bem-vindo ao Sistema KDD

Esta aplicação realiza todas as etapas do processo KDD:

- Preparação dos Dados
- Transformação
- Mineração
- Matriz de Confusão
- Dashboards Analíticos
- Hipóteses Terapêuticas

Utilize o menu lateral para navegar entre as etapas.
""")

st.info(
    "Faça upload do dataset apenas uma vez na página de Preparação."
)