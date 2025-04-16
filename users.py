from google_sheets_utils import authenticate_gsheets, get_worksheet
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe

SHEET = authenticate_gsheets()

# Charger les utilisateurs
def load_users():
    worksheet = get_worksheet(SHEET, "Users")
    df = get_as_dataframe(worksheet).dropna(subset=['prenom'])
    return df['prenom'].tolist() if not df.empty else []

# Ajouter un utilisateur
def add_user(prenom):
    worksheet = get_worksheet(SHEET, "Users")
    df = get_as_dataframe(worksheet).dropna(subset=['prenom'])
    
    if prenom in df['prenom'].values:
        return False  # L'utilisateur existe déjà

    new_data = pd.DataFrame([[prenom]], columns=["prenom"])
    updated_df = pd.concat([df, new_data], ignore_index=True)
    set_with_dataframe(worksheet, updated_df)
    return True
