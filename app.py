import streamlit as st
import requests

# -------------------------------------------------------------------
# KULCSFONTOSSÁGÚ RÉSZ: AZ n8n KAPCSOLAT
# -------------------------------------------------------------------
# Illeszd be ide a TELJES URL-t, amit az n8n Webhook node-ból
# kimásoltál az előző (3.) lépésben.
#
# A te IP címed: 46.62.222.149
# A teljes URL valahogy így fog kinézni:
# "http://46.62.222.149:5678/webhook/12345abc-1234-..."
# -------------------------------------------------------------------
N8N_WEBHOOK_URL = "http://46.62.222.149:5678/webhook/fc5f37e5-c275-480b-957b-40e5ad388027"

# --- OLDALSÁV SZŰRŐK ---
st.sidebar.header("🔍 Szűrők")

# 1. Dokumentum Típus
doc_types = ["Összes", "Judgment", "Opinion", "Order"]
selected_type = st.sidebar.selectbox("Dokumentum Típusa", doc_types)

# 2. Évszám választó
min_year, max_year = st.sidebar.slider("Időszak", 1950, 2025, (2000, 2025))

# 3. Kulcsszó (Opcionális)
# Ezt később dinamikusan is betöltheted, most legyen egy egyszerű lista
filter_keyword = st.sidebar.text_input("Kulcsszó szűrés")

# --- KÜLDÉS A WEBHOOKNAK ---
# Amikor a requests.post-ot hívod, tedd bele ezeket is a JSON-be:


st.title("🤖 Jogeset kereső assziszetens")

# Chat előzmények inicializálása
if "messages" not in st.session_state:
    st.session_state.messages = []

# Előzmények kiírása
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Felhasználói bevitel kezelése
if prompt := st.chat_input("Milyen jogesetekkel kapcsolatos kérdésed van?"):
    
    # 1. Felhasználói üzenet megjelenítése
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Kérés küldése az n8n backendnek
    try:        
        # POST kérés küldése a webhook URL-re
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
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=90) # 90 mp timeout

        # 3. Válasz feldolgozása
        if response.status_code == 200:
            # Az n8n válasza (a "Respond to Webhook" node-ból):
            # {"response": "Az AI által generált válasz..."}
            ai_response = response.json().get("response", "Hiba: Ismeretlen válaszformátum az n8n-től.")
        else:
            ai_response = f"Hiba: A backend szerver ({response.status_code}) hibát adott vissza."

    except requests.exceptions.ConnectionError:
        ai_response = "Hiba: Nem sikerült csatlakozni a Hetzner szerverhez. (ERR_CONNECTION_REFUSED)"
    except requests.exceptions.RequestException as e:
        ai_response = f"Hiba: A kapcsolat megszakadt. ({e})"

    # 4. AI válasz megjelenítése
    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.session_state.messages.append({"role": "assistant", "content": ai_response})









