import streamlit as st
from users import *
from consumption import *
from stats_all_time import * 
from stats_du_mois import *

def main():
    st.sidebar.title("Menu")

    # Sections du menu dans la sidebar
    with st.sidebar.expander("Gestion des consommations", expanded=True):
        gestion_action = st.radio(
            "Actions",
            ["Ajouter une consommation", "Supprimer une consommation"],
            key="gestion_consommations"
        )
    
    with st.sidebar.expander("Statistiques", expanded=True):
        stats_action = st.radio(
            "Voir les stats",
            ["Stats du mois", "Stats all time"],
            key="stats"
        )
    
    with st.sidebar.expander("Utilisateurs", expanded=True):
        user_action = st.radio(
            "Gestion utilisateurs",
            ["Ajouter un utilisateur"],
            key="utilisateurs"
        )

    USERS_LIST = load_users()

    # Gestion des consommations
    if gestion_action == "Ajouter une consommation":
        if USERS_LIST:
            selected_user = st.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)
            with st.spinner("Chargement des consommations..."):
                add_consumption(selected_user)
        else:
            st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")

    elif gestion_action == "Supprimer une consommation":
        if USERS_LIST:
            selected_user = st.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)
            with st.spinner("Chargement des consommations..."):
                manage_consumptions(selected_user)
        else:
            st.warning("Ajoutez un utilisateur avant de pouvoir gérer les consommations.")

    # Statistiques
    elif stats_action == "Stats du mois":
        stats_du_mois()
    elif stats_action == "Stats all time":
        stats_all_time()

    # Gestion des utilisateurs
    elif user_action == "Ajouter un utilisateur":
        st.title("Créer un compte utilisateur")
        prenom = st.text_input("Entrez votre prénom :")
        if st.button("Ajouter"):
            if add_user(prenom):
                st.success(f"Utilisateur {prenom} ajouté avec succès !")
            else:
                st.warning("Cet utilisateur existe déjà.")

if __name__ == "__main__":
    main()
