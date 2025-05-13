import streamlit as st
import requests
import pandas as pd

# --- CONFIGURATION ---
# Load your RapidAPI key securely from Streamlit secrets
RAPID_API_KEY = st.secrets["RAPID_API_KEY"]
API_HOST = "transfermarkt6.p.rapidapi.com"

# --- PREDEFINED PLAYER OPTIONS ---
player_options = {
    "Lionel Messi": "28003",
    "Cristiano Ronaldo": "8198",
    "Erling Haaland": "418560"
}

# --- PAGE HEADER ---
st.set_page_config(page_title="Market Value Tracker", page_icon="⚽")
st.title("⚽ Player Market Value Tracker")

# --- PLAYER INPUT OPTIONS ---
# Allow users to choose from a list or enter a custom player ID
use_custom = st.checkbox("🔍 Enter custom player ID", value=False)

if use_custom:
    player_id = st.text_input("Enter Transfermarkt Player ID (e.g., 28003 for Messi)", value="28003")
    player_name = "Custom Player"
else:
    player_name = st.selectbox("Choose a player", list(player_options.keys()))
    player_id = player_options[player_name]

# --- FUNCTION TO FETCH MARKET VALUE DATA ---
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

# --- FETCH & HANDLE API DATA ---
data, error = get_market_values(player_id)

if error:
    st.error(error)
else:
    st.success(f"Loaded {len(data)} entries for {player_name}")

    # --- VALUE FILTER ---
    min_value = st.slider("Minimum value (€m)", 0, 200, 0, step=5)

    # Filter records based on minimum value
    filtered = [
        d for d in data 
        if d["value"] and int(d["value"].replace("€", "").replace(".", "").replace("m", "")) >= min_value
    ]

    # --- DATA DISPLAY + PROFILE LINK ---
    st.subheader("📊 Market Value History")
    if filtered and "profile" in filtered[0]:
        st.markdown(f"🔗 [View Profile on Transfermarkt]({filtered[0]['profile']})")

    # --- DATA TABLE ---
    st.dataframe(pd.DataFrame(filtered))

    # --- EXPORT TO CSV BUTTON ---
    csv = pd.DataFrame(filtered).to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"{player_name}_market_value.csv",
        mime="text/csv"
    )

    # --- CHART VISUALIZATION ---
    try:
        df = pd.DataFrame(filtered)
        df = df[df["date"].notnull()]  # remove empty dates
        df["date"] = pd.to_datetime(df["date"], errors='coerce')
        df = df.dropna(subset=["date"])
        df["value_num"] = df["value"].str.extract(r"(\d+)").astype(float)
        st.line_chart(df.set_index("date")["value_num"])
    except Exception as e:
        st.warning(f"Could not display chart: {e}")

