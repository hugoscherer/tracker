import streamlit as st
from users import *
from consumption import *
from stats_all_time import * 
from stats_du_mois import *

def main():
    st.sidebar.title("Menu")

    # Choix de la catégorie principale
    category = st.sidebar.radio("Catégorie", ["Consommations", "Statistiques", "Utilisateurs"])

    USERS_LIST = load_users()

    if category == "Consommations":
        action = st.sidebar.radio("Action", ["Ajouter une consommation", "Supprimer une consommation"])
        if action == "Ajouter une consommation":
            if USERS_LIST:
                selected_user = st.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)
                with st.spinner("Chargement des consommations..."):
                    add_consumption(selected_user)
            else:
                st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")

        elif action == "Supprimer une consommation":
            if USERS_LIST:
                selected_user = st.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)
                with st.spinner("Chargement des consommations..."):
                    df_user = load_consumptions(selected_user)
                    manage_consumptions(selected_user, df_user)
            else:
                st.warning("Ajoutez un utilisateur avant de pouvoir gérer les consommations.")

    elif category == "Statistiques":
        stats_page = st.sidebar.radio("Type de stats", ["Stats du mois", "Stats all time"])
        if stats_page == "Stats du mois":
            stats_du_mois()
        elif stats_page == "Stats all time":
            stats_all_time()

    elif category == "Utilisateurs":
        st.title("Créer un compte utilisateur")
        prenom = st.text_input("Entrez votre prénom :")
        if st.button("Ajouter"):
            if add_user(prenom):
                st.success(f"Utilisateur {prenom} ajouté avec succès !")
            else:
                st.warning("Cet utilisateur existe déjà.")

if __name__ == "__main__":
    main()
