import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import altair as alt
from google_sheets_utils import authenticate_gsheets, get_worksheet
from users import load_users
from gspread_dataframe import get_as_dataframe

SHEET = authenticate_gsheets()

# Charger toutes les consommations
def load_all_data():
    users = load_users()
    all_data = []
    for user in users:
        df = get_as_dataframe(get_worksheet(SHEET, user)).dropna(how='all')
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

    # Filtrer les données en fonction de la sélection
    if selected_user != "Tous":
        df_filtered = df[df["Utilisateur"] == selected_user]
    else:
        df_filtered = df.copy()

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
            <div class="podium-box silver">
                <div class="podium-user">{top_users.iloc[1]['Utilisateur']}</div>
                <div class="podium-score">{top_users.iloc[1]['Alcool en grammes']:.2f} g</div>
                <div class="podium-rank">🥈</div>
            </div>
            <div class="podium-box gold">
                <div class="podium-user">{top_users.iloc[0]['Utilisateur']}</div>
                <div class="podium-score">{top_users.iloc[0]['Alcool en grammes']:.2f} g</div>
                <div class="podium-rank">🥇</div>
            </div>
            <div class="podium-box bronze">
                <div class="podium-user">{top_users.iloc[2]['Utilisateur']}</div>
                <div class="podium-score">{top_users.iloc[2]['Alcool en grammes']:.2f} g</div>
                <div class="podium-rank">🥉</div>
            </div>
        </div>
        """
        components.html(podium_html, height=250)

    if selected_user != "Tous":
        df = df[df["Utilisateur"] == selected_user]
    
    # Indicateurs clés
    df_biere = df[df["Type"] == "🍺 Bière"]
    volume_total_biere = df_biere["Volume en litres"].sum()
    total_pintes = volume_total_biere / 0.5
    total_vin = df[df["Boisson"].str.contains("Rouge|Blanc|Rosé", na=False)]["Volume en litres"].sum() / 0.75
    total_hard = df[df["Type"].str.contains("Hard", na=False)]["Volume en litres"].sum() / 0.7
    total_alcool_grams = df["Alcool en grammes"].sum() / 1000
    total_volume_litres = df["Volume en litres"].sum()
    
    # Création de trois colonnes côte à côte
    col1, col2, col3 = st.columns(3)

    # Affichage des métriques dans chaque colonne
    with col1:
        st.metric("🍺 Pintes bues", int(total_pintes))
        st.metric("💪 Alcool total (kg)", f"{total_alcool_grams:.2f} kg")

    with col2:
        st.metric("🍷 Bouteilles de vin bues", int(total_vin))
        st.metric("🧴 Volume total consommé", f"{total_volume_litres:.2f} L")

    with col3:
        st.metric("🥃 Bouteilles de hard bues", int(total_hard))
        
    # Regroupement par jour pour avoir un point de donnée par jour
    df_daily = df.groupby(["Date", "Utilisateur"], as_index=False)["Alcool en grammes"].sum()

    # Ajout d'une colonne de cumul par utilisateur
    df_daily["Cumul Alcool"] = df_daily.groupby("Utilisateur")["Alcool en grammes"].cumsum()

    # Création du graphique Altair
    chart_trend = alt.Chart(df_daily).mark_line(point=True).encode(
        x=alt.X("Date:T", title="Date"),
        y=alt.Y("Cumul Alcool", title="Alcool en grammes cumulé"),
        color=alt.Color("Utilisateur", scale=alt.Scale(scheme='set2')),
        tooltip=["Date", "Utilisateur", "Cumul Alcool"]
    ).properties(title="📈 Évolution cumulée de la consommation par jour")

    # Affichage dans Streamlit
    st.altair_chart(chart_trend, use_container_width=True)

    
    if selected_user == "Tous":
        
        chart_comparison = alt.Chart(df).mark_bar().encode(
            x=alt.X("Utilisateur", title="Utilisateur", sort="-y"),
            y=alt.Y("sum(Alcool en grammes)", title="Alcool consommé en grammes"),
            color=alt.Color("Type", scale=alt.Scale(scheme='pastel1'), legend=None),
            tooltip=["Utilisateur", "Type", "sum(Alcool en grammes)"]
        ).properties(title="🏆 Classement des utilisateurs")
        st.altair_chart(chart_comparison, use_container_width=True)
    else:
        chart_type = alt.Chart(df).mark_bar().encode(
            x=alt.X("Type", title="Type d'alcool"),
            y=alt.Y("sum(Alcool en grammes)", title="Alcool en grammes"),
            color=alt.Color("Type", scale=alt.Scale(scheme='pastel2'), legend=None),
            tooltip=["Type", "sum(Alcool en grammes)"]
        ).properties(title="📌 Répartition des types d'alcool")
        st.altair_chart(chart_type, use_container_width=True)
    
    def plot_top_consumption(df, drink_type, metric, conversion=1, unit="", selected_user="Tous"):
        # Filtrage des données par type de boisson
        df_filtered = df[df["Type"] == drink_type].copy()

        # Filtrage par utilisateur si nécessaire
        if selected_user != "Tous":
            df_filtered = df_filtered[df_filtered["Utilisateur"] == selected_user]

        # Conversion du volume si nécessaire (par ex : litres -> pintes)
        df_filtered[metric] = df_filtered["Volume en litres"] / conversion if conversion != 1 else df_filtered["Volume en litres"]

        # Agrégation des données
        group_cols = ["Utilisateur", "Boisson"] if selected_user == "Tous" else ["Boisson"]
        top_items = (
            df_filtered.groupby(group_cols, as_index=False)[metric]
            .sum()
            .sort_values(by=metric, ascending=False)
        )

        # Top 5 des consommations
        top_5_items = (
            top_items.groupby("Boisson", as_index=False)[metric]
            .sum()
            .sort_values(by=metric, ascending=False)
            .head(5)
        )

        # Paramètres des couleurs
        color_field = "Utilisateur" if selected_user == "Tous" else "Boisson"
        color_scheme = "pastel1" if selected_user == "Tous" else "pastel2"

        # Création du bar plot vertical
        plot = (
            alt.Chart(df_filtered[df_filtered["Boisson"].isin(top_5_items["Boisson"])])
            .mark_bar()
            .encode(
                x=alt.X("Boisson:N", sort='-y', title="Boisson"),  # Axe des X = catégories (vertical)
                y=alt.Y(f"sum({metric}):Q", title=f"Total consommé ({unit})"),  # Axe des Y = valeurs
                color=alt.Color(f"{color_field}:N", scale=alt.Scale(scheme=color_scheme)),
                tooltip=["Boisson", color_field, alt.Tooltip(f"sum({metric}):Q", title=f"Total ({unit})")]
            )
            .properties(
                title=f"Top 5 des {drink_type}s consommés - {selected_user}",
                width=500,
                height=400
            )
        )

        # Affichage du graphique
        st.altair_chart(plot, use_container_width=True)

    # 🔍 Plots des bières (en pintes) et des alcools forts (en litres)
    plot_top_consumption(df, drink_type="🍺 Bière", metric="Pintes", conversion=0.5, unit="pintes", selected_user=selected_user)
    plot_top_consumption(df, drink_type="🥃 Hard", metric="Volume en litres", unit="L", selected_user=selected_user)

    # Filtrer les données en fonction de la sélection
    if selected_user != "Tous":
        df_filtered = df[df["Utilisateur"] == selected_user]

        # Regrouper les données par date et sommer la quantité d'alcool en grammes
        df_daily_alcool = df_filtered.groupby("Date", as_index=False)["Alcool en grammes"].sum()

        # Bar plot avec des couleurs pastel vert → jaune → rouge
        bar_plot = alt.Chart(df_daily_alcool).mark_bar().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format='%b %d', labelAngle=-90)),
            y=alt.Y("Alcool en grammes:Q", title="Alcool consommé (g)"),
            color=alt.Color(
                "Alcool en grammes:Q",
                scale=alt.Scale(
                    domain=[0, df_daily_alcool["Alcool en grammes"].max()],
                    range=["#C8E6C9", "#FFF9C4", "#FFCDD2"]  # Vert pastel → Jaune pastel → Rouge pastel
                ),
                legend=None
            ),
            tooltip=["Date", alt.Tooltip("Alcool en grammes:Q", title="Alcool consommé (g)")]
        ).properties(
            title=f"📊 Quantité d'alcool consommée par jour - {selected_user}",
            width=700,
            height=400
        )

    else:
        df_filtered = df.copy()

        # Regrouper par date et utilisateur pour la vue "Tous"
        df_daily_alcool = df_filtered.groupby(["Date", "Utilisateur"], as_index=False)["Alcool en grammes"].sum()

        # Bar plot avec des couleurs pastel vert → jaune → rouge
        bar_plot = alt.Chart(df_daily_alcool).mark_bar().encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format='%b %d', labelAngle=-90)),
            y=alt.Y("Alcool en grammes:Q", title="Alcool consommé (g)"),
            color=alt.Color(
                "Alcool en grammes:Q",
                scale=alt.Scale(
                    domain=[0, df_daily_alcool["Alcool en grammes"].max()],
                    range=["#C8E6C9", "#FFF9C4", "#FFCDD2"]  # Vert pastel → Jaune pastel → Rouge pastel
                ),
                legend=None
            ),
            tooltip=["Date", "Utilisateur", alt.Tooltip("Alcool en grammes:Q", title="Alcool consommé (g)")]
        ).properties(
            title="📊 Quantité d'alcool consommée par jour (Tous les utilisateurs)",
            width=700,
            height=400
        )

    # Affichage du graphique
    st.altair_chart(bar_plot, use_container_width=True)
