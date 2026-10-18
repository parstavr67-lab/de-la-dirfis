import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Εκτροφείο de la Dirfis", page_icon="🐕", layout="wide"
)

st.title("🐕 Εκτροφείο de la Dirfis")
st.markdown("### Σύστημα Διαχείρισης & Παρακολούθησης (Tablet Edition)")


@st.cache_resource
def get_connection():
  return sqlite3.connect("de_la_dirfis.db", check_same_thread=False)


conn = get_connection()

menu = st.selectbox(
    "Επιλέξτε Ενότητα:", [
        "🐕 Σκύλοι Εκτροφείου",
        "❤️ Ζευγαρώματα",
        "🐶 Γέννες",
        "🐾 Κουτάβια / Πωλήσεις",
        "🎯 Εκπαίδευση",
        "👤 Πελάτες / Waitlist",
        "💰 Οικονομικά & Ταμείο",
    ]
)


def load_data(query):
  return pd.read_sql(query, conn)


if menu == "🐕 Σκύλοι Εκτροφείου":
  st.subheader("🐕 Σκύλοι Εκτροφείου")
  df = load_data(
      "SELECT id, name, sex, birth_date, microchip, pedigree, father, mother,"
      " breeder, color FROM dogs"
  )
  st.dataframe(df, use_container_width=True)

elif menu == "❤️ Ζευγαρώματα":
  st.subheader("❤️ Διαχείριση Ζευγαρωμάτων")
  df = load_data(
      "SELECT id, male_dog, female_dog, mating_date, expected_birth_date,"
      " status FROM matings"
  )
  st.dataframe(df, use_container_width=True)

elif menu == "🐶 Γέννες":
  st.subheader("🐶 Καταχωρημένες Γέννες")
  df = load_data(
      "SELECT id, mating_info, birth_date, males_count, females_count,"
      " total_puppies FROM litters"
  )
  st.dataframe(df, use_container_width=True)

elif menu == "🐾 Κουτάβια / Πωλήσεις":
  st.subheader("🐾 Κουτάβια & Κατάσταση")
  df = load_data(
      "SELECT id, litter_info, name, sex, status, price, deposit, buyer_name"
      " FROM puppies"
  )
  st.dataframe(df, use_container_width=True)

elif menu == "🎯 Εκπαίδευση":
  st.subheader("🎯 Εκπαίδευση Σκύλων & Πελάτες")
  df = load_data(
      "SELECT id, client_name, phone, dog_name, dog_breed, training_type,"
      " status, total_cost, advance_payment FROM trainings"
  )
  st.dataframe(df, use_container_width=True)

elif menu == "👤 Πελάτες / Waitlist":
  st.subheader("👤 Ενδιαφερόμενοι & Λίστα Αναμονής")
  df = load_data(
      "SELECT id, full_name, phone, city, pref_sex, purpose, deposit, status"
      " FROM clients"
  )
  st.dataframe(df, use_container_width=True)

elif menu == "💰 Οικονομικά & Ταμείο":
  st.subheader("💰 Οικονομικά & Συναλλαγές")
  df = load_data(
      "SELECT id, trans_date, trans_type, category, amount, payment_method,"
      " description FROM transactions"
  )
  st.dataframe(df, use_container_width=True)

  inc_df = load_data(
      "SELECT SUM(amount) FROM transactions WHERE trans_type = 'Έσοδο'"
  )
  exp_df = load_data(
      "SELECT SUM(amount) FROM transactions WHERE trans_type = 'Έξοδο'"
  )

  total_in = inc_df.iloc[0, 0] if inc_df.iloc[0, 0] is not None else 0.0
  total_out = exp_df.iloc[0, 0] if exp_df.iloc[0, 0] is not None else 0.0

  col1, col2, col3 = st.columns(3)
  col1.metric("Έσοδα", f"€{total_in:.2f}")
  col2.metric("Έξοδα", f"€{total_out:.2f}")
  col3.metric("Ταμείο", f"€{total_in - total_out:.2f}")
