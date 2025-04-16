import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import streamlit.components.v1 as components
from fonc import *

def stats_all_time():

    st.title("📊 Stats All-Time")

    df = load_all_data()
    if df.empty:
        st.warning("Aucune donnée disponible.")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"])

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # 🥇 Podium all-time
    st.subheader("🏆 Podium All-Time")
    podium = df.groupby("Utilisateur")["Alcool en grammes"].sum().reset_index().sort_values(by="Alcool en grammes", ascending=False).head(3)
    st.components.v1.html(generate_podium(podium), height=250)

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # 📥 Sélection des utilisateurs à inclure
    st.subheader("👤 Filtrer par utilisateur")

    users = sorted(df["Utilisateur"].unique().tolist())
    user_choice = st.selectbox("Afficher :", ["Tous les utilisateurs"] + users)

    if user_choice != "Tous les utilisateurs":
        df = df[df["Utilisateur"] == user_choice]

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

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

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # 👑 Leaders all-time
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

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # 📈 Évolution hebdomadaire - par utilisateur (avec semaines à 0)
    st.subheader("📈 Évolution hebdomadaire - par utilisateur")

    df["Date"] = pd.to_datetime(df["Date"])
    df["Semaine"] = df["Date"].dt.isocalendar().week
    df["Année"] = df["Date"].dt.isocalendar().year
    utilisateurs = df["Utilisateur"].unique()

    # Créer toutes les semaines entre min et max date
    start_week = df["Date"].min().to_period('W').start_time
    end_week = pd.to_datetime("today").to_period('W').start_time
    all_weeks = pd.date_range(start=start_week, end=end_week, freq="W-MON")  # Lundi de chaque semaine

    # Créer Année + Semaine à partir des dates
    weeks_df = pd.DataFrame({"Date ISO": all_weeks})
    weeks_df["Année"] = weeks_df["Date ISO"].dt.isocalendar().year
    weeks_df["Semaine"] = weeks_df["Date ISO"].dt.isocalendar().week
    weeks_df["Semaine ISO"] = weeks_df["Année"].astype(str) + "-S" + weeks_df["Semaine"].astype(str).str.zfill(2)

    # Combinaison complète Semaine x Utilisateur
    full_weeks = pd.MultiIndex.from_product([weeks_df["Année"], weeks_df["Semaine"], utilisateurs], names=["Année", "Semaine", "Utilisateur"])
    df_full_weeks = pd.DataFrame(index=full_weeks).reset_index()

    # Ajout de Semaine ISO et Date ISO
    df_full_weeks = pd.merge(df_full_weeks, weeks_df, on=["Année", "Semaine"], how="left")

    # Regrouper les conso réelles
    weekly = df.groupby(["Année", "Semaine", "Utilisateur"], as_index=False)["Alcool en grammes"].sum()

    # Fusionner avec la grille complète
    weekly_merged = pd.merge(df_full_weeks, weekly, on=["Année", "Semaine", "Utilisateur"], how="left")
    weekly_merged["Alcool en grammes"] = weekly_merged["Alcool en grammes"].fillna(0)

    # Graphe
    line_chart = alt.Chart(weekly_merged).mark_line(point=True).encode(
        x=alt.X("Date ISO:T", title="Semaine"),
        y=alt.Y("Alcool en grammes:Q", title="Grammage (g)"),
        color=alt.Color("Utilisateur:N", title="Utilisateur", scale=alt.Scale(scheme="set2")),
        tooltip=["Utilisateur", "Semaine ISO", "Alcool en grammes"]
    ).properties(
        width=800,
        height=400,
    )
    st.altair_chart(line_chart, use_container_width=True)

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################
    
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

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

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

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

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

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # 🔢 Jours avec/sans alcool
    st.subheader("📅 Présence d’alcool dans la semaine")
    df_jours = df.groupby("Date")["Alcool en grammes"].sum().reset_index()
    nb_jours_bu = (df_jours["Alcool en grammes"] > 0).sum()

    # Nombre de jours depuis le 31 janvier
    date_depart = pd.to_datetime("2025-01-31")
    date_aujourdhui = pd.to_datetime("today").normalize()
    nb_jours_total = (date_aujourdhui - date_depart).days + 1    
    
    st.write(f"**{nb_jours_bu} jours** avec alcool sur **{nb_jours_total} jours**. ({nb_jours_bu/nb_jours_total*100}%)")

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # S'assurer que la date est bien en format datetime
    df["Date"] = pd.to_datetime(df["Date"])

    # Lister tous les utilisateurs
    utilisateurs = df["Utilisateur"].unique()

    # Générer toutes les dates entre le premier jour et aujourd’hui
    dates_all = pd.date_range(start=df["Date"].min(), end=pd.to_datetime("today"))

    # Combinaisons complètes Date x Utilisateur
    full_index = pd.MultiIndex.from_product([dates_all, utilisateurs], names=["Date", "Utilisateur"])
    df_full = pd.DataFrame(index=full_index).reset_index()

    # Regrouper les consommations réelles
    df_jour = df.groupby(["Date", "Utilisateur"], as_index=False)["Alcool en grammes"].sum()

    # Fusionner pour inclure les jours sans conso
    df_merged = pd.merge(df_full, df_jour, on=["Date", "Utilisateur"], how="left")
    df_merged["Alcool en grammes"] = df_merged["Alcool en grammes"].fillna(0)

    # Classification des zones de consommation
    def classify_jour(g):
        if g == 0:
            return "0g"
        elif g <= 25:
            return ">0-25g"
        elif g <= 50:
            return "25-50g"
        elif g <= 100:
            return "50-100g"
        elif g <= 200:
            return "100-200g"
        else:
            return ">200g"

    df_merged["Zone"] = df_merged["Alcool en grammes"].apply(classify_jour)

    # Comptage des zones par utilisateur
    tab_zones = df_merged.groupby(["Utilisateur", "Zone"]).size().unstack(fill_value=0)

    # Réorganisation des colonnes dans l’ordre souhaité
    zone_order = ["0g", ">0-25g", "25-50g", "50-100g", "100-200g", ">200g"]
    tab_zones = tab_zones.reindex(columns=zone_order, fill_value=0)

    # Couleurs pastel progressives
    zone_colors = {
    "0g": "#A8E6CF",      # vert pastel
    ">0-25g": "#DCEDC1",   # vert clair pastel
    "25-50g": "#FFFACD",   # jaune très doux (citron givré)
    "50-100g": "#FFD3B6",   # orange clair pastel
    "100-200g": "#FFAAA5",   # rouge clair pastel
    ">200g": "#FF8B94",      # rouge pastel
    }

    # Appliquer les couleurs à chaque colonne
    def highlight_column(val, colname):
        color = zone_colors.get(colname, "#ffffff")
        return f"background-color: {color}"

    styled_table = tab_zones.style.apply(
        lambda col: [highlight_column(v, col.name) for v in col], axis=0
    )

    # Affichage
    st.subheader("📊 Répartition des jours par zone de consommation")
    st.dataframe(styled_table, use_container_width=True)

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # 📊 Analyse par utilisateur/semaine (avec vraies couleurs)

    # S'assurer que les dates sont bien formatées
    df["Date"] = pd.to_datetime(df["Date"])

    # Extraire les infos semaine et année
    df["Semaine"] = df["Date"].dt.isocalendar().week
    df["Année"] = df["Date"].dt.isocalendar().year

    # Regroupement par utilisateur et semaine
    df_par_semaine = df.groupby(["Année", "Semaine", "Utilisateur"])["Alcool en grammes"].sum().reset_index()

    # Classification des zones par grammage
    def classify_zone(g):
        if g < 100:
            return "<100g"
        elif g < 200:
            return "100-200g"
        elif g < 300:
            return "200-300g"
        elif g < 400:
            return "300-400g"
        elif g < 500:
            return "400-500g"
        else:
            return ">500g"

    df_par_semaine["Zone"] = df_par_semaine["Alcool en grammes"].apply(classify_zone)

    # Création du tableau croisé
    tab_zones = df_par_semaine.groupby(["Utilisateur", "Zone"]).size().unstack(fill_value=0)

    # Réorganisation de l’ordre des colonnes
    zone_order = ["<100g", "100-200g", "200-300g", "300-400g", "400-500g", ">500g"]
    tab_zones = tab_zones.reindex(columns=zone_order, fill_value=0)

    # Définition des couleurs à appliquer par zone
    zone_colors = {
    "<100g": "#A8E6CF",      # vert pastel
    "100-200g": "#DCEDC1",   # vert clair pastel
    "200-300g": "#FFFACD",   # jaune très doux (citron givré)
    "300-400g": "#FFD3B6",   # orange clair pastel
    "400-500g": "#FFAAA5",   # rouge clair pastel
    ">500g": "#FF8B94",      # rouge pastel
    }

    # Fonction d'application des couleurs par colonne
    def highlight_column(val, colname):
        color = zone_colors.get(colname, "#ffffff")
        return f"background-color: {color}"

    # Application des couleurs à chaque colonne selon son nom
    styled_table = tab_zones.style.apply(
        lambda col: [highlight_column(v, col.name) for v in col], axis=0
    )

    ######################################################################################################
    ######################################################################################################
    ######################################################################################################

    # Affichage
    st.subheader("📊 Répartition des semaines par zone de consommation")
    st.dataframe(styled_table, use_container_width=True)

    # 📈 Évolution cumulée (all-time avec jours à 0)

    st.subheader("📈 Évolution cumulée")

    df["Date"] = pd.to_datetime(df["Date"])
    utilisateurs = df["Utilisateur"].unique()
    dates_all = pd.date_range(start=df["Date"].min(), end=pd.to_datetime("today"))

    # Générer toutes les combinaisons Date x Utilisateur
    full_index = pd.MultiIndex.from_product([dates_all, utilisateurs], names=["Date", "Utilisateur"])
    df_full = pd.DataFrame(index=full_index).reset_index()

    # Regrouper les conso réelles
    df_grouped = df.groupby(["Date", "Utilisateur"], as_index=False)["Alcool en grammes"].sum()

    # Fusion pour compléter avec 0
    df_merged = pd.merge(df_full, df_grouped, on=["Date", "Utilisateur"], how="left")
    df_merged["Alcool en grammes"] = df_merged["Alcool en grammes"].fillna(0)

    # Cumul par utilisateur
    df_merged["Cumul Alcool"] = df_merged.groupby("Utilisateur")["Alcool en grammes"].cumsum()

    # Graphe
    chart = alt.Chart(df_merged).mark_line(point=True).encode(
        x=alt.X("Date:T", title="Date", axis=alt.Axis(labelAngle=-90)),
        y=alt.Y("Cumul Alcool", title="Alcool en grammes cumulé"),
        color=alt.Color("Utilisateur:N", scale=alt.Scale(scheme="set2")),
        tooltip=["Date", "Utilisateur", "Cumul Alcool"]
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True)