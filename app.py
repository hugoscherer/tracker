import streamlit as st
from users import *
from consumption import *
from visualizations import * 

def main():
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Navigation", ["Ajouter une consommation", "Ajouter un utilisateur", "Visualisation des consommations", "Gestion des consommations"])

    if page == "Ajouter un utilisateur":
        st.title("Créer un compte utilisateur")
        prenom = st.text_input("Entrez votre prénom :")
        if st.button("Ajouter"):
            if add_user(prenom):
                st.success(f"Utilisateur {prenom} ajouté avec succès !")
            else:
                st.warning("Cet utilisateur existe déjà.")

    elif page == "Ajouter une consommation":
        users = load_users()
        if users:
            selected_user = st.selectbox("Sélectionnez un utilisateur", users)
            add_consumption(selected_user)
        else:
            st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")

    elif page == "Visualisation des consommations":
        visualize_consumption()
    
    elif page == "Gestion des consommations":
        users = load_users()
        if users:
            selected_user = st.selectbox("Sélectionnez un utilisateur", users)
            manage_consumptions(selected_user)
        else:
            st.warning("Ajoutez un utilisateur avant de pouvoir enregistrer une consommation.")


if __name__ == "__main__":
    main()
