import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="DTR से Smart Metered Consumer Indexing की प्रक्रिया",
    page_icon="📑",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# st.markdown(
#     """
#     <div style='text-align: center; margin-bottom: 20px;'>
#         <img src='mpez-logo.png' width='120'>
#     </div>
#     """,
#     unsafe_allow_html=True
# )
# ----------------- CUSTOM CSS -----------------
st.markdown("""
    <style>
        /* Center logo */
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 10px;
        }

        /* Change dropdown background and text color */
        div[data-baseweb="select"] > div {
            background-color: #f0f4ff !important;  /* Light blue background */
            color: #000000 !important;             /* Black text */
            border: 1px solid #004aad !important;  /* Blue border */
            border-radius: 8px;
        }

        /* Change hover color */
        div[data-baseweb="select"]:hover > div {
            background-color: #e3ecff !important;  /* Slightly darker on hover */
        }

        /* Dropdown menu list color */
        ul[role="listbox"] {
            background-color: #ffffff !important;  /* White dropdown list */
            color: #000000 !important;
            border-radius: 6px;
        }

        /* Change font and highlight color */
        .stSelectbox label {
            color: #004aad !important;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# # ----------------- LOGO SECTION -----------------
# st.markdown(
#     """
#     <div class='logo-container'>
#         <img src='https://www.bing.com/images/search?view=detailV2&ccid=eZyl3t6q&id=DD1EE906728970266B93176F58AF9C706AE2A8BC&thid=OIP.eZyl3t6qEyxh1tfNfghJ3wAAAA&mediaurl=https%3a%2f%2fmedia.9curry.com%2fuploads%2forganization%2fimage%2f987%2fmpez-logo.png&exph=320&expw=320&q=mpez+logo&FORM=IRPRST&ck=F845CB955318706BFD28DB2820923F52&selectedIndex=0&itb=0' width='120'>
#     </div>
#     """,
#     unsafe_allow_html=True
# )


# ----------------- HEADER -----------------
st.markdown("""
    <h1 style='text-align: center; color: #004aad; font-size: 36px;'>
        ⚡DTR से Smart Metered Consumer Indexating की प्रक्रियाा
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
        # zone = st.selectbox("🏠 वितरण केंद्र (Zone)", hierarchy_df[hierarchy_df["Division"] == division]["Zone"].unique())
        substation = st.selectbox("⚙️ उपकेंद्र (Substation)", hierarchy_df[hierarchy_df["Division"] == division]["Sub station"].unique())
        feeder = st.selectbox("🔌 फीडर (Feeder)", hierarchy_df[hierarchy_df["Sub station"] == substation]["Feeder"].unique())
        dtr = st.selectbox("🧭 डीटीआर का प्रचलित नाम (DTR)", hierarchy_df[hierarchy_df["Feeder"] == feeder]["Dtr"].unique())
        feeder_code = st.selectbox("💡 फीडर कोड", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Feeder code"].unique())
        
        dtr_code = st.selectbox("📟 डीटीआर कोड", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Dtr code"].unique())
        msn_auto = st.selectbox("🔢डीटीआर मीटर सीरियल नंबर (MSN)", hierarchy_df[hierarchy_df["Dtr code"] == dtr_code]["Msn"].unique())

except Exception as e:
    st.error(f"⚠️ मास्टर फ़ाइल लोड करने में समस्या: {e}")
    region, circle, division, zone, substation, feeder, dtr, dtr_code, feeder_code, msn_auto = [None]*10

# ----------------- CONFIRM MSN -----------------
final_msn = None
new_msn = None

if msn_auto:
    st.markdown("### ✅ डीटीआर मीटर सीरियल नंबर की पुष्टि करें")
    st.info(f"🔍 MDM में दर्ज डीटीआर मीटर सीरियल नंबर: **{msn_auto}**")
    confirm = st.radio("क्या यह डीटीआर मीटर सीरियल नंबर सही है?", ["हाँ, सही है ✅", "नहीं, बदलना है ❌"], horizontal=True)

    if confirm == "हाँ, सही है ✅":
        final_msn = msn_auto
    else:
        new_msn = st.text_input("✏️ नया डीटीआर मीटर सीरियल नंबर दर्ज करें")
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
    st.subheader("⏱️ डीटीआर के द्वारा सप्लाई बंद करने का विवरण")
    date = st.date_input("📅 दिनांक चुनें", datetime.today())
    dtr_off_time = simple_time_picker("डीटीआर से विद्युत् आपूर्ति बंद करने का समय", "off_time")
    dtr_on_time = simple_time_picker("डीटीआर से विद्युत् आपूर्ति चालू करने का समय", "on_time")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("👤 सम्बंधित अधिकारी की जानकारी")
    ae_je_name = st.text_input("👨‍💼 AE/JE का नाम")
    mobile_number = st.text_input("📱 मोबाइल नंबर", max_chars=10, placeholder="10 अंकों का मोबाइल नंबर दर्ज करें")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)



   # ----------------- SUBMIT -----------------
    # ----------------- SUBMIT -----------------
    if st.button("💾 सबमिट करें", use_container_width=True, type="primary"):
        new_data = [
            region, circle, division, substation,
            feeder, dtr, dtr_code, feeder_code,
            msn_auto, new_msn if new_msn else "",
            final_msn, dtr_off_time, dtr_on_time, date.strftime("%d-%m-%Y"),
            ae_je_name, mobile_number   # ✅ Added two new columns at the end
        ]
        application_number = f"{datetime.now().strftime('%d%m')}{len(sheet.get_all_values()) + 1:04d}"
        new_data.append(application_number)   # ✅ add unique application number
        sheet.append_row(new_data)
        # sheet.append_row(new_data)
        st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया!")
# ✅ Display confirmation box with key details
        st.markdown("""
            <div style="
                border: 2px solid #004aad;
                border-radius: 12px;
                padding: 15px;
                background-color: #f0f4ff;
                margin-top: 15px;
                ">
                <h4 style="color:#004aad; text-align:center; margin-bottom:10px;">🔎 सबमिट किया गया विवरण</h4>
                <p><b>🧾 आवेदन संख्या (Application No.):</b> {application_number}</p>
                <p><b>🌐 फीडर (Feeder):</b> {feeder}</p>
                <p><b>💡 फीडर कोड:</b> {feeder_code}</p>
                <p><b>🧭 डीटीआर का प्रचलित नाम:</b> {dtr}</p>
                <p><b>🔢 डीटीआर MSN:</b> {final_msn}</p>
                <p><b>⏰ डीटीआर बंद करने का समय:</b> {off_time}</p>
                <p><b>⚡ डीटीआर चालू करने का समय:</b> {on_time}</p>
                <p><b>📅 दिनांक:</b> {date.strftime("%d-%m-%Y")}</p>
            </div>
        """.format(
            application_number= application_number,
            feeder=feeder,
            feeder_code=feeder_code,
            dtr=dtr,
            final_msn=final_msn,
            off_time=dtr_off_time,
            on_time=dtr_on_time,
            date=date.strftime("%d-%m-%Y")
        ), unsafe_allow_html=True)
        st.subheader("📸 आप उक्त जानकारी का स्क्रीनशॉट अपने फोन पर सुरक्षित रख सकते है ")


# ----------------- FOOTER -----------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 15px;'>
        <b>Developed by Esyasoft Team</b> | © 2025<br>
        <span style='color:#004aad;'>DTR Indexation Portal</span>
    </div>
""", unsafe_allow_html=True)


st.image("download (1).png", width=150, caption="Esyasoft Technologies", use_container_width=False)
