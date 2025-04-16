import streamlit as st
from users import *
from consumption import *
from stats_all_time import * 
from stats_du_mois import *

def main():
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Navigation", ["Ajouter une consommation", "Supprimer une consommation", "Stats du mois", "Stats all time", "Ajouter un utilisateur"])
    USERS_LIST = load_users()

    if page == "Ajouter une consommation":
        if USERS_LIST:
        # Sélection de l'utilisateur
            selected_user = st.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)

            # Chargement des données une seule fois
            with st.spinner("Chargement des consommations..."):
                df_user = load_consumptions(selected_user)            
                add_consumption(selected_user, df_user)
        else:
            st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")
    
    elif page == "Supprimer une consommation":
        if USERS_LIST:
        # Sélection de l'utilisateur
            selected_user = st.selectbox("👤 Sélectionnez un utilisateur", USERS_LIST)

            # Chargement des données une seule fois
            with st.spinner("Chargement des consommations..."):
                df_user = load_consumptions(selected_user)            
                manage_consumptions(selected_user, df_user)
        else:
            st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")
    
    elif page == "Stats du mois":
        stats_du_mois()

    elif page == "Stats all time":
        stats_all_time()
    
    elif page == "Ajouter un utilisateur":
        st.title("Créer un compte utilisateur")
        prenom = st.text_input("Entrez votre prénom :")
        if st.button("Ajouter"):
            if add_user(prenom):
                st.success(f"Utilisateur {prenom} ajouté avec succès !")
            else:
                st.warning("Cet utilisateur existe déjà.")
    
    


if __name__ == "__main__":
    main()
