import streamlit as st
import pandas as pd
from google_sheets_utils import authenticate_gsheets, get_worksheet
from datetime import datetime
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from users import *
import time

# Authentification Google Sheets
SHEET = authenticate_gsheets()

@st.cache_data
def load_consumptions(user):
    worksheet = get_worksheet(SHEET, user)
    df = get_as_dataframe(worksheet).dropna(how='all') if worksheet else pd.DataFrame(columns=[
        "Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"
    ])

    # 🔐 Forcer certaines colonnes en texte, pour éviter 1664 → int
    for col in ["Type", "Boisson", "Taille"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    return df

# 🔍 Données des boissons prédéfinies avec leur degré d'alcool
DRINKS_DATA = {
    "🍺 Bière": {
        "Affligem": 6.7,
        "Bête": 8.0,
        "1664": 5.5,
        "Chouffe": 8.0,
        "Kronenbourg": 4.2,
        "Blonde bar": 4.5,
        "Leffe": 6.6,
        "Heineken": 5.0,
        "Desperados": 5.9,
        "Corona": 4.5,
        "IPA": 6.0,
        "Pelforth": 5.8,
        "Autre": 5.0
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
        "Pastis": 45.0,
        "Autre": 40.0
    },
    "🍾 Autres": {
        "Champagne": 12.0,
        "Cidre": 4.5,
        "Liqueur": 20.0,
        "Autre": 10.0
    }
}

# 📏 Tailles des verres en fonction des types de boissons
GLASS_SIZES = {
    "🍺 Bière": {
        "Pinte (50cl)": 500,
        "Bouteille (33cl)": 330,
        "Demi (25cl)": 250,
        "Autre": None
    },
    "🍷 Vin": {
        "Verre de vin (15cl)": 150,
        "Bouteille (75cl)": 750,
        "Autre": None
    },
    "🥃 Hard": {
        "Shot (3cl)": 30,
        "Verre soirée (20cl)": 60,
        "Cocktail (25cl)": 40,
        "Ricard (2cl)": 20,
        "Autre": None
    },
    "🍾 Autres": {
        "Coupe champagne (15 cl)": 150,
        "Verre de cidre (20 cl)": 200,
        "Bouteille (75cl)": 750,
        "Autre": None
    }
}

def add_consumption(user):
    st.title(f"🍻 Ajouter une consommation pour {user}")

    # Sélection des données
    date = st.date_input("📅 Sélectionnez la date", datetime.today())
    type_boisson = st.selectbox("🔍 Type de boisson", list(DRINKS_DATA.keys()))
    boisson = st.selectbox("🍹 Sélectionnez la boisson", list(DRINKS_DATA[type_boisson].keys()))

    # Définition du step dynamique en fonction du type de boisson
    step_values = {
        "🍺 Bière": 0.1,
        "🍷 Vin": 0.5,
        "🥃 Hard": 2.0,
        "🍾 Autres": 1.0
    }
    step = step_values[type_boisson]

    # Pré-remplissage du degré d'alcool
    default_degree = DRINKS_DATA[type_boisson].get(boisson, 0.0) or 0.0
    degree = st.number_input("✏️ Degré d'alcool (%)", min_value=0.0, max_value=100.0, value=default_degree, step=step)

    # Sélection de la taille du verre
    taille = st.selectbox("📏 Sélectionnez la taille du verre", list(GLASS_SIZES[type_boisson].keys()))

    # Si l'utilisateur sélectionne "Autre", permettre une saisie manuelle du volume
    if taille == "Autre":
        volume_cl = st.number_input("🔢 Entrez la quantité d'alcool en cl", min_value=1, max_value=50, step=1, value=10)
        volume_ml = volume_cl * 10
    else:
        volume_ml = GLASS_SIZES[type_boisson][taille]

    # Quantité consommée
    quantite = st.number_input("🔢 Quantité consommée", min_value=1, max_value=20, step=1)

    # Calcul du volume total en litres
    total_volume = (volume_ml * quantite) / 1000  # Volume total consommé
    alcool_pur_volume = total_volume * (degree / 100)

    # Conversion en grammes d'alcool pur (densité de l'alcool : 0.8 g/ml)
    alcool_grams = alcool_pur_volume * 1000 * 0.8  # Conversion en grammes

    # Affichage des résultats
    st.write(f"Total Volume Alcool: {total_volume:.2f} L")
    st.write(f"Alcool en grammes: {alcool_grams:.2f} g")

    # Bouton d'enregistrement
    if st.button("💾 Enregistrer la consommation"):
        worksheet = get_worksheet(SHEET, user)
        df = load_consumptions(user)  # Chargement depuis le cache

        new_data = pd.DataFrame([[date.strftime('%Y-%m-%d'), type_boisson, boisson, degree, taille, quantite, alcool_grams, total_volume]],
                                columns=["Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"])

        updated_df = pd.concat([df, new_data], ignore_index=True)
        set_with_dataframe(worksheet, updated_df)  # Enregistrement

        st.cache_data.clear()  # 🚀 Invalide le cache pour recharger les données
        st.success(f"✅ {quantite} x {taille} de {boisson} ajouté ({alcool_grams:.2f} g d'alcool, {total_volume:.2f} L) !")
        st.rerun()  # 🔄 Recharge la page pour afficher les nouvelles données

def manage_consumptions(selected_user):
    st.title("🗑️ Gestion des consommations")

    df = load_consumptions(selected_user)
    if df.empty:
        st.info(f"Aucune consommation enregistrée pour {selected_user}.")
        return

    df_display = df[::-1].reset_index()  # garder index original

    st.markdown("### 📋 Consommations récentes")

    # En-tête du tableau
    header = st.columns([2, 3, 2, 2, 1])
    header[0].markdown("**📅 Date**")
    header[1].markdown("**🍻 Type - Boisson**")
    header[2].markdown("**📏 Taille x Qté**")
    header[3].markdown("**Alcool**")
    header[4].markdown("**Delete**")

    # Corps du tableau
    for _, row in df_display.iterrows():
        cols = st.columns([2, 3, 2, 2, 1])
        cols[0].write(f"{row['Date']}")
        cols[1].write(f"{row['Type']} - {row['Boisson']}")
        cols[2].write(f"{row['Taille']} x{int(row['Quantité'])}")
        cols[3].write(f"{row['Alcool en grammes']:.1f} g")
        if cols[4].button("❌", key=f"delete_{row['index']}"):
            delete_consumption(selected_user, row['index'])
            st.rerun()
                       
def delete_consumption(user, row_index):
    """ Supprime une consommation spécifique et met à jour Google Sheets """
    worksheet = get_worksheet(SHEET, user)
    
    if worksheet is None:
        st.error(f"❌ Erreur : Impossible d'accéder à la feuille de {user}. Vérifiez votre connexion Google Sheets.")
        return

    df = load_consumptions(user)

    if df.empty:
        st.warning("⚠️ Aucune donnée trouvée, impossible de supprimer une consommation.")
        return

    if row_index in df.index:
        df = df.drop(row_index).reset_index(drop=True)  # Supprimer la ligne et réindexer

        # ✅ Écriture optimisée : supprimer puis réécrire les nouvelles données
        worksheet.clear()  # Efface tout le contenu de la feuille
        set_with_dataframe(worksheet, df)  # Réécrit les données mises à jour

        st.cache_data.clear()  # 🚀 Invalide le cache pour recharger correctement
        st.success("✅ Consommation supprimée avec succès !")
        
        st.rerun()  # 🔄 Recharge immédiatement la page
    else:
        st.warning(f"⚠️ Impossible de supprimer la consommation, la ligne {row_index} n'existe pas.")