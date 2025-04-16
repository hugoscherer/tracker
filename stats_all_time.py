import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import streamlit.components.v1 as components
from google_sheets_utils import authenticate_gsheets
from fonc import *

def stats_all_time():
    SHEET = authenticate_gsheets()

    st.title("📊 Stats All-Time")

    df = load_all_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"])

    # 🥇 Podium all-time
    st.subheader("🏆 Podium All-Time")
    podium = df.groupby("Utilisateur")["Alcool en grammes"].sum().reset_index().sort_values(by="Alcool en grammes", ascending=False).head(3)
    st.components.v1.html(generate_podium(podium), height=250)

    # 📥 Sélection des utilisateurs à inclure
    st.subheader("👤 Filtrer par utilisateur")

    users = sorted(df["Utilisateur"].unique().tolist())
    user_choice = st.selectbox("Afficher :", ["Tous les utilisateurs"] + users)

    if user_choice != "Tous les utilisateurs":
        df = df[df["Utilisateur"] == user_choice]

    # 📊 Indicateurs généraux
    st.subheader("📊 Indicateurs globaux")
    df_biere = df[df["Type"] == "🍺 Bière"]
    total_pintes = df_biere["Volume en litres"].sum() / 0.5
    total_vin = df[df["Boisson"].isin(["Rouge", "Blanc", "Rosé"])]
    total_bouteilles_vin = total_vin["Volume en litres"].sum() / 0.75
    total_hard = df[df["Type"].str.contains("Hard")]["Volume en litres"].sum() / 0.7
    total_alcool = df["Alcool en grammes"].sum()
    total_volume = df["Volume en litres"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🍺 Pintes bues", int(total_pintes))
        st.metric("💪 Alcool total", f"{total_alcool:.0f} g")
    with col2:
        st.metric("🍷 Bouteilles de vin", int(total_bouteilles_vin))
        st.metric("🧴 Volume total", f"{total_volume:.2f} L")
    with col3:
        st.metric("🥃 Bouteilles de hard", int(total_hard))

    # 👑 Leaders all-time améliorés
    st.subheader("👑 Leaders par type")

    leader_biere = get_top_user(df, df["Type"] == "🍺 Bière")
    leader_vin = get_top_user(df, df["Type"] == "🍷 Vin")
    leader_hard = top_user(df, df["Type"].str.contains("Hard"))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("🍺 **Bière**")
        if leader_biere is not None and not leader_biere.empty:
            row = leader_biere.iloc[0]
            pintes = row["Volume en litres"] / 0.5
            st.write(f"**{row['Utilisateur']}** ({pintes:.1f} pintes)")

    with col2:
        st.write("🍷 **Vin**")
        if leader_vin is not None and not leader_vin.empty:
            row = leader_vin.iloc[0]
            verres = row["Volume en litres"] / 0.15
            st.write(f"**{row['Utilisateur']}** ({verres:.0f} verres)")

    with col3:
        st.write("🥃 **Hard**")
        if leader_hard is not None and not leader_hard.empty:
            row = leader_hard.iloc[0]
            cocktails = row["Alcool en grammes"] / 12.5
            st.write(f"**{row['Utilisateur']}** ({cocktails:.0f} cocktails)")

    # 📈 Line chart de la conso hebdomadaire par utilisateur

    st.subheader("📈 Évolution hebdomadaire - par utilisateur")

    # Extraire semaine ISO
    df["Semaine"] = df["Date"].dt.isocalendar().week
    df["Année"] = df["Date"].dt.isocalendar().year
    weekly = df.groupby(["Année", "Semaine", "Utilisateur"])["Alcool en grammes"].sum().reset_index()
    weekly["Semaine ISO"] = weekly["Année"].astype(str) + "-S" + weekly["Semaine"].astype(str).str.zfill(2)

    # Convertir Semaine ISO en date approximative (pour tri X)
    weekly["Date ISO"] = pd.to_datetime(weekly["Année"].astype(str) + weekly["Semaine"].astype(str) + '1', format="%G%V%u")

    # Line chart
    line_chart = alt.Chart(weekly).mark_line(point=True).encode(
        x=alt.X("Date ISO:T", title="Semaine"),
        y=alt.Y("Alcool en grammes:Q", title="Grammage (g)"),
        color=alt.Color("Utilisateur:N", title="Utilisateur", scale=alt.Scale(scheme="set2")),
        tooltip=["Utilisateur", "Semaine ISO", "Alcool en grammes"]
    ).properties(
        width=800,
        height=400,
    )

    st.altair_chart(line_chart, use_container_width=True)
    
    # 🍺 Top 7 bières les plus bues (en pintes)
    st.subheader("🍺 Top 7 bières les plus bues")

    top_bieres = df[df["Type"] == "🍺 Bière"].groupby("Boisson")["Volume en litres"].sum().reset_index()
    top_bieres["Pintes"] = top_bieres["Volume en litres"] / 0.5
    top_bieres = top_bieres.sort_values(by="Pintes", ascending=False).head(7)

    chart_bieres = alt.Chart(top_bieres).mark_bar().encode(
        x=alt.X("Pintes:Q", title="Pintes bues"),
        y=alt.Y("Boisson:N", sort='-x', title="Bière"),
        color=alt.Color("Boisson:N", scale=alt.Scale(scheme="pastel2"), legend=None),
        tooltip=["Boisson", alt.Tooltip("Pintes:Q", title="Pintes")]
    ).properties(
        height=300,
    )

    st.altair_chart(chart_bieres, use_container_width=True)


    # 🥃 Top 5 alcools forts (en shots)
    st.subheader("🥃 Top 5 alcools forts les plus bus")

    top_hard = df[df["Type"].str.contains("Hard")].groupby("Boisson")["Volume en litres"].sum().reset_index()
    top_hard["Shots"] = top_hard["Volume en litres"] / 0.03
    top_hard = top_hard.sort_values(by="Shots", ascending=False).head(5)

    chart_hard = alt.Chart(top_hard).mark_bar().encode(
        x=alt.X("Shots:Q", title="Shots bus"),
        y=alt.Y("Boisson:N", sort='-x', title="Alcool fort"),
        color=alt.Color("Boisson:N", scale=alt.Scale(scheme="pastel2"), legend=None),
        tooltip=["Boisson", alt.Tooltip("Shots:Q", title="Shots")]
    ).properties(
        height=250,
    )

    st.altair_chart(chart_hard, use_container_width=True)


    # 🥤 Top 7 tailles de verres utilisées
    st.subheader("🥤 Tailles de verres les plus utilisées")

    top_tailles = df.groupby("Taille")["Quantité"].sum().reset_index().sort_values(by="Quantité", ascending=False).head(7)

    chart_tailles = alt.Chart(top_tailles).mark_bar().encode(
        x=alt.X("Quantité:Q", title="Nombre total"),
        y=alt.Y("Taille:N", sort='-x', title="Taille de verre", axis=alt.Axis(labelLimit=200)),  # 💡 plus de place pour les noms
        color=alt.Color("Taille:N", scale=alt.Scale(scheme="pastel2"), legend=None),
        tooltip=["Taille", "Quantité"]
    ).properties(
        height=300,
    )

    st.altair_chart(chart_tailles, use_container_width=True)


    # 📅 Moyenne de consommation par jour de la semaine (avec jours sans alcool inclus)

    st.subheader("📅 Moyenne d'alcool consommé par jour de la semaine")

    # Base de référence
    date_depart = df["Date"].min().normalize()
    date_aujourdhui = pd.to_datetime("today").normalize()

    # Générer tous les jours depuis le 31 janvier
    all_days = pd.date_range(start=date_depart, end=date_aujourdhui, freq='D')
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    # Créer un DataFrame vide avec tous les jours
    df_all_days = pd.DataFrame({"Date": all_days})
    df_all_days["Jour"] = df_all_days["Date"].dt.dayofweek
    df_all_days["Jour nom"] = df_all_days["Jour"].apply(lambda x: jours[x])

    # Regrouper ta consommation réelle par jour
    conso_par_jour = df.groupby("Date")["Alcool en grammes"].sum().reset_index()

    # Fusionner pour inclure les 0g sur les jours où tu n'as pas bu
    df_jour_complet = df_all_days.merge(conso_par_jour, on="Date", how="left").fillna(0)

    # Moyenne par jour de la semaine
    moyenne_jour = df_jour_complet.groupby("Jour nom")["Alcool en grammes"].mean().reindex(jours).reset_index()

    # Affichage
    chart_jours = alt.Chart(moyenne_jour).mark_bar().encode(
        x=alt.X("Jour nom:N", title="Jour de la semaine", sort=jours),
        y=alt.Y("Alcool en grammes:Q", title="Moyenne (g)"),
        color=alt.Color("Jour nom:N", scale=alt.Scale(scheme="pastel2"), legend=None),
        tooltip=["Jour nom", "Alcool en grammes"]
    ).properties(
        height=300,
    )

    st.altair_chart(chart_jours, use_container_width=True)

    # 🔢 Jours avec/sans alcool
    st.subheader("📅 Présence d’alcool dans la semaine")
    df_jours = df.groupby("Date")["Alcool en grammes"].sum().reset_index()
    nb_jours_bu = (df_jours["Alcool en grammes"] > 0).sum()
    # Nombre de jours depuis le 31 janvier
    date_depart = pd.to_datetime("2025-01-31")
    date_aujourdhui = pd.to_datetime("today").normalize()
    nb_jours_total = (date_aujourdhui - date_depart).days + 1    
    
    st.write(f"**{nb_jours_bu} jours** avec alcool sur **{nb_jours_total} jours**. ({nb_jours_bu/nb_jours_total*100}%)")

    # 📊 Analyse par utilisateur/jour
    df_par_jour = df.groupby(["Date", "Utilisateur"])["Alcool en grammes"].sum().reset_index()

    def classify_jour(g):
        if g <= 25:
            return "🟢 ≤25g"
        elif g <= 50:
            return "🟡 25-50g"
        elif g <= 100:
            return "🟠 50-100g"
        else:
            return "🔴 >100g"

    df_par_jour["Zone"] = df_par_jour["Alcool en grammes"].apply(classify_jour)

    # Comptage par zone et utilisateur
    tab_zones = df_par_jour.groupby(["Utilisateur", "Zone"]).size().unstack(fill_value=0)

    # 🧾 Réorganisation visuelle (ordre voulu)
    zone_order = ["🟢 ≤25g", "🟡 25-50g", "🟠 50-100g", "🔴 >100g"]
    tab_zones = tab_zones.reindex(columns=zone_order, fill_value=0)

    st.subheader("📊 Répartition des jours par utilisateur et par zone de consommation")
    st.dataframe(tab_zones)

    # 📈 Graphe d’évolution
    st.subheader("📈 Évolution cumulée")
    df_daily = df.groupby(["Date", "Utilisateur"], as_index=False)["Alcool en grammes"].sum()
    df_daily["Cumul Alcool"] = df_daily.groupby("Utilisateur")["Alcool en grammes"].cumsum()

    chart = alt.Chart(df_daily).mark_line(point=True).encode(
        x=alt.X("Date:T", title="Date", axis=alt.Axis(labelAngle=-90)),
        y=alt.Y("Cumul Alcool", title="Alcool en grammes cumulé"),
        color=alt.Color("Utilisateur:N", scale=alt.Scale(scheme="set2")),
        tooltip=["Date", "Utilisateur", "Cumul Alcool"]
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)