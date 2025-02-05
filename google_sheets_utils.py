import streamlit as st
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import pandas as pd
import json
from google.oauth2.service_account import Credentials

# ✅ Authentification avec Google Sheets via les secrets Streamlit
def authenticate_gsheets():
    # 🔐 Charger les credentials depuis les secrets
    credentials_json = st.secrets["google"]["credentials"]
    
    # Convertir la chaîne JSON en dictionnaire Python
    credentials_info = json.loads(credentials_json)
    
    # Créer des credentials Google à partir du JSON
    credentials = Credentials.from_service_account_info(credentials_info)
    
    # 🔗 Connexion à Google Sheets
    gc = gspread.authorize(credentials)
    
    # 📊 Ouvrir le Google Sheet par son ID
    sheet = gc.open_by_key('1OG1bH9gshq6Kl6H0nZq_7jhACN6lH2jX9_1U5nuinZg')  # Remplace par l'ID de ton Google Sheet
    return sheet

# 📋 Récupérer un onglet spécifique (worksheet)
def get_worksheet(sheet, worksheet_name):
    try:
        # Tenter de récupérer l'onglet existant
        return sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # S'il n'existe pas, le créer
        return sheet.add_worksheet(title=worksheet_name, rows="1000", cols="10")