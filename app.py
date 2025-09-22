import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="DTR से Consumer Indexation की प्रक्रिया", layout="centered")

# Title
st.title("📑 DTR से Consumer Indexation की प्रक्रिया")

# Load Google credentials
creds_dict = st.secrets["gcp_service_account"]
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

# Open Google Sheet
SHEET_NAME = "DTR_Indexation_Records"
sheet = client.open(SHEET_NAME).sheet1

# --------- Load Hierarchy File ----------
try:
    hierarchy_path = r"DTR Master Information 2025-09-22 07-00_21992_batch1.xlsx"
    hierarchy_df = pd.read_excel(hierarchy_path)

    region = st.selectbox("क्षेत्र (Region) चुनें", hierarchy_df["Region"].unique())
    circle = st.selectbox("सर्कल (Circle) चुनें", hierarchy_df[hierarchy_df["Region"] == region]["Circle"].unique())
    division = st.selectbox("डिवीजन (Division) चुनें", hierarchy_df[hierarchy_df["Circle"] == circle]["Division"].unique())
    zone = st.selectbox("ज़ोन (Zone) चुनें", hierarchy_df[hierarchy_df["Division"] == division]["Zone"].unique())
    substation = st.selectbox("उपकेंद्र (Substation) चुनें", hierarchy_df[hierarchy_df["Zone"] == zone]["Sub station"].unique())
    feeder = st.selectbox("फीडर (Feeder) चुनें", hierarchy_df[hierarchy_df["Sub station"] == substation]["Feeder"].unique())
    dtr = st.selectbox("डीटीआर (DTR) चुनें", hierarchy_df[hierarchy_df["Feeder"] == feeder]["Dtr"].unique())
    dtr_code = st.selectbox("डीटीआर कोड चुनें", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Dtr code"].unique())
    feeder_code = st.selectbox("फीडर कोड चुनें", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Feeder code"].unique())
    msn_auto = st.selectbox("मीटर सीरियल नंबर (MSN) चुनें", hierarchy_df[hierarchy_df["Dtr code"] == dtr_code]["Msn"].unique())

except Exception as e:
    st.error(f"⚠️ मास्टर फ़ाइल लोड करने में समस्या: {e}")
    region, circle, division, zone, substation, feeder, dtr, dtr_code, feeder_code, msn_auto = [None]*10

# --------- Confirm MSN ----------
final_msn = None
new_msn = None

if msn_auto:
    st.write(f"🔍 चुना गया MSN: **{msn_auto}**")
    confirm = st.radio("क्या यह MSN सही है?", ["हाँ, सही है ✅", "नहीं, बदलना है ❌"], horizontal=True)

    if confirm == "हाँ, सही है ✅":
        final_msn = msn_auto
    else:
        new_msn = st.text_input("नया MSN दर्ज करें")
        if new_msn:
            final_msn = new_msn

# --- Custom time picker ---
def custom_time_picker(label):
    st.write(f"### {label}")
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        hour = st.slider(f"{label} - घंटा", 1, 12, 12, key=label + "hour")
    with col2:
        minute = st.slider(f"{label} - मिनट", 0, 59, 0, key=label + "minute")
    with col3:
        am_pm = st.radio(f"{label} - AM/PM", ["AM", "PM"], horizontal=True, key=label + "ampm")

    time_str = f"{hour:02d}:{minute:02d} {am_pm}"
    return time_str

# Date & Time inputs (only when MSN confirmed)
if final_msn:
    dtr_off_time = custom_time_picker("डीटीआर बंद करने का समय")
    dtr_on_time = custom_time_picker("डीटीआर चालू करने का समय")
    date = st.date_input("दिनांक चुनें", datetime.today())

    # --------- Submit ----------
    if st.button("Submit"):
        new_data = [
            region, circle, division, zone, substation,
            feeder, dtr, dtr_code, feeder_code,
            msn_auto, new_msn if new_msn else "",  # नया MSN column
            final_msn, dtr_off_time, dtr_on_time, date.strftime("%d-%m-%Y")
        ]

        # Save in Google Sheet
        sheet.append_row(new_data)

        st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया!")
        st.table(pd.DataFrame([new_data], columns=[
            "क्षेत्र", "सर्कल", "डिवीजन", "ज़ोन", "उपकेंद्र",
            "फीडर", "डीटीआर", "डीटीआर कोड", "फीडर कोड",
            "Auto MSN", "New MSN", "Final MSN",
            "डीटीआर बंद करने का समय", "डीटीआर चालू करने का समय", "दिनांक"
        ]))

# --------- Display Records ----------
st.subheader("📋 सभी रिकॉर्ड्स")
records = sheet.get_all_records()
if records:
    df = pd.DataFrame(records)
    st.dataframe(df)
else:
    st.info("अभी तक कोई रिकॉर्ड सेव नहीं हुआ है।")
