import streamlit as st
from visualisations import *
def manage_consumptions():
    st.title("🗂️ Gérer les consommations")

    users = load_users()
    if not users:
        st.warning("Aucun utilisateur trouvé. Veuillez ajouter un utilisateur d'abord.")
        return

    selected_user = st.selectbox("👤 Sélectionnez un utilisateur", users)
    user_file = os.path.join(ALCOHOL_FOLDER, f"{selected_user}.csv")

    if os.path.exists(user_file):
        df = pd.read_csv(user_file)
        if df.empty:
            st.info("Aucune consommation enregistrée pour cet utilisateur.")
            return

        st.subheader(f"Consommations de {selected_user}")
        st.dataframe(df)

        # Sélection d'une consommation à supprimer
        selected_index = st.selectbox("Sélectionnez la consommation à supprimer (par index) :", df.index)

        if st.button("Supprimer la consommation"):
            df = df.drop(index=selected_index)
            df.to_csv(user_file, index=False)
            st.success("Consommation supprimée avec succès.")
            st.experimental_rerun()  # Rafraîchir la page pour afficher les données mises à jour
    else:
        st.warning("Aucune donnée trouvée pour cet utilisateur.")
