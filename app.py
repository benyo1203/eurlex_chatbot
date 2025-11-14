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
N8N_WEBHOOK_URL = "http://46.62.222.149:5678/webhook/http://localhost:5678/webhook-test/fc5f37e5-c275-480b-957b-40e5ad388027"


st.title("🤖 EUR-Lex AI Asszisztens")
st.caption("A teljes EUR-Lex adatbázisban (~500GB) keresek.")

# Chat előzmények inicializálása
if "messages" not in st.session_state:
    st.session_state.messages = []

# Előzmények kiírása
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Felhasználói bevitel kezelése
if prompt := st.chat_input("Mit szeretnél tudni az EUR-Lex-ből?"):
    
    # 1. Felhasználói üzenet megjelenítése
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Kérés küldése az n8n backendnek
    try:
        # A JSON payloadnak meg kell egyeznie azzal, amit az n8n vár
        # Az n8n-ben ezt használjuk: {{ $json.body.question }}
        # Ezért itt a kulcsnak "question"-nek kell lennie.
        payload = {"question": prompt}
        
        # POST kérés küldése a webhook URL-re
        with st.spinner("Keresés a teljes adatbázisban..."):
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
