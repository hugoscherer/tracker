import streamlit as st
from users import *
from consumption import *
from stats_all_time import * 
from stats_du_mois import *

def sidebar_box(title, content_func):
    st.sidebar.markdown(
        f"""
        <div style="border:1px solid #ddd; border-radius:8px; padding:10px; margin-bottom:15px; background:#fafafa;">
            <h4 style="margin-top:0;">{title}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    content_func()

def main():
    st.sidebar.title("Menu")

    def choix_categorie():
        return st.sidebar.radio("", ["Consommations", "Statistiques", "Utilisateurs"])

    category = choix_categorie()

    USERS_LIST = load_users()

    if category == "Consommations":

        def choix_action():
            return st.sidebar.radio("", ["Ajouter une consommation", "Supprimer une consommation"])

        sidebar_box("Actions sur consommations", lambda: None)  # juste pour l'encadré

        action = choix_action()

        if action == "Ajouter une consommation":
            if USERS_LIST:
                selected_user = st.sidebar.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)
                with st.spinner("Chargement des consommations..."):
                    add_consumption(selected_user)
            else:
                st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")

        elif action == "Supprimer une consommation":
            if USERS_LIST:
                selected_user = st.sidebar.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)
                with st.spinner("Chargement des consommations..."):
                    manage_consumptions(selected_user)
            else:
                st.warning("Ajoutez un utilisateur avant de pouvoir gérer les consommations.")

    elif category == "Statistiques":

        def choix_stats():
            return st.sidebar.radio("", ["Stats du mois", "Stats all time"])

        sidebar_box("Choix des statistiques", lambda: None)

        stats_page = choix_stats()

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
