import streamlit as st
import pandas as pd
import os
from conso import *
from visualisations import *

# Définition des fichiers CSV
USERS_CSV = "users.csv"
ALCOHOL_DATA_FOLDER = "alcohol_data"  # Dossier pour stocker les consommations

# Vérification et création des fichiers nécessaires
if not os.path.exists(USERS_CSV):
    pd.DataFrame(columns=["prenom"]).to_csv(USERS_CSV, index=False)
if not os.path.exists(ALCOHOL_DATA_FOLDER):
    os.makedirs(ALCOHOL_DATA_FOLDER)



# Définition des pages
def main():
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Navigation", ["Ajouter une consommation", "Ajouter un user", "Visualisation"])
    
    if page == "Ajouter un user":
        st.title("Bienvenue sur le tracker de consommation d'alcool")
        prenom = st.text_input("Entrez votre prénom pour créer un compte :")
        if st.button("Ajouter") and prenom:
            if add_user(prenom):
                st.success(f"Utilisateur {prenom} ajouté avec succès !")
            else:
                st.warning("Cet utilisateur existe déjà.")
    
    elif page == "Ajouter une consommation":
        st.title("Ajouter une consommation")
        initialize_files()
        users = load_users()
        if users:
            selected_user = st.selectbox("👤 Sélectionnez un utilisateur", users)
            user_file = os.path.join(ALCOHOL_FOLDER, f"{selected_user}.csv")
            add_consumption(user_file, selected_user)
        else:
            st.warning("Aucun utilisateur trouvé. Veuillez ajouter un utilisateur d'abord.")

    
    elif page == "Visualisation":
        visualize_consumption()

if __name__ == "__main__":
    main()
