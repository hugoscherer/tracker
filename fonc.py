# helpers/utils.py

import pandas as pd
from google_sheets_utils import authenticate_gsheets, get_worksheet
from gspread_dataframe import get_as_dataframe
from users import load_users

# Chargement des consommations

def load_all_data():
    """Charge toutes les consommations de tous les utilisateurs."""
    SHEET = authenticate_gsheets()
    users = load_users()
    all_data = []
    for user in users:
        worksheet = get_worksheet(SHEET, user)
        if worksheet is not None:
            df = get_as_dataframe(worksheet).dropna(how='all')
            df["Utilisateur"] = user
            all_data.append(df)
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Leader par type de boisson

def get_top_user(df, condition):
    """Retourne l'utilisateur top consommateur d'un sous-ensemble."""
    filtered = df[condition]
    if filtered.empty:
        return None
    top = filtered.groupby("Utilisateur")["Volume en litres"].sum().reset_index()
    return top.sort_values(by="Volume en litres", ascending=False).head(1)

def top_user(df, filtre):
    df_filtered = df[filtre]
    if df_filtered.empty:
        return None
    return df_filtered.groupby("Utilisateur")[["Volume en litres", "Alcool en grammes"]].sum().reset_index().sort_values(by="Volume en litres", ascending=False).head(1)

# Indicateurs globaux

def compute_indicators(df):
    """Calcule les indicateurs de base pour une période donnée."""
    df_biere = df[df["Type"] == "🍺 Bière"]
    total_pintes = df_biere["Volume en litres"].sum() / 0.5
    total_vin = df[df["Boisson"].isin(["Rouge", "Blanc", "Rosé"])]
    total_bouteilles_vin = total_vin["Volume en litres"].sum() / 0.75
    total_hard = df[df["Type"].str.contains("Hard")]["Volume en litres"].sum() / 0.7
    total_alcool = df["Alcool en grammes"].sum()
    total_volume = df["Volume en litres"].sum()

    return {
        "pintes": int(total_pintes),
        "bouteilles_vin": int(total_bouteilles_vin),
        "bouteilles_hard": int(total_hard),
        "alcool_g": total_alcool,
        "volume_l": total_volume,
    }

# Podium HTML

def generate_podium(df):
    podium_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        .podium-container {{
            text-align: center;
            display: flex;
            justify-content: center;
            gap: 20px;
            font-family: 'Inter', sans-serif;
            align-items: flex-end;
        }}
        .podium-box {{
            width: 120px;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
        }}
        .gold {{ background-color: gold; height: 200px; }}
        .silver {{ background-color: silver; height: 170px; }}
        .bronze {{ background-color: #cd7f32; height: 150px; }}
        .podium-rank {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .podium-user {{
            font-size: 16px;
            font-weight: 600;
            margin-top: auto;
        }}
        .podium-score {{
            font-size: 14px;
            font-weight: 400;
        }}
    </style>
    <div class="podium-container">
    """

    positions = [
        ("silver", "🥈", 1),
        ("gold", "🥇", 0),
        ("bronze", "🥉", 2)
    ]

    for css_class, emoji, df_index in positions:
        if df_index < len(df):
            user = df.iloc[df_index]
            user_html = f"""
            <div class="podium-box {css_class}">
                <div class="podium-user">{user['Utilisateur']}</div>
                <div class="podium-score">{user['Alcool en grammes']:.2f} g</div>
                <div class="podium-rank">{emoji}</div>
            </div>
            """
        else:
            user_html = f"""
            <div class="podium-box {css_class}">
                <div class="podium-user">—</div>
                <div class="podium-score">0.00 g</div>
                <div class="podium-rank">{emoji}</div>
            </div>
            """
        podium_html += user_html

    podium_html += "</div>"
    return podium_html