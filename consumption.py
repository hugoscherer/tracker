import streamlit as st
import pandas as pd
from google_sheets_utils import authenticate_gsheets, get_worksheet
from datetime import datetime
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# Authentification Google Sheets
SHEET = authenticate_gsheets()

# 🔍 Données des boissons prédéfinies avec leur degré d'alcool
DRINKS_DATA = {
    "🍺 Bière": {
        "Affligem": 6.7,
        "Bête": 8.0,
        "1664": 5.5,
        "Chouffe": 8.0,
        "Kronenbourg": 4.2,
        "Blonde classique de bar": 4.5,
        "Leffe": 6.6,
        "Heineken": 5.0,
        "Desperados": 5.9,
        "Corona": 4.5,
        "Autre": None
    },
    "🍷 Vin": {
        "Rouge": 12.5,
        "Blanc": 11.0,
        "Rosé": 12.0
    },
    "🥃 Hard": {
        "Vodka": 40.0,
        "Rhum": 40.0,
        "Whisky": 40.0,
        "Tequila": 38.0,
        "Gin": 37.5,
        "Autre": None
    },
    "🍾 Autres": {
        "Champagne": 12.0,
        "Cidre": 4.5,
        "Pastis": 45.0,
        "Autre": None
    }
}

# 📏 Tailles des verres en fonction des types de boissons
GLASS_SIZES = {
    "🍺 Bière": {
        "Pinte (50cl)": 500,
        "Bouteille (33cl)": 330,
        "Demi (25cl)": 250
    },
    "🍷 Vin": {
        "Verre de vin (15cl)": 150,
        "Bouteille (75cl)": 750
    },
    "🥃 Hard": {
        "Shot (3cl)": 30,
        "Verre soirée (20cl)": 60,
        "Cocktail (25cl)": 40
    },
    "🍾 Autres": {
        "Coupe champagne (15 cl)": 150,
        "Bouteille (75cl)": 750,
        "Verre (20 cl)": 200,
        "Ricard (2 cl)": 20
    }
}

# 🔄 Charger les consommations d'un utilisateur
def load_consumptions(user):
    worksheet = get_worksheet(SHEET, user)
    df = get_as_dataframe(worksheet).dropna(how='all')
    return df if not df.empty else pd.DataFrame(columns=["Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"])

# 🍻 Ajouter une consommation
def add_consumption(user):
    st.title(f"🍻 Ajouter une consommation pour {user}")

    # Sélection des données
    date = st.date_input("📅 Sélectionnez la date", datetime.today())
    type_boisson = st.selectbox("🔍 Type de boisson", list(DRINKS_DATA.keys()))
    boisson = st.selectbox("🍹 Sélectionnez la boisson", list(DRINKS_DATA[type_boisson].keys()))

    # Pré-remplissage du degré d'alcool
    default_degree = DRINKS_DATA[type_boisson].get(boisson, 0) or 0
    degree = st.number_input("✏️ Degré d'alcool (%)", min_value=0.0, max_value=100.0, value=default_degree, step=0.1)

    # Sélection de la taille du verre
    taille = st.selectbox("📏 Sélectionnez la taille du verre", list(GLASS_SIZES[type_boisson].keys()))
    
    volume_ml = GLASS_SIZES[type_boisson][taille]
    # Quantité consommée
    quantite = st.number_input("🔢 Quantité consommée", min_value=1, max_value=20, step=1)

    # Calcul du volume total en litres
    total_volume = (volume_ml * quantite) / 1000  # Volume total consommé
    alcool_pur_volume = total_volume * (degree / 100)

    # Conversion en grammes d'alcool pur (densité de l'alcool : 0.8 g/ml)
    alcool_grams = alcool_pur_volume * 1000 * 0.8  # Conversion en grammes

    # Affichage des résultats (facultatif pour vérifier les calculs)
    st.write(f"Total Volume: {total_volume:.2f} L")
    st.write(f"Alcool pur: {alcool_pur_volume:.2f} L")
    st.write(f"Alcool en grammes: {alcool_grams:.2f} g")


    # Bouton d'enregistrement
    if st.button("💾 Enregistrer la consommation"):
        worksheet = get_worksheet(SHEET, user)
        df = load_consumptions(user)

        new_data = pd.DataFrame([[date.strftime('%Y-%m-%d'), type_boisson, boisson, degree, taille, quantite, alcool_grams, total_volume]],
                                columns=["Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"])

        updated_df = pd.concat([df, new_data], ignore_index=True)
        set_with_dataframe(worksheet, updated_df)

        st.success(f"✅ {quantite} x {taille} de {boisson} ajouté ({alcool_grams:.2f} g d'alcool, {total_volume:.2f} L) !")
