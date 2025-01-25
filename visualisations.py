import streamlit as st
import pandas as pd
import os
import altair as alt
import streamlit.components.v1 as components


# Définition des fichiers CSV
ALCOHOL_FOLDER = "alcohol_data"
USERS_CSV = "users.csv"

# Fonction pour charger les utilisateurs
def load_users():
    return pd.read_csv(USERS_CSV)["prenom"].tolist()

# Fonction pour charger les consommations d'un utilisateur
def load_user_data(user_file):
    if os.path.exists(user_file):
        df = pd.read_csv(user_file)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        return df
    return pd.DataFrame(columns=["Date", "Type", "Boisson", "Degré d'alcool", "Taille", "Quantité", "Alcool en grammes", "Volume en litres"])

# Fonction pour charger toutes les consommations
def load_all_data():
    users = load_users()
    all_data = []
    for user in users:
        user_file = os.path.join(ALCOHOL_FOLDER, f"{user}.csv")
        df = load_user_data(user_file)
        df["Utilisateur"] = user
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Fonction de visualisation
def visualize_consumption():
    st.title("📊 Visualisation des consommations")
    df = load_all_data()
    
    if df.empty:
        st.warning("Aucune donnée disponible.")
        return
    
    # Filtrage par utilisateur
    users = load_users()
    selected_user = st.selectbox("👤 Sélectionnez un utilisateur ou 'Tous'", ["Tous"] + users)

    # Classement des utilisateurs en fonction de la consommation totale d'alcool
    top_users = df.groupby("Utilisateur")["Alcool en grammes"].sum().reset_index()
    top_users = top_users.sort_values(by="Alcool en grammes", ascending=False).reset_index(drop=True)

    # Vérification qu'il y a au moins 3 utilisateurs
    if len(top_users) >= 3:
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
            <div class="podium-box bronze">
                <div class="podium-user">{top_users.iloc[2]['Utilisateur']}</div>
                <div class="podium-score">{top_users.iloc[2]['Alcool en grammes']:.2f} g</div>
                <div class="podium-rank">🥉</div>
            </div>
            <div class="podium-box gold">
                <div class="podium-user">{top_users.iloc[0]['Utilisateur']}</div>
                <div class="podium-score">{top_users.iloc[0]['Alcool en grammes']:.2f} g</div>
                <div class="podium-rank">🥇</div>
            </div>
            <div class="podium-box silver">
                <div class="podium-user">{top_users.iloc[1]['Utilisateur']}</div>
                <div class="podium-score">{top_users.iloc[1]['Alcool en grammes']:.2f} g</div>
                <div class="podium-rank">🥈</div>
            </div>
        </div>
        """
        components.html(podium_html, height=250)

    if selected_user != "Tous":
        df = df[df["Utilisateur"] == selected_user]
    
    # Indicateurs clés
    total_pintes = df[df["Taille"].str.contains("Pinte", na=False)]["Quantité"].sum()
    total_vin = df[df["Boisson"].str.contains("Rouge|Blanc|Rosé", na=False)]["Volume en litres"].sum() / 0.75
    total_hard = df[df["Type"].str.contains("Hard", na=False)]["Volume en litres"].sum() / 0.7
    total_alcool_grams = df["Alcool en grammes"].sum()
    total_volume_litres = df["Volume en litres"].sum()
    
    st.metric("🍺 Pintes bues", int(total_pintes))
    st.metric("🍷 Bouteilles de vin bues", int(total_vin))
    st.metric("🥃 Bouteilles de hard bues", int(total_hard))
    st.metric("💪 Alcool total (g)", f"{total_alcool_grams:.2f} g")
    st.metric("🧴 Volume total consommé", f"{total_volume_litres:.2f} L")
    
    # Évolution de la consommation cumulée
    df["Mois"] = df["Date"].dt.strftime('%Y-%m')
    df = df.sort_values("Date")
    df["Cumul Alcool"] = df["Alcool en grammes"].cumsum()
    
    chart_trend = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Cumul Alcool", title="Alcool en grammes cumulé"),
        color=alt.Color("Utilisateur", scale=alt.Scale(scheme='set2')),
        tooltip=["Date", "Utilisateur", "Cumul Alcool"]
    ).properties(title="📈 Évolution cumulée de la consommation")
    st.altair_chart(chart_trend, use_container_width=True)
    
    if selected_user == "Tous":
        
        chart_comparison = alt.Chart(df).mark_bar().encode(
            x=alt.X("Utilisateur", title="Utilisateur", sort="-y"),
            y=alt.Y("sum(Alcool en grammes)", title="Alcool consommé en grammes"),
            color=alt.Color("Type", scale=alt.Scale(scheme='tableau10')),
            tooltip=["Utilisateur", "Type", "sum(Alcool en grammes)"]
        ).properties(title="🏆 Classement des utilisateurs")
        st.altair_chart(chart_comparison, use_container_width=True)
    else:
        chart_type = alt.Chart(df).mark_bar().encode(
            x=alt.X("Type", title="Type d'alcool"),
            y=alt.Y("sum(Alcool en grammes)", title="Alcool en grammes"),
            color=alt.Color("Type", scale=alt.Scale(scheme='tableau10')),
            tooltip=["Type", "sum(Alcool en grammes)"]
        ).properties(title="📌 Répartition des types d'alcool")
        st.altair_chart(chart_type, use_container_width=True)
    
    if selected_user == "Tous":
        df_beers = df[df["Type"] == "🍺 Bière"].copy()
    else:
        df_beers = df[(df["Type"] == "🍺 Bière") & (df["Utilisateur"] == selected_user)].copy()

    df_beers["Pintes"] = (df_beers["Volume en litres"] / 0.5).astype(int)  # Conversion en unités de pintes

    if selected_user == "Tous":
        top_beers = df_beers.groupby(["Utilisateur", "Boisson"])["Pintes"].sum().reset_index()
        top_beers = top_beers.groupby("Utilisateur").apply(lambda x: x.nlargest(5, "Pintes")).reset_index(drop=True)
    else:
        top_beers = df_beers.groupby("Boisson")["Pintes"].sum().nlargest(5).reset_index()

    chart_beers = alt.Chart(top_beers).mark_bar().encode(
        x=alt.X("Boisson", title="Bière"),
        y=alt.Y("Pintes", title="Nombre de pintes"),
        color=alt.Color("Boisson", scale=alt.Scale(scheme='set3')),
        tooltip=["Boisson", "Pintes"]
    ).properties(title="🍺 Top 5 des bières consommées en pintes")
    st.altair_chart(chart_beers, use_container_width=True)

    import random

    if selected_user == "Tous":
        df_hard = df[df["Type"] == "🥃 Hard"].copy()
    else:
        df_hard = df[(df["Type"] == "🥃 Hard") & (df["Utilisateur"] == selected_user)].copy()

    if selected_user == "Tous":
        top_hard = df_hard.groupby(["Utilisateur", "Boisson"])["Volume en litres"].sum().reset_index()
        top_hard = top_hard.groupby("Utilisateur").apply(lambda x: x.nlargest(5, "Volume en litres")).reset_index(drop=True)
    else:
        top_hard = df_hard.groupby("Boisson")["Volume en litres"].sum().nlargest(5).reset_index()

    # Mélanger l'ordre des boissons pour varier les couleurs attribuées
    boissons = top_hard["Boisson"].tolist()
    random.shuffle(boissons)
    top_hard["Boisson"] = boissons

    chart_hard = alt.Chart(top_hard).mark_bar().encode(
        x=alt.X("Boisson", title="Alcool fort"),
        y=alt.Y("Volume en litres", title="Volume total consommé (L)"),
        color=alt.Color("Boisson", scale=alt.Scale(scheme="tableau10")),  # Garde les mêmes couleurs mais les mélange
        tooltip=["Boisson", "Volume en litres"]
    ).properties(title="🥃 Top 5 des alcools forts consommés")
    st.altair_chart(chart_hard, use_container_width=True)




# Exécution
if __name__ == "__main__":
    visualize_consumption()
