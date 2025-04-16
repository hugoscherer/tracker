import streamlit as st
import pandas as pd
from google_sheets_utils import authenticate_gsheets, get_worksheet
from datetime import datetime
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from users import *
import time

# Authentification Google Sheets
SHEET = authenticate_gsheets()

@st.cache_data(ttl=600)
def load_consumptions(user):
    worksheet = get_worksheet(SHEET, user)
    df = get_as_dataframe(worksheet).dropna(how='all') if worksheet else pd.DataFrame(columns=[
        "Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"
    ])

    for col in ["Type", "Boisson", "Taille"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    return df

# 🔍 Données des boissons prédéfinies avec leur degré d'alcool
DRINKS_DATA = {
    "🍺 Bière": {
        "Affligem": 6.7, "Bête": 8.0, "1664": 5.5, "Chouffe": 8.0,
        "Kronenbourg": 4.2, "Blonde bar": 4.5, "Leffe": 6.6,
        "Heineken": 5.0, "Desperados": 5.9, "Corona": 4.5,
        "IPA": 6.0, "Pelforth": 5.8, "Autre": 5.0
    },
    "🍷 Vin": {
        "Rouge": 12.5, "Blanc": 11.0, "Rosé": 12.0
    },
    "🥃 Hard": {
        "Vodka": 40.0, "Rhum": 40.0, "Whisky": 40.0,
        "Tequila": 38.0, "Gin": 37.5, "Pastis": 45.0, "Autre": 40.0
    },
    "🍾 Autres": {
        "Champagne": 12.0, "Cidre": 4.5, "Liqueur": 20.0, "Autre": 10.0
    }
}

GLASS_SIZES = {
    "🍺 Bière": {
        "Pinte (50cl)": 500, "Bouteille (33cl)": 330, "Demi (25cl)": 250, "Autre": None
    },
    "🍷 Vin": {
        "Verre de vin (15cl)": 150, "Bouteille (75cl)": 750, "Autre": None
    },
    "🥃 Hard": {
        "Shot (3cl)": 30, "Verre soirée (20cl)": 60, "Cocktail (25cl)": 40,
        "Ricard (2cl)": 20, "Autre": None
    },
    "🍾 Autres": {
        "Coupe champagne (15 cl)": 150, "Verre de cidre (20 cl)": 200,
        "Bouteille (75cl)": 750, "Autre": None
    }
}

# Ajouter une consommation
def add_consumption(user, df):
    st.title(f"🍻 Ajouter une consommation pour {user}")

    date = st.date_input("📅 Sélectionnez la date", datetime.today())
    type_boisson = st.selectbox("🔍 Type de boisson", list(DRINKS_DATA.keys()))
    boisson = st.selectbox("🍹 Sélectionnez la boisson", list(DRINKS_DATA[type_boisson].keys()))

    step_values = {"🍺 Bière": 0.1, "🍷 Vin": 0.5, "🥃 Hard": 2.0, "🍾 Autres": 1.0}
    step = step_values[type_boisson]

    default_degree = DRINKS_DATA[type_boisson].get(boisson, 0.0)
    degree = st.number_input("✏️ Degré d'alcool (%)", min_value=0.0, max_value=100.0, value=default_degree, step=step)

    taille = st.selectbox("📏 Taille du verre", list(GLASS_SIZES[type_boisson].keys()))

    if taille == "Autre":
        volume_cl = st.number_input("🔢 Quantité d'alcool (en cl)", min_value=1, max_value=50, step=1, value=10)
        volume_ml = volume_cl * 10
    else:
        volume_ml = GLASS_SIZES[type_boisson][taille]

    quantite = st.number_input("🔢 Quantité consommée", min_value=1, max_value=20, step=1)

    total_volume = (volume_ml * quantite) / 1000
    alcool_pur_volume = total_volume * (degree / 100)
    alcool_grams = alcool_pur_volume * 1000 * 0.8

    st.write(f"💧 Volume total : {total_volume:.2f} L")
    st.write(f"🍸 Alcool pur : {alcool_grams:.2f} g")

    if st.button("💾 Enregistrer la consommation"):
        worksheet = get_worksheet(SHEET, user)
        new_data = pd.DataFrame([[date.strftime('%Y-%m-%d'), type_boisson, boisson, degree, taille, quantite, alcool_grams, total_volume]],
                                columns=["Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"])

        updated_df = pd.concat([df, new_data], ignore_index=True)
        set_with_dataframe(worksheet, updated_df)

        st.cache_data.clear()
        st.success(f"✅ {quantite} x {taille} de {boisson} ajouté ({alcool_grams:.2f} g) !")
        st.rerun()

# Gérer les consommations
def manage_consumptions(user, df):
    st.title("🗑️ Gestion des consommations")

    if df.empty:
        st.info(f"Aucune consommation enregistrée pour {user}.")
        return

    df_display = df[::-1].reset_index()

    st.markdown("### 📋 Consommations récentes")

    header = st.columns([2, 3, 2, 2, 1])
    header[0].markdown("**📅 Date**")
    header[1].markdown("**🍻 Type - Boisson**")
    header[2].markdown("**📏 Taille x Qté**")
    header[3].markdown("**Alcool**")
    header[4].markdown("**❌**")

    for _, row in df_display.iterrows():
        cols = st.columns([2, 3, 2, 2, 1])
        cols[0].write(f"{row['Date']}")
        cols[1].write(f"{row['Type']} - {row['Boisson']}")
        cols[2].write(f"{row['Taille']} x{int(row['Quantité'])}")
        cols[3].write(f"{row['Alcool en grammes']:.1f} g")
        if cols[4].button("❌", key=f"delete_{row['index']}"):
            delete_consumption(user, row['index'])
            st.rerun()

# Suppression d'une ligne
def delete_consumption(user, row_index):
    worksheet = get_worksheet(SHEET, user)
    if worksheet is None:
        st.error(f"❌ Impossible d'accéder à la feuille de {user}.")
        return

    df = load_consumptions(user)
    if df.empty:
        st.warning("⚠️ Aucune donnée trouvée.")
        return

    if row_index in df.index:
        df = df.drop(row_index).reset_index(drop=True)
        worksheet.clear()
        set_with_dataframe(worksheet, df)
        st.cache_data.clear()
        st.success("✅ Consommation supprimée avec succès !")
        st.rerun()
    else:
        st.warning(f"⚠️ Ligne {row_index} introuvable.")