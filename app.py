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


# --------- Custom Scroll Time Picker ---------
def scroll_time_picker(label, key_prefix):
    st.markdown(f"### {label}")
    components.html(f"""
    <html>
    <head>
    <style>
      body {{ font-family: sans-serif; text-align: center; }}
      .picker-container {{
        display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 10px;
      }}
      select {{
        font-size: 24px; padding: 8px; border-radius: 8px;
        border: 2px solid #6f42c1; background: white; text-align: center; width: 100px;
      }}
    </style>
    </head>
    <body>
      <div class="picker-container">
        <select id="{key_prefix}_hour">
          <option value="" disabled selected>HH</option>
          <script>
            for(let i=1;i<=12;i++){{
              let val = i.toString().padStart(2,'0');
              document.write(`<option value="${{val}}">${{val}}</option>`);
            }}
          </script>
        </select>
        <span style="font-size:24px;">:</span>
        <select id="{key_prefix}_minute">
          <option value="" disabled selected>MM</option>
          <script>
            for(let i=0;i<60;i++){{
              let val = i.toString().padStart(2,'0');
              document.write(`<option value="${{val}}">${{val}}</option>`);
            }}
          </script>
        </select>
        <select id="{key_prefix}_ampm">
          <option value="AM">AM</option>
          <option value="PM">PM</option>
        </select>
      </div>
      <button id="{key_prefix}_ok" style="margin-top: 15px; padding: 8px 20px; font-size: 18px;
        background-color: #6f42c1; color: white; border: none; border-radius: 8px; cursor: pointer;">
        OK
      </button>

      <script>
        const btn = document.getElementById("{key_prefix}_ok");
        btn.addEventListener("click", () => {{
          const h = document.getElementById("{key_prefix}_hour").value;
          const m = document.getElementById("{key_prefix}_minute").value;
          const a = document.getElementById("{key_prefix}_ampm").value;
          if(!h || !m){{ alert("Please select hour and minute."); return; }}
          const time = `${{h}}:${{m}} ${{a}}`;
          const event = {{ type: "streamlit:setComponentValue", value: time }};
          window.parent.postMessage(event, "*");
        }});
      </script>
    </body>
    </html>
    """, height=300, key=key_prefix)


# --------- Time + Date input only when MSN confirmed ---------
if final_msn:
    st.markdown("---")
    st.subheader("🕒 समय और दिनांक दर्ज करें")

    st.markdown("#### डीटीआर बंद करने का समय")
    scroll_time_picker("डीटीआर बंद करने का समय", key_prefix="off")

    st.markdown("#### डीटीआर चालू करने का समय")
    scroll_time_picker("डीटीआर चालू करने का समय", key_prefix="on")

    date = st.date_input("दिनांक चुनें", datetime.today())

    # Submit button
    if st.button("Submit"):
        dtr_off_time = st.session_state.get("off_time", "")
        dtr_on_time = st.session_state.get("on_time", "")
        new_data = [
            region, circle, division, zone, substation, feeder,
            dtr, dtr_code, feeder_code, msn_auto, new_msn if new_msn else "",
            final_msn, dtr_off_time, dtr_on_time, date.strftime("%d-%m-%Y")
        ]
        sheet.append_row(new_data)

        st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया!")
        st.table(pd.DataFrame([new_data], columns=[
            "क्षेत्र", "सर्कल", "डिवीजन", "ज़ोन", "उपकेंद्र", "फीडर", "डीटीआर", "डीटीआर कोड",
            "फीडर कोड", "Auto MSN", "New MSN", "Final MSN", "डीटीआर बंद करने का समय",
            "डीटीआर चालू करने का समय", "दिनांक"
        ]))
