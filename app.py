import streamlit as st
import requests

N8N_WEBHOOK_URL = "http://46.62.222.149:5678/webhook/fc5f37e5-c275-480b-957b-40e5ad388027"

st.sidebar.header("🔍 Szűrők")

doc_types = ["Összes", "Judgment", "Opinion", "Order"]
selected_type = st.sidebar.selectbox("Dokumentum Típusa", doc_types)

min_year, max_year = st.sidebar.slider("Időszak", 1950, 2025, (2000, 2025))
filter_keyword = st.sidebar.text_input("Kulcsszó szűrés")

st.title("🤖 Jogeset kereső assziszetens")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Milyen jogesetekkel kapcsolatos kérdésed van?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:        
        payload = {
            "question": prompt,
            "filters": {
                "doc_type": None if selected_type == "Összes" else selected_type,
                "year_start": min_year,
                "year_end": max_year,
                "keyword": filter_keyword if filter_keyword else None
                }
        }
        with st.spinner("Keresés..."):
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=90)

        if response.status_code == 200:
            ai_response = response.json().get("response", "Hiba: Ismeretlen válaszformátum az n8n-től.")
        else:
            ai_response = f"Hiba: A backend szerver ({response.status_code}) hibát adott vissza."

    except requests.exceptions.ConnectionError:
        ai_response = "Hiba: Nem sikerült csatlakozni a Hetzner szerverhez. (ERR_CONNECTION_REFUSED)"
    except requests.exceptions.RequestException as e:
        ai_response = f"Hiba: A kapcsolat megszakadt. ({e})"
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})










