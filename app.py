import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components

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

# --------- Analog Clock Time Picker ----------
def analog_clock_picker(label):
    """Custom analog clock picker using JS component"""
    st.markdown(f"### {label}")
    components.html(f"""
    <html>
    <head>
      <link href="https://cdn.jsdelivr.net/npm/mdtimepicker@0.6.3/mdtimepicker.min.css" rel="stylesheet">
    </head>
    <body style="font-family: sans-serif; text-align: center; padding-top: 10px;">
      <input id="{label}_picker" type="text" placeholder="Select time" style="font-size:20px; padding:8px; width:200px; text-align:center; border-radius:8px;">
      <script src="https://cdn.jsdelivr.net/npm/mdtimepicker@0.6.3/mdtimepicker.min.js"></script>
      <script>
        const tp = mdtimepicker('#{label}_picker', {{
            format: 'hh:mm tt',
            theme: 'purple',
            hourPadding: true
        }});
      </script>
    </body>
    </html>
    """, height=220)

    return st.text_input(f"{label} (मैन्युअल पुष्टि करें)", "")

# --------- Date & Time inputs ----------
if final_msn:
    dtr_off_time = analog_clock_picker("डीटीआर बंद करने का समय")
    dtr_on_time = analog_clock_picker("डीटीआर चालू करने का समय")
    date = st.date_input("दिनांक चुनें", datetime.today())

    # --------- Submit ----------
    if st.button("Submit"):
        if not dtr_off_time or not dtr_on_time:
            st.warning("⏰ कृपया दोनों समय भरें!")
        else:
            new_data = [
                region, circle, division, zone, substation,
                feeder, dtr, dtr_code, feeder_code,
                msn_auto, new_msn if new_msn else "",
                final_msn, dtr_off_time, dtr_on_time, date.strftime("%d-%m-%Y")
            ]
            sheet.append_row(new_data)

            st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया!")
            st.table(pd.DataFrame([new_data], columns=[
                "क्षेत्र", "सर्कल", "डिवीजन", "ज़ोन", "उपकेंद्र",
                "फीडर", "डीटीआर", "डीटीआर कोड", "फीडर कोड",
                "Auto MSN", "New MSN", "Final MSN",
                "डीटीआर बंद करने का समय", "डीटीआर चालू करने का समय", "दिनांक"
            ]))
