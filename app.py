import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="DTR से Consumer Indexation की प्रक्रिया",
    page_icon="📑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------- HEADER -----------------
st.markdown("""
    <h1 style='text-align: center; color: #004aad; font-size: 36px;'>
        ⚡ DTR से Consumer Indexation की प्रक्रिया
    </h1>
    <p style='text-align: center; color: gray; font-size: 18px;'>
        कृपया नीचे दी गई जानकारी ध्यानपूर्वक भरें।
    </p>
    <hr style='margin-top: 10px; margin-bottom: 20px;'>
""", unsafe_allow_html=True)

# ----------------- GOOGLE SHEET CONNECTION -----------------
creds_dict = st.secrets["gcp_service_account"]
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)
sheet = client.open("DTR_Indexation_Records").sheet1

# ----------------- LOAD HIERARCHY -----------------


try:
    hierarchy_path = r"DTR Master Information 2025-09-22 07-00_21992_batch1.xlsx"
    hierarchy_df = pd.read_excel(hierarchy_path)

    with st.expander("🔽 विवरण चुनें", expanded=True):
        region = st.selectbox("🌍 क्षेत्र (Region)", hierarchy_df["Region"].unique())
        circle = st.selectbox("🏛️ सर्कल (Circle)", hierarchy_df[hierarchy_df["Region"] == region]["Circle"].unique())
        division = st.selectbox("🏢 डिवीजन (Division)", hierarchy_df[hierarchy_df["Circle"] == circle]["Division"].unique())
        zone = st.selectbox("🏠 वितरण केंद्र (Zone)", hierarchy_df[hierarchy_df["Division"] == division]["Zone"].unique())
        substation = st.selectbox("⚙️ उपकेंद्र (Substation)", hierarchy_df[hierarchy_df["Zone"] == zone]["Sub station"].unique())
        feeder = st.selectbox("🔌 फीडर (Feeder)", hierarchy_df[hierarchy_df["Sub station"] == substation]["Feeder"].unique())
        dtr = st.selectbox("🧭 डीटीआर (DTR)", hierarchy_df[hierarchy_df["Feeder"] == feeder]["Dtr"].unique())
        dtr_code = st.selectbox("📟 डीटीआर कोड", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Dtr code"].unique())
        feeder_code = st.selectbox("💡 फीडर कोड", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Feeder code"].unique())
        msn_auto = st.selectbox("🔢 मीटर सीरियल नंबर (MSN)", hierarchy_df[hierarchy_df["Dtr code"] == dtr_code]["Msn"].unique())

except Exception as e:
    st.error(f"⚠️ मास्टर फ़ाइल लोड करने में समस्या: {e}")
    region, circle, division, zone, substation, feeder, dtr, dtr_code, feeder_code, msn_auto = [None]*10

# ----------------- CONFIRM MSN -----------------
final_msn = None
new_msn = None

if msn_auto:
    st.markdown("### ✅ मीटर सीरियल नंबर की पुष्टि करें")
    st.info(f"🔍 चुना गया मीटर सीरियल नंबर: **{msn_auto}**")
    confirm = st.radio("क्या यह मीटर सीरियल नंबर सही है?", ["हाँ, सही है ✅", "नहीं, बदलना है ❌"], horizontal=True)

    if confirm == "हाँ, सही है ✅":
        final_msn = msn_auto
    else:
        new_msn = st.text_input("✏️ नया मीटर सीरियल नंबर दर्ज करें")
        if new_msn:
            final_msn = new_msn

# ----------------- TIME PICKER FUNCTION -----------------
def simple_time_picker(label, key):
    st.markdown(f"**{label}**")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        hour = st.selectbox("Hour", [f"{i:02d}" for i in range(1,13)], key=f"{key}_hour")
    with col2:
        minute = st.selectbox("Minute", [f"{i:02d}" for i in range(0,60)], key=f"{key}_minute")
    with col3:
        am_pm = st.selectbox("AM/PM", ["AM","PM"], key=f"{key}_ampm")
    return f"{hour}:{minute} {am_pm}"

# ----------------- DATE & TIME -----------------
if final_msn:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("⏱️ डीटीआर समय विवरण")

    dtr_off_time = simple_time_picker("डीटीआर बंद करने का समय", "off_time")
    dtr_on_time = simple_time_picker("डीटीआर चालू करने का समय", "on_time")
    date = st.date_input("📅 दिनांक चुनें", datetime.today())
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("👤 अधिकारी की जानकारी")
    ae_je_name = st.text_input("👨‍💼 AE/JE का नाम")
    mobile_number = st.text_input("📱 मोबाइल नंबर", max_chars=10, placeholder="10 अंकों का मोबाइल नंबर दर्ज करें")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)



   # ----------------- SUBMIT -----------------
    if st.button("💾 सबमिट करें", use_container_width=True, type="primary"):
       new_data = [
         region, circle, division, zone, substation,
         feeder, dtr, dtr_code, feeder_code,
         msn_auto, new_msn if new_msn else "",
         final_msn, dtr_off_time, dtr_on_time, date.strftime("%d-%m-%Y"),
          ae_je_name, mobile_number   # ✅ Added two new columns at the end
       ]
        sheet.append_row(new_data)
        st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया!")

# ----------------- FOOTER -----------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 15px;'>
        <b>Developed by Esyasoft GIS Team</b> | © 2025<br>
        <span style='color:#004aad;'>DTR Indexation Portal</span>
    </div>
""", unsafe_allow_html=True)


st.image("download (1).png", width=150, caption="Esyasoft Technologies", use_container_width=False)
