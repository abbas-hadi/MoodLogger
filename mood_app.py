import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="data_refresh")

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("wise-baton-461122-f1-83caeddbbeaa.json", scope)
client = gspread.authorize(creds)
sheet = client.open("MoodLogger").sheet1  # Make sure your Sheet name matches

# Streamlit UI
st.set_page_config(page_title="Mood of the Queue", page_icon="🧠")
st.title("🧠 Mood of the Queue")

# Mood Entry Form
with st.form("mood_form"):
    st.subheader("Log a Mood")
    mood = st.radio("How does the queue feel right now?", ["😊", "😠", "😕", "🎉"])
    note = st.text_input("Optional note:")
    submitted = st.form_submit_button("Log Mood")
    if submitted:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, mood, note])
        st.success("✅ Mood logged!")

st.divider()

# Mood Visualization
st.header("📊 Mood Trends")

# Load data from Google Sheet
data = sheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    st.subheader("📅 Select a Date")
    selected_date = st.date_input("Choose a date", value=date.today())
    filtered_df = df[df["timestamp"].dt.date == selected_date]

    if not filtered_df.empty:
        chart = filtered_df["mood"].value_counts().reset_index()
        chart.columns = ["mood", "count"]
        fig = px.bar(chart, x="mood", y="count", title=f"Mood Count for {selected_date.strftime('%b %d')}", color="mood")
        st.plotly_chart(fig)
        st.markdown("### 🧾 Recent Logs")
        st.dataframe(filtered_df.sort_values(by="timestamp", ascending=False).head(5))
    else:
        st.info("No moods logged for this day.")
else:
    st.info("No mood entries found yet.")

