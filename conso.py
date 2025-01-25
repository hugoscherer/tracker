import streamlit as st
import pandas as pd
import os
import altair as alt
from datetime import datetime

# Définition des fichiers CSV
ALCOHOL_FOLDER = "alcohol_data"
USERS_CSV = "users.csv"

# Vérification et création des fichiers nécessaires
def initialize_files():
    if not os.path.exists(ALCOHOL_FOLDER):
        os.makedirs(ALCOHOL_FOLDER)
    if not os.path.exists(USERS_CSV):
        pd.DataFrame(columns=["prenom"]).to_csv(USERS_CSV, index=False)

# Fonction pour charger les utilisateurs
def load_users():
    return pd.read_csv(USERS_CSV)["prenom"].tolist()

# Fonction pour charger les consommations d'un utilisateur
def load_user_data(user_file):
    if os.path.exists(user_file):
        df = pd.read_csv(user_file)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        return df.dropna(subset=["Date"])
    return pd.DataFrame(columns=["Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"])

# Fonction pour ajouter un utilisateur
def add_user(prenom):
    users = load_users()
    if prenom not in users:
        df = pd.read_csv(USERS_CSV)
        df = pd.concat([df, pd.DataFrame([{"prenom": prenom}])], ignore_index=True)
        df.to_csv(USERS_CSV, index=False)
        user_file = os.path.join(ALCOHOL_FOLDER, f"{prenom}.csv")
        pd.DataFrame(columns=["Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"]).to_csv(user_file, index=False)
        return True
    return False

# Fonction d'ajout de consommation
def add_consumption(user_file, selected_user):
    st.title(f"🍻 Ajout d'une consommation pour {selected_user}")
    
    # Sélection de la date (par défaut aujourd'hui)
    date = st.date_input("📅 Sélectionnez la date", datetime.today())
    
    ALCOHOL_TYPES = ["🍺 Bière", "🍷 Vin", "🥃 Hard", "🍾 Autres"]
    
    BEERS = {"Affligem": 6.7, "Bête": 8.0, "Kronenbourg": 4.2, "Blonde classique" : 4.5, "Heineken": 5.0, "1664": 5.5, "Leffe": 6.6, "Desperados": 5.9, "Corona": 4.5, "Chouffe": 8.0, "Autre": None}
    WINES = {"Rouge": 12.5, "Blanc": 11.0, "Rosé": 12.0}
    HARD_ALCOHOLS = {"Rhum": 40.0, "Vodka": 40.0, "Tequila": 38.0, "Whisky": 40.0, "Gin": 37.5, "Autre": None}
    OTHER_ALCOHOLS = {"Cidre": 4.0, "Champagne": 12.0, "Autre": None}
    
    GLASS_SIZES = {
        "🍺 Bière": { "Pinte (50cl)": 500,  "Bouteille (33cl)": 330, "Demi (25cl)": 250},
        "🍷 Vin": {"Verre de vin (15cl)": 150, "Bouteille (75cl)": 750},
        "🥃 Hard": {"Shot (3cl)": 30, "Verre soirée (20cl)": 200, "Cocktail (25cl)": 250},
        "🍾 Autres": {"Verre de vin (15cl)": 150, "Bouteille (33cl)": 330, "Cocktail (25cl)": 250}
    }
    
    type_boisson = st.selectbox("🔍 Sélectionnez un type de boisson", ALCOHOL_TYPES)
    boisson = st.selectbox("🍹 Sélectionnez la boisson", list(BEERS.keys() if "Bière" in type_boisson else WINES.keys() if "Vin" in type_boisson else HARD_ALCOHOLS.keys() if "Hard" in type_boisson else OTHER_ALCOHOLS.keys()))
    
    degree = BEERS.get(boisson) or WINES.get(boisson) or HARD_ALCOHOLS.get(boisson) or OTHER_ALCOHOLS.get(boisson)
    if type_boisson == "🍺 Bière" and boisson == "Autre":
        degree = st.number_input("✏️ Entrez le degré d'alcool", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
    if type_boisson == "🥃 Hard" and boisson == "Autre":
        degree = st.number_input("✏️ Entrez le degré d'alcool", min_value=0.0, max_value=100.0, value=40, step=1)
    if type_boisson == "🍾 Autres" and boisson == "Autre":
        degree = st.number_input("✏️ Entrez le degré d'alcool", min_value=0.0, max_value=100.0, value=10, step=0.5)

    taille = st.selectbox("📏 Sélectionnez la taille du verre", list(GLASS_SIZES[type_boisson].keys()))
    volume_ml = GLASS_SIZES[type_boisson][taille]
    
    quantite = st.number_input("🔢 Quantité consommée", min_value=1, max_value=20, step=1)
    total_volume = (volume_ml * quantite) / 1000  # Conversion en litres

    # Ajustement pour les cocktails et verres soirée
    if "Cocktail" in taille:
        total_volume *= 40 / 250  # Ratio d'alcool dans un cocktail (~16%)
    elif "Verre soirée" in taille:
        total_volume *= 1/3  # Supposons qu'un verre de soirée contient 1/3 d'alcool

    alcool_grams = (total_volume * 1000) * (degree / 100) * 0.8

    
    if st.button("💾 Enregistrer la consommation"):
        df = pd.DataFrame([{ 
            "Date": date.strftime('%Y-%m-%d'), 
            "Type": type_boisson, 
            "Boisson": boisson, 
            "Degré d'alcool": degree, 
            "Taille": taille, 
            "Quantité": quantite, 
            "Alcool en grammes": alcool_grams, 
            "Volume en litres": total_volume 
        }])
        
        df.to_csv(user_file, index=False, mode='a', header=not os.path.exists(user_file))
        
        st.success(f"✅ {quantite} x {taille} de {boisson} ajouté avec {degree}% d'alcool (Total : {alcool_grams:.2f} g d'alcool, {total_volume:.2f} L)")
