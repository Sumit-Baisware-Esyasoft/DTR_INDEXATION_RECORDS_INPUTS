import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="DTR Smart Meter Indexing Portal",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------- CUSTOM CSS -----------------
st.markdown("""
    <style>
        /* Main background styling */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, #004aad 0%, #002966 100%);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0, 74, 173, 0.4);
            text-align: center;
            border-left: 6px solid #ffd700;
            border-right: 6px solid #ffd700;
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 1%);
            background-size: 20px 20px;
            animation: sparkle 4s linear infinite;
        }
        
        @keyframes sparkle {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Card styling */
        .custom-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .custom-card:hover {
            box-shadow: 0 6px 20px rgba(0, 74, 173, 0.15);
            border-color: #004aad;
            transform: translateY(-2px);
        }
        
        /* Success card */
        .success-card {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 2px solid #28a745;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
        }
        
        /* Dropdown styling */
        div[data-baseweb="select"] > div {
            background-color: #f8f9fa !important;
            color: #000000 !important;
            border: 2px solid #004aad !important;
            border-radius: 10px;
            padding: 10px;
            font-weight: 500;
        }
        
        div[data-baseweb="select"]:hover > div {
            background-color: #e3ecff !important;
            border-color: #002966 !important;
        }
        
        ul[role="listbox"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            border-radius: 10px;
            border: 2px solid #004aad;
        }
        
        .stSelectbox label {
            color: #004aad !important;
            font-weight: 700;
            font-size: 16px;
        }
        
        /* Button styling */
        .stButton button {
            background: linear-gradient(135deg, #004aad 0%, #002966 100%) !important;
            color: white !important;
            border: none !important;
            padding: 12px 30px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 18px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 74, 173, 0.4) !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 74, 173, 0.6) !important;
            background: linear-gradient(135deg, #002966 0%, #004aad 100%) !important;
        }
        
        /* Text input styling */
        .stTextInput input {
            border: 2px solid #004aad !important;
            border-radius: 10px !important;
            padding: 12px !important;
            font-size: 16px !important;
        }
        
        /* Date input styling */
        .stDateInput input {
            border: 2px solid #004aad !important;
            border-radius: 10px !important;
            padding: 12px !important;
        }
        
        /* Radio button styling */
        .stRadio > div {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #004aad 0%, #002966 100%) !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 18px !important;
        }
        
        /* Footer styling */
        .footer {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-top: 30px;
            box-shadow: 0 -4px 15px rgba(0, 0, 0, 0.1);
        }
        
        /* Icon styling */
        .icon-large {
            font-size: 24px;
            margin-right: 10px;
        }
        
        /* Progress indicator */
        .progress-container {
            display: flex;
            justify-content: space-between;
            margin: 30px 0;
            position: relative;
        }
        
        .progress-step {
            text-align: center;
            z-index: 2;
            background: white;
            padding: 10px;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 3px solid #004aad;
            font-weight: bold;
            color: #004aad;
        }
        
        .progress-line {
            position: absolute;
            top: 25px;
            left: 0;
            right: 0;
            height: 3px;
            background: #e0e0e0;
            z-index: 1;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- ATTRACTIVE HEADER -----------------
st.markdown("""
    <div class='main-header'>
        <h1 style='
            color: white; 
            font-size: 32px; 
            margin: 0;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            letter-spacing: 0.5px;
        '>
            ⚡ DTR Smart Metered Consumer Indexing Process
        </h1>
        <p style='
            color: #e6f2ff; 
            font-size: 18px; 
            margin: 10px 0 0 0;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        '>
            कृपया नीचे दी गई जानकारी ध्यानपूर्वक भरें | Please fill the below information carefully
        </p>
    </div>
""", unsafe_allow_html=True)

# ----------------- PROGRESS INDICATOR -----------------
st.markdown("""
    <div class='progress-container'>
        <div class='progress-line'></div>
        <div class='progress-step'>1</div>
        <div class='progress-step'>2</div>
        <div class='progress-step'>3</div>
        <div class='progress-step'>4</div>
    </div>
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
st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
st.markdown("### 🗂️ सिस्टम जानकारी | System Information")

try:
    hierarchy_path = r"DTR Master Information 2025-09-22 07-00_21992_batch1.xlsx"
    hierarchy_df = pd.read_excel(hierarchy_path)

    with st.expander("🔽 विवरण चुनें | Select Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            region = st.selectbox("🌍 क्षेत्र (Region)", hierarchy_df["Region"].unique())
            circle = st.selectbox("🏛️ सर्कल (Circle)", hierarchy_df[hierarchy_df["Region"] == region]["Circle"].unique())
            division = st.selectbox("🏢 डिवीजन (Division)", hierarchy_df[hierarchy_df["Circle"] == circle]["Division"].unique())
            substation = st.selectbox("⚙️ उपकेंद्र (Substation)", hierarchy_df[hierarchy_df["Division"] == division]["Sub station"].unique())
        
        with col2:
            feeder = st.selectbox("🔌 फीडर (Feeder)", hierarchy_df[hierarchy_df["Sub station"] == substation]["Feeder"].unique())
            dtr = st.selectbox("🧭 डीटीआर का नाम (DTR Name)", hierarchy_df[hierarchy_df["Feeder"] == feeder]["Dtr"].unique())
            feeder_code = st.selectbox("💡 फीडर कोड (Feeder Code)", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Feeder code"].unique())
            dtr_code = st.selectbox("📟 डीटीआर कोड (DTR Code)", hierarchy_df[hierarchy_df["Dtr"] == dtr]["Dtr code"].unique())

except Exception as e:
    st.error(f"⚠️ मास्टर फ़ाइल लोड करने में समस्या | Error loading master file: {e}")
    region, circle, division, substation, feeder, dtr, dtr_code, feeder_code = [None]*8

st.markdown("</div>", unsafe_allow_html=True)

# ----------------- MSN CONFIRMATION -----------------
if dtr_code:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    
    try:
        msn_auto = st.selectbox("🔢 डीटीआर मीटर सीरियल नंबर (DTR Meter Serial Number)", 
                               hierarchy_df[hierarchy_df["Dtr code"] == dtr_code]["Msn"].unique(),
                               key="msn_auto")
        
        final_msn = None
        new_msn = None

        if msn_auto:
            st.markdown("### ✅ डीटीआर मीटर सीरियल नंबर की पुष्टि करें | Confirm DTR Meter Serial Number")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.info(f"**🔍 MDM में दर्ज डीटीआर मीटर सीरियल नंबर:** {msn_auto}")
            with col2:
                confirm = st.radio("क्या यह सही है? | Is this correct?", 
                                 ["हाँ, सही है ✅", "नहीं, बदलना है ❌"], 
                                 horizontal=True)

            if confirm == "हाँ, सही है ✅":
                final_msn = msn_auto
                st.success("✅ मीटर सीरियल नंबर स्वीकृत | Meter Serial Number Approved")
            else:
                new_msn = st.text_input("✏️ नया डीटीआर मीटर सीरियल नंबर दर्ज करें | Enter New DTR Meter Serial Number",
                                       placeholder="नया सीरियल नंबर दर्ज करें")
                if new_msn:
                    final_msn = new_msn
                    st.success("✅ नया मीटर सीरियल नंबर स्वीकृत | New Meter Serial Number Approved")
    
    except Exception as e:
        st.error(f"⚠️ MSN लोड करने में त्रुटि | Error loading MSN: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- TIME PICKER FUNCTION -----------------
def attractive_time_picker(label, key):
    st.markdown(f"**{label}**")
    col1, col2, col3, col4 = st.columns([1,1,1,2])
    with col1:
        hour = st.selectbox("घंटा | Hour", [f"{i:02d}" for i in range(1,13)], key=f"{key}_hour")
    with col2:
        minute = st.selectbox("मिनट | Minute", [f"{i:02d}" for i in range(0,60)], key=f"{key}_minute")
    with col3:
        am_pm = st.selectbox("AM/PM", ["AM","PM"], key=f"{key}_ampm")
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"**चयनित समय:** {hour}:{minute} {am_pm}")
    return f"{hour}:{minute} {am_pm}"

# ----------------- DATE & TIME SECTION -----------------
if 'final_msn' in locals() and final_msn:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### ⏱️ डीटीआर संचालन समय | DTR Operation Timing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 दिनांक | Date")
        date = st.date_input("तारीख चुनें | Select Date", datetime.today(), label_visibility="collapsed")
        
    with col2:
        st.markdown("#### 🕒 समय | Time")
        dtr_off_time = attractive_time_picker("बंद करने का समय | Shutdown Time", "off_time")
        dtr_on_time = attractive_time_picker("चालू करने का समय | Startup Time", "on_time")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- OFFICER INFORMATION -----------------
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### 👤 अधिकारी जानकारी | Officer Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ae_je_name = st.text_input("👨‍💼 AE/JE का नाम | AE/JE Name", 
                                 placeholder="अधिकारी का पूरा नाम दर्ज करें")
    
    with col2:
        mobile_number = st.text_input("📱 मोबाइल नंबर | Mobile Number", 
                                    max_chars=10, 
                                    placeholder="10 अंकों का नंबर दर्ज करें")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- SUBMIT BUTTON -----------------
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 डेटा सबमिट करें | Submit Data", use_container_width=True, type="primary"):
        if not ae_je_name or not mobile_number:
            st.error("❌ कृपया अधिकारी का नाम और मोबाइल नंबर दर्ज करें | Please enter officer name and mobile number")
        elif len(mobile_number) != 10 or not mobile_number.isdigit():
            st.error("❌ कृपया वैध 10-अंकीय मोबाइल नंबर दर्ज करें | Please enter valid 10-digit mobile number")
        else:
            try:
                application_number = f"{datetime.now().strftime('%d%m%Y')}{len(sheet.get_all_values()) + 1:04d}"
                new_data = [
                    region, circle, division, substation,
                    feeder, dtr, dtr_code, feeder_code,
                    msn_auto, new_msn if new_msn else "",
                    final_msn, dtr_off_time, dtr_on_time, date.strftime("%d-%m-%Y"),
                    ae_je_name, mobile_number, application_number
                ]
                
                sheet.append_row(new_data)
                
                # SUCCESS MESSAGE
                st.balloons()
                st.markdown("<div class='custom-card success-card'>", unsafe_allow_html=True)
                st.markdown("### 🎉 सफलता | Success!")
                st.success("✅ डेटा सफलतापूर्वक Google Sheet में सेव हो गया! | Data successfully saved to Google Sheet!")
                
                # CONFIRMATION DETAILS
                st.markdown("""
                    <div style="
                        border: 2px solid #28a745;
                        border-radius: 12px;
                        padding: 20px;
                        background: linear-gradient(135deg, #f8fff9 0%, #e8f5e8 100%);
                        margin: 15px 0;
                        font-size:16px;
                        line-height:1.8;
                    ">
                        <h4 style="color:#28a745; text-align:center; margin-bottom:15px;">
                            📋 सबमिट किया गया विवरण | Submitted Details
                        </h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div><b>🧾 आवेदन संख्या:</b><br>{application_number}</div>
                            <div><b>🌐 फीडर:</b><br>{feeder}</div>
                            <div><b>💡 फीडर कोड:</b><br>{feeder_code}</div>
                            <div><b>🧭 डीटीआर नाम:</b><br>{dtr}</div>
                            <div><b>🔢 डीटीआर MSN:</b><br>{final_msn}</div>
                            <div><b>⏰ बंद समय:</b><br>{off_time}</div>
                            <div><b>⚡ चालू समय:</b><br>{on_time}</div>
                            <div><b>📅 दिनांक:</b><br>{date}</div>
                        </div>
                    </div>
                """.format(
                    application_number=application_number,
                    feeder=feeder,
                    feeder_code=feeder_code,
                    dtr=dtr,
                    final_msn=final_msn,
                    off_time=dtr_off_time,
                    on_time=dtr_on_time,
                    date=date.strftime("%d-%m-%Y")
                ), unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("""
                    <div style='
                        background: #fff3cd;
                        border: 2px solid #ffc107;
                        border-radius: 10px;
                        padding: 15px;
                        text-align: center;
                        margin: 15px 0;
                    '>
                        <h4 style='color: #856404; margin: 0;'>
                            📸 स्क्रीनशॉट सुरक्षित रखें | Save Screenshot
                        </h4>
                        <p style='color: #856404; margin: 5px 0 0 0;'>
                            उपरोक्त जानकारी का स्क्रीनशॉट अपने रिकॉर्ड के लिए सुरक्षित रखें
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ सबमिट करने में त्रुटि | Submission Error: {str(e)}")

# ----------------- FOOTER -----------------
st.markdown("""
    <div class='footer'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
            <div style='text-align: left;'>
                <h4 style='color: #ffd700; margin: 0;'>MPEZ - DTR Indexation</h4>
                <p style='margin: 5px 0; color: #bdc3c7;'>Smart Meter Implementation</p>
            </div>
            <div style='text-align: center;'>
                <p style='margin: 0; font-weight: bold;'>Developed by Esyasoft Team</p>
                <p style='margin: 5px 0; color: #bdc3c7;'>© 2025 All Rights Reserved</p>
            </div>
            <div style='text-align: right;'>
                <p style='margin: 0; color: #3498db; font-weight: bold;'>DTR Indexation Portal</p>
                <p style='margin: 5px 0; color: #bdc3c7;'>Version 2.0</p>
            </div>
        </div>
        <hr style='border-color: #7f8c8d; margin: 15px 0;'>
        <p style='color: #95a5a6; font-size: 14px; margin: 0;'>
            🔒 Secure & Reliable Data Collection System
        </p>
    </div>
""", unsafe_allow_html=True)

# ----------------- PARTNER LOGO -----------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("download (1).png", width=120, caption="Technology Partner: Esyasoft Technologies")
