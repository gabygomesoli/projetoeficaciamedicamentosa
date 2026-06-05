
import pandas as pd
import os

DATA_PATH = "dataset_salvo.csv"

def carregar_css():
    import streamlit as st

    with open("style.css", "r", encoding="utf-8") as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True
        )

def salvar_dataset(df):
    df.to_csv(DATA_PATH, index=False)

def dataset_existe():
    return os.path.exists(DATA_PATH)

def carregar_dataset():
    return pd.read_csv(DATA_PATH)

def limpar_dados(df):
    colunas = [
        "Idade",
        "Índice de Massa Corporal (IMC)",
        "Dose de Medicamento (mg/dia)",
        "Eficácia do Medicamento",
        "Medicamento"
    ]
    return df.dropna(subset=colunas)

def faixa_etaria(x):
    if 18 <= x <= 29:
        return "18–29 anos"
    elif 30 <= x <= 44:
        return "30–44 anos"
    elif 45 <= x <= 59:
        return "45–59 anos"
    return "≥60 anos"

def categoria_imc(x):
    if x < 18.5:
        return "Baixo peso"
    elif x < 25:
        return "Peso normal"
    elif x < 30:
        return "Sobrepeso"
    return "Obesidade"

def transformar(df):
    df = limpar_dados(df)
    df["Faixa Etária"] = df["Idade"].apply(faixa_etaria)
    df["Categoria IMC"] = df["Índice de Massa Corporal (IMC)"].apply(categoria_imc)
    return df
