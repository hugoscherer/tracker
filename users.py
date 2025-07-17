from google_sheets_utils import authenticate_gsheets, get_worksheet
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import streamlit as st

SHEET = authenticate_gsheets()

def load_users(force_reload=False):
    """
    Charge la liste des utilisateurs depuis Google Sheets,
    ou depuis st.session_state si déjà chargé (sauf si force_reload=True).
    """
    if "users_list" not in st.session_state or force_reload:
        worksheet = get_worksheet(SHEET, "Users")
        if worksheet is None:
            st.error("❌ Feuille 'Users' introuvable.")
            st.session_state["users_list"] = []
            return []

        try:
            df = get_as_dataframe(worksheet)
            df.columns = df.columns.str.lower().str.strip()
            df = df.dropna(subset=['prenom'])
            st.session_state["users_list"] = df['prenom'].tolist() if not df.empty else []
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des utilisateurs : {e}")
            st.session_state["users_list"] = []

    return st.session_state["users_list"]

def add_user(prenom):
    worksheet = get_worksheet(SHEET, "Users")
    if worksheet is None:
        st.error("❌ Feuille 'Users' introuvable.")
        return False

    try:
        # On récupère la liste depuis la session pour éviter un nouvel appel
        users = load_users()
        if prenom in users:
            return False  # L'utilisateur existe déjà

        # On ajoute en local dans la session et dans Google Sheets
        users.append(prenom)
        st.session_state["users_list"] = users

        # Mise à jour Google Sheets
        new_data = pd.DataFrame(users, columns=["prenom"])
        set_with_dataframe(worksheet, new_data)
        return True
    except Exception as e:
        st.error(f"❌ Erreur lors de l'ajout de l'utilisateur : {e}")
        return False
