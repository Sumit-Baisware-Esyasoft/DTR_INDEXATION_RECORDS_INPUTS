import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="DTR से Consumer Indexation की प्रक्रिया", layout="centered")

# Title in Hindi
st.title("📑 DTR से Consumer Indexation की प्रक्रिया")

# Load Google credentials from Streamlit Secrets
creds_dict = st.secrets["gcp_service_account"]

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

# Open your Google Sheet (make sure this name matches your actual sheet)
SHEET_NAME = "MyDTRSheet"
sheet = client.open(SHEET_NAME).sheet1

# --------- Form Inputs ----------
feeder_code = st.text_input("Feeder Code")
dtr_code = st.text_input("DTR Code")
dtr_meter_serial = st.text_input("DTR Meter Serial Number")

# --- Custom time picker (slider based) ---
def custom_time_picker(label):
    st.write(f"### {label}")
    col1, col2, col3 = st.columns([2,2,2])

    with col1:
        hour = st.slider(f"{label} - घंटा", 1, 12, 12, key=label+"hour")
    with col2:
        minute = st.slider(f"{label} - मिनट", 0, 59, 0, key=label+"minute")
    with col3:
        am_pm = st.radio(f"{label} - AM/PM", ["AM", "PM"], horizontal=True, key=label+"ampm")

    time_str = f"{hour:02d}:{minute:02d} {am_pm}"
    return time_str

# Time inputs
dtr_off_time = custom_time_picker("DTR बंद करने का समय")
dtr_on_time = custom_time_picker("DTR चालू करने का समय")

# Date picker
date = st.date_input("दिनांक चुनें", datetime.today())

# --------- Submit Button ----------
if st.button("Submit"):
    if feeder_code and dtr_code and dtr_meter_serial and dtr_off_time and dtr_on_time and date:
        new_data = [
            feeder_code,
            dtr_code,
            dtr_meter_serial,
            dtr_off_time,
            dtr_on_time,
            date.strftime("%d-%m-%Y")
        ]

        # Append row into Google Sheet
        sheet.append_row(new_data)

        st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया!")
        st.table(pd.DataFrame([new_data], columns=[
            "Feeder Code",
            "DTR Code",
            "DTR Meter Serial Number",
            "DTR बंद करने का समय",
            "DTR चालू करने का समय",
            "दिनांक"
        ]))
    else:
        st.warning("⚠️ कृपया सभी फ़ील्ड भरें, फिर Submit करें।")

# --------- Display Latest Records ----------
st.subheader("📋 सभी रिकॉर्ड्स")
records = sheet.get_all_records()
if records:
    df = pd.DataFrame(records)
    st.dataframe(df)
else:
    st.info("अभी तक कोई रिकॉर्ड सेव नहीं हुआ है।")
