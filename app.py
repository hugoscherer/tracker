import streamlit as st
from users import *
from consumption import *
from stats_all_time import * 
from stats_du_mois import *

def main():
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Navigation", ["Ajouter une consommation", "Supprimer une consommation", "Stats du mois", "Stats all time", "Ajouter un utilisateur"])

    if page == "Ajouter une consommation":
        users = load_users()
        if users:
            selected_user = st.selectbox("Sélectionnez un utilisateur", users)
            add_consumption(selected_user)
        else:
            st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")
    
    elif page == "Supprimer une consommation":
        users = load_users()
        if users:
            selected_user = st.selectbox("Sélectionnez un utilisateur", users)
            manage_consumptions(selected_user)
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
