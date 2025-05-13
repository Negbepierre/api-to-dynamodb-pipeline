import streamlit as st
import requests
import pandas as pd

# --- CONFIG ---
RAPID_API_KEY = st.secrets["RAPID_API_KEY"]
API_HOST = "transfermarkt6.p.rapidapi.com"

# --- PLAYER OPTIONS ---
player_options = {
    "Lionel Messi": "28003",
    "Cristiano Ronaldo": "8198",
    "Erling Haaland": "418560"
}

# --- UI HEADER ---
st.set_page_config(page_title="Market Value Tracker", page_icon="⚽")
st.title("⚽ Player Market Value Tracker")

# --- PLAYER SELECTION ---
player_name = st.selectbox("Choose a player", list(player_options.keys()))
player_id = player_options[player_name]

# --- API CALL FUNCTION ---
def get_market_values(player_id):
    url = f"https://{API_HOST}/players/market-value-progress?id={player_id}"
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": RAPID_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return [], f"API Error: {response.status_code}"

    data = response.json().get("data", {})
    share = data.get("share", {})
    history = data.get("marketValueDevelopment", [])

    return [{
        "date": h.get("date"),
        "value": h.get("value"),
        "profile": share.get("url"),
        "name": share.get("title")
    } for h in history], None

# --- FETCH DATA ---
data, error = get_market_values(player_id)

# --- HANDLE RESPONSE ---
if error:
    st.error(error)
else:
    st.success(f"Loaded {len(data)} entries for {player_name}")

    # --- FILTER ---
    min_value = st.slider("Minimum value (€m)", 0, 200, 0, step=5)
    filtered = [
        d for d in data 
        if d["value"] and int(d["value"].replace("€", "").replace(".", "").replace("m", "")) >= min_value
    ]

    st.subheader("📊 Market Value History")
    st.write(filtered)

    # --- PLOT ---
    try:
        df = pd.DataFrame(filtered)
        df = df[df["date"].notnull()]  # Remove null dates
        df["date"] = pd.to_datetime(df["date"], errors='coerce')
        df = df.dropna(subset=["date"])
        df["value_num"] = df["value"].str.extract(r"(\d+)").astype(float)
        st.line_chart(df.set_index("date")["value_num"])
    except Exception as e:
        st.warning(f"Could not display chart: {e}")

