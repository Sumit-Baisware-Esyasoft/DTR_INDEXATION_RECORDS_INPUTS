import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components

st.set_page_config(page_title="DTR से Consumer Indexation की प्रक्रिया", layout="centered")

# Title
st.title("📑 DTR से Consumer Indexation की प्रक्रिया")

# Load Google credentials (ensure you set st.secrets["gcp_service_account"])
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

# --------- Scroll (wheel) Time Picker Component ----------
def scroll_time_picker(label: str, key_prefix: str, height: int = 280) -> str:
    """
    Scrollable hour/minute/AMPM picker using JS component.
    Stores selected time in st.session_state[key_prefix].
    """
    st.markdown(f"### {label}")
    html_template = r"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; margin: 0; padding: 8px; }
        .picker-container { display:flex; justify-content:center; align-items:center; gap:12px; margin-top:10px; }
        select { font-size:20px; padding:6px; border-radius:8px; border:1px solid #ccc; width:90px; text-align:center; }
        #{KEY}_ok { margin-top:12px; padding:8px 18px; font-size:16px; border-radius:8px; background:#4B2C83; color:white; border:none; cursor:pointer; }
      </style>
    </head>
    <body>
      <div class="picker-container">
        <select id="{KEY}_hour" aria-label="hour"><option value="" disabled selected>HH</option></select>
        <span style="font-size:20px;">:</span>
        <select id="{KEY}_minute" aria-label="minute"><option value="" disabled selected>MM</option></select>
        <select id="{KEY}_ampm" aria-label="ampm"><option value="AM">AM</option><option value="PM">PM</option></select>
      </div>
      <div style="text-align:center;">
        <button id="{KEY}_ok">OK</button>
      </div>
      <script>
        (function() {{
          var hourSelect = document.getElementById("{KEY}_hour");
          for(var i=1;i<=12;i++){{
            var v = (i<10?'0'+i:''+i);
            var o = document.createElement('option'); o.value=v;o.text=v;hourSelect.appendChild(o);
          }}
          var minSelect = document.getElementById("{KEY}_minute");
          for(var j=0;j<60;j++){{
            var mv = (j<10?'0'+j:''+j);
            var mo = document.createElement('option'); mo.value=mv;mo.text=mv;minSelect.appendChild(mo);
          }}
          document.getElementById("{KEY}_ok").addEventListener('click', function(){{
            var h=document.getElementById("{KEY}_hour").value;
            var m=document.getElementById("{KEY}_minute").value;
            var a=document.getElementById("{KEY}_ampm").value;
            if(!h || !m){{ alert("कृपया Hour और Minute चुनें।"); return; }}
            var time=h+":"+m+" "+a;
            window.parent.postMessage({{type:'streamlit:customTime', key:'{KEY}', value:time}}, '*');
          }});
        }})();
      </script>
    </body>
    </html>
    """
    html = html_template.replace("{KEY}", key_prefix)
    components.html(html, height=height, scrolling=False, key=f"comp_{key_prefix}")

    # Return value from session_state (set by JS)
    return st.session_state.get(key_prefix, "")

# --------- Date & Time inputs (only when MSN confirmed) ----------
if final_msn:
    st.markdown("---")
    st.subheader("🕒 डीटीआर का समय और दिनांक चुनें")

    # Render scroll pickers; they will store into session_state keys "off_time" and "on_time"
    off_time = scroll_time_picker("डीटीआर बंद करने का समय", key_prefix="off_time")
    on_time = scroll_time_picker("डीटीआर चालू करने का समय", key_prefix="on_time")

    # Show chosen times
    col1, col2 = st.columns(2)
    with col1:
        st.write("**चुना गया बंद समय:**", off_time if off_time else "—")
    with col2:
        st.write("**चुना गया चालू समय:**", on_time if on_time else "—")

    date = st.date_input("दिनांक चुनें", datetime.today())

    # --------- Submit ----------
    if st.button("Submit"):
        # Basic validation
        if not off_time or not on_time:
            st.warning("कृपया दोनों समय चुनकर OK दबाएँ।")
        else:
            new_data = [
                region, circle, division, zone, substation,
                feeder, dtr, dtr_code, feeder_code,
                msn_auto, new_msn if new_msn else "",
                final_msn, off_time, on_time, date.strftime("%d-%m-%Y")
            ]

            # Save in Google Sheet
            try:
                sheet.append_row(new_data)
                st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया!")
                st.table(pd.DataFrame([new_data], columns=[
                    "क्षेत्र", "सर्कल", "डिवीजन", "ज़ोन", "उपकेंद्र",
                    "फीडर", "डीटीआर", "डीटीआर कोड", "फीडर कोड",
                    "Auto MSN", "New MSN", "Final MSN",
                    "डीटीआर बंद करने का समय", "डीटीआर चालू करने का समय", "दिनांक"
                ]))
            except Exception as e:
                st.error(f"⚠️ Google Sheet में सेव करने में त्रुटि: {e}")
