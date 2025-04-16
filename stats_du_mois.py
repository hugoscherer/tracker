import streamlit as st
import altair as alt
from datetime import datetime
import pandas as pd
import streamlit.components.v1 as components
from google_sheets_utils import authenticate_gsheets
from fonc import *

SHEET = authenticate_gsheets()

def stats_du_mois():
    st.title("📅 Stats du Mois")

    # Chargement des données

    df = load_all_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        st.stop()

    # Préparation des données
    month = datetime.today().month
    year = datetime.today().year
    df["Date"] = pd.to_datetime(df["Date"])
    df_month = df[(df["Date"].dt.month == month) & (df["Date"].dt.year == year)]

    if df_month.empty:
        st.info("Aucune consommation ce mois-ci.")
        st.stop()

    # 🥇 Podium du mois
    st.subheader("🏆 Podium du mois")
    podium = df_month.groupby("Utilisateur")["Alcool en grammes"].sum().reset_index().sort_values(by="Alcool en grammes", ascending=False).head(3)
    st.components.v1.html(generate_podium(podium), height=250)

    # 📊 Indicateurs du mois
    st.subheader("📊 Indicateurs")
    df_biere = df_month[df_month["Type"] == "🍺 Bière"]
    total_pintes = df_biere["Volume en litres"].sum() / 0.5
    total_vin = df_month[df_month["Boisson"].isin(["Rouge", "Blanc", "Rosé"])]
    total_bouteilles_vin = total_vin["Volume en litres"].sum() / 0.75
    total_hard = df_month[df_month["Type"].str.contains("Hard")]["Volume en litres"].sum() / 0.7
    total_alcool = df_month["Alcool en grammes"].sum()
    total_volume = df_month["Volume en litres"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🍺 Pintes bues", int(total_pintes))
        st.metric("💪 Alcool total", f"{total_alcool:.0f} g")
    with col2:
        st.metric("🍷 Bouteilles de vin", int(total_bouteilles_vin))
        st.metric("🧴 Volume total", f"{total_volume:.2f} L")
    with col3:
        st.metric("🥃 Bouteilles de hard", int(total_hard))

    # 👑 Leaders par catégorie
    st.subheader("👑 Leaders par catégorie du mois")
    col1, col2, col3 = st.columns(3)

    def top_user(df, filtre):
        return df[filtre].groupby("Utilisateur")["Volume en litres"].sum().reset_index().sort_values(by="Volume en litres", ascending=False).head(1)

    leader_biere = top_user(df_month, df_month["Type"] == "🍺 Bière")
    leader_vin = top_user(df_month, df_month["Type"] == "🍷 Vin")
    leader_hard = top_user(df_month, df_month["Type"].str.contains("Hard"))

    with col1:
        st.write("🍺 Bière")
        if not leader_biere.empty:
            st.write(f"{leader_biere.iloc[0]['Utilisateur']} ({leader_biere.iloc[0]['Volume en litres']:.2f} L)")
    with col2:
        st.write("🍷 Vin")
        if not leader_vin.empty:
            st.write(f"{leader_vin.iloc[0]['Utilisateur']} ({leader_vin.iloc[0]['Volume en litres']:.2f} L)")
    with col3:
        st.write("🥃 Hard")
        if not leader_hard.empty:
            st.write(f"{leader_hard.iloc[0]['Utilisateur']} ({leader_hard.iloc[0]['Volume en litres']:.2f} L)")

    # 📅 Récap jour par jour
    st.subheader("📆 Récap jour par jour")
    df_day = df_month.groupby(["Date", "Utilisateur"])["Alcool en grammes"].sum().reset_index()
    chart = alt.Chart(df_day).mark_bar().encode(
        x=alt.X("Date:T", title="Date", axis=alt.Axis(labelAngle=-90)),
        y=alt.Y("Alcool en grammes:Q", title="Alcool consommé (g)"),
        color=alt.Color("Utilisateur:N", scale=alt.Scale(scheme="pastel1")),
        tooltip=["Date", "Utilisateur", "Alcool en grammes"]
    ).properties(title="Consommation quotidienne du mois", width=700, height=400)

    st.altair_chart(chart, use_container_width=True)