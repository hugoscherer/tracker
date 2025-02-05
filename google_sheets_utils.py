import streamlit as st
import gspread
import pandas as pd
import json
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def authenticate_gsheets():
    try:
        credentials_json = st.secrets["google"]["credentials"]
        credentials_info = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key('1OG1bH9gshq6Kl6H0nZq_7jhACN6lH2jX9_1U5nuinZg')
        return sheet
    except Exception:
        return None

def get_worksheet(sheet, worksheet_name):
    if sheet is None:
        return None

    try:
        worksheet = sheet.worksheet(worksheet_name)
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        try:
            worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="10")
            return worksheet
        except Exception:
            return None
    except Exception:
        return None
