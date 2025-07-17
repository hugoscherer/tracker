from google_sheets_utils import authenticate_gsheets, get_worksheet
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import streamlit as st

SHEET = authenticate_gsheets()

# Charger les utilisateurs
def load_users():
    worksheet = get_worksheet(SHEET, "Users")
    if worksheet is None:
        st.error("❌ Feuille 'Users' introuvable.")
        return []

    try:
        df = get_as_dataframe(worksheet)
        df.columns = df.columns.str.lower().str.strip()  # Normalisation
        df = df.dropna(subset=['prenom'])
        return df['prenom'].tolist() if not df.empty else []
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des utilisateurs : {e}")
        return []

# Ajouter un utilisateur
def add_user(prenom):
    worksheet = get_worksheet(SHEET, "Users")
    if worksheet is None:
        st.error("❌ Feuille 'Users' introuvable.")
        return False

    try:
        df = get_as_dataframe(worksheet)
        df.columns = df.columns.str.lower().str.strip()
        df = df.dropna(subset=['prenom'])

        if prenom in df['prenom'].values:
            return False  # L'utilisateur existe déjà

        new_data = pd.DataFrame([[prenom]], columns=["prenom"])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        set_with_dataframe(worksheet, updated_df)
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de l'ajout de l'utilisateur : {e}")
        return False
