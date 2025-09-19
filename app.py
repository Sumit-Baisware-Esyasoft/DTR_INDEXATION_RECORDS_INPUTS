import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="DTR से Consumer Indexation की प्रक्रिया", layout="centered")

# Title in Hindi
st.title("📑 DTR से Consumer Indexation की प्रक्रिया")

# Input fields
feeder_code = st.text_input("Feeder Code")
dtr_code = st.text_input("DTR Code")
dtr_meter_serial = st.text_input("DTR Meter Serial Number")

# --- Custom time picker (slider based) ---
def custom_time_picker(label):
    st.write(f"### {label}")
    col1, col2, col3 = st.columns([2,2,2])

    with col1:
        hour = st.slider(f"{label} - घंटा", 1, 12, 12)
    with col2:
        minute = st.slider(f"{label} - मिनट", 0, 59, 0)
    with col3:
        am_pm = st.radio(f"{label} - AM/PM", ["AM", "PM"], horizontal=True)

    time_str = f"{hour:02d}:{minute:02d} {am_pm}"
    return time_str

# Time inputs
dtr_off_time = custom_time_picker("DTR बंद करने का समय")
dtr_on_time = custom_time_picker("DTR चालू करने का समय")

# Date picker
date = st.date_input("दिनांक चुनें", datetime.today())

# File names
excel_file = "records.xlsx"
csv_file = "records.csv"

# Submit button
if st.button("Submit"):
    if feeder_code and dtr_code and dtr_meter_serial and dtr_off_time and dtr_on_time and date:
        # Prepare data
        new_data = {
            "Feeder Code": feeder_code,
            "DTR Code": dtr_code,
            "DTR Meter Serial Number": dtr_meter_serial,
            "DTR बंद करने का समय": dtr_off_time,
            "DTR चालू करने का समय": dtr_on_time,
            "दिनांक": date.strftime("%d-%m-%Y")
        }

        df_new = pd.DataFrame([new_data])

        # ---- Save to Excel ----
        if os.path.exists(excel_file):
            df_existing = pd.read_excel(excel_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_excel(excel_file, index=False)
        else:
            df_new.to_excel(excel_file, index=False)

        # ---- Save to CSV ----
        if os.path.exists(csv_file):
            df_new.to_csv(csv_file, mode="a", header=False, index=False, encoding="utf-8")
        else:
            df_new.to_csv(csv_file, index=False, encoding="utf-8")

        st.success("✅ डेटा सफलतापूर्वक सेव हो गया!")
        st.table(df_new)

    else:
        st.warning("⚠️ कृपया सभी फ़ील्ड भरें, फिर Submit करें।")
