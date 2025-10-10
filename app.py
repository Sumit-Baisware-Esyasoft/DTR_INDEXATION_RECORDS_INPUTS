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
        }
        
        /* Card styling */
        .custom-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 2px solid #e0e0e0;
        }
        
        .success-card {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 2px solid #28a745;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
        }
        
        /* Dropdown styling - FIXED */
        .stSelectbox > div > div {
            background-color: #f8f9fa !important;
            border: 2px solid #004aad !important;
            border-radius: 10px !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #004aad 0%, #002966 100%) !important;
            color: white !important;
            border: none !important;
            padding: 12px 30px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 18px !important;
            width: 100% !important;
        }
        
        /* Text input styling */
        .stTextInput > div > div > input {
            border: 2px solid #004aad !important;
            border-radius: 10px !important;
            padding: 12px !important;
        }
        
        /* Date input styling */
        .stDateInput > div > div > input {
            border: 2px solid #004aad !important;
            border-radius: 10px !important;
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
            border: none !important;
        }
        
        .streamlit-expanderContent {
            background: #f8f9fa !important;
            border-radius: 0 0 10px 10px !important;
            padding: 20px !important;
        }
        
        /* Footer styling */
        .footer {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-top: 30px;
        }
        
        /* Remove default Streamlit styling */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Fix column spacing */
        .stColumn {
            padding: 10px;
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
        '>
            कृपया नीचे दी गई जानकारी ध्यानपूर्वक भरें | Please fill the below information carefully
        </p>
    </div>
""", unsafe_allow_html=True)

# ----------------- GOOGLE SHEET CONNECTION -----------------
@st.cache_resource
def get_google_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    return client.open("DTR_Indexation_Records").sheet1

try:
    sheet = get_google_sheet()
except Exception as e:
    st.error(f"Google Sheets connection failed: {e}")
    sheet = None

# ----------------- LOAD HIERARCHY -----------------
@st.cache_data
def load_hierarchy_data():
    try:
        hierarchy_path = r"DTR Master Information 2025-09-22 07-00_21992_batch1.xlsx"
        return pd.read_excel(hierarchy_path)
    except Exception as e:
        st.error(f"Error loading master file: {e}")
        return None

hierarchy_df = load_hierarchy_data()

# ----------------- SYSTEM INFORMATION SECTION -----------------
st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
st.markdown("### 🗂️ सिस्टम जानकारी | System Information")

if hierarchy_df is not None:
    with st.expander("🔽 विवरण चुनें | Select Details", expanded=True):
        # Initialize session state for dropdowns
        if 'region' not in st.session_state:
            st.session_state.region = None
        if 'circle' not in st.session_state:
            st.session_state.circle = None
        if 'division' not in st.session_state:
            st.session_state.division = None
        if 'substation' not in st.session_state:
            st.session_state.substation = None
        if 'feeder' not in st.session_state:
            st.session_state.feeder = None
        if 'dtr' not in st.session_state:
            st.session_state.dtr = None

        col1, col2 = st.columns(2)
        
        with col1:
            region = st.selectbox(
                "🌍 क्षेत्र (Region)", 
                options=hierarchy_df["Region"].unique(),
                index=0
            )
            
            if region:
                circle_options = hierarchy_df[hierarchy_df["Region"] == region]["Circle"].unique()
                circle = st.selectbox(
                    "🏛️ सर्कल (Circle)", 
                    options=circle_options,
                    index=0
                )
                
                if circle:
                    division_options = hierarchy_df[hierarchy_df["Circle"] == circle]["Division"].unique()
                    division = st.selectbox(
                        "🏢 डिवीजन (Division)", 
                        options=division_options,
                        index=0
                    )
                    
                    if division:
                        substation_options = hierarchy_df[hierarchy_df["Division"] == division]["Sub station"].unique()
                        substation = st.selectbox(
                            "⚙️ उपकेंद्र (Substation)", 
                            options=substation_options,
                            index=0
                        )
        
        with col2:
            if 'substation' in locals() and substation:
                feeder_options = hierarchy_df[hierarchy_df["Sub station"] == substation]["Feeder"].unique()
                feeder = st.selectbox(
                    "🔌 फीडर (Feeder)", 
                    options=feeder_options,
                    index=0
                )
                
                if feeder:
                    dtr_options = hierarchy_df[hierarchy_df["Feeder"] == feeder]["Dtr"].unique()
                    dtr = st.selectbox(
                        "🧭 डीटीआर का नाम (DTR Name)", 
                        options=dtr_options,
                        index=0
                    )
                    
                    if dtr:
                        feeder_code_options = hierarchy_df[hierarchy_df["Dtr"] == dtr]["Feeder code"].unique()
                        feeder_code = st.selectbox(
                            "💡 फीडर कोड (Feeder Code)", 
                            options=feeder_code_options,
                            index=0
                        )
                        
                        dtr_code_options = hierarchy_df[hierarchy_df["Dtr"] == dtr]["Dtr code"].unique()
                        dtr_code = st.selectbox(
                            "📟 डीटीआर कोड (DTR Code)", 
                            options=dtr_code_options,
                            index=0
                        )
else:
    st.error("❌ मास्टर डेटा लोड नहीं हो सका | Master data could not be loaded")

st.markdown("</div>", unsafe_allow_html=True)

# ----------------- MSN CONFIRMATION SECTION -----------------
if hierarchy_df is not None and 'dtr_code' in locals() and dtr_code:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    
    try:
        msn_options = hierarchy_df[hierarchy_df["Dtr code"] == dtr_code]["Msn"].unique()
        if len(msn_options) > 0:
            msn_auto = st.selectbox(
                "🔢 डीटीआर मीटर सीरियल नंबर (DTR Meter Serial Number)", 
                options=msn_options,
                index=0
            )
            
            st.markdown("### ✅ डीटीआर मीटर सीरियल नंबर की पुष्टि करें | Confirm DTR Meter Serial Number")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.info(f"**🔍 MDM में दर्ज डीटीआर मीटर सीरियल नंबर:** {msn_auto}")
            
            with col2:
                confirm = st.radio(
                    "क्या यह सही है? | Is this correct?", 
                    options=["हाँ, सही है ✅", "नहीं, बदलना है ❌"], 
                    horizontal=True,
                    index=0
                )

            if confirm == "हाँ, सही है ✅":
                final_msn = msn_auto
                st.success("✅ मीटर सीरियल नंबर स्वीकृत | Meter Serial Number Approved")
            else:
                new_msn = st.text_input(
                    "✏️ नया डीटीआर मीटर सीरियल नंबर दर्ज करें | Enter New DTR Meter Serial Number",
                    placeholder="नया सीरियल नंबर दर्ज करें | Enter new serial number"
                )
                if new_msn:
                    final_msn = new_msn
                    st.success("✅ नया मीटर सीरियल नंबर स्वीकृत | New Meter Serial Number Approved")
                else:
                    final_msn = None
        else:
            st.warning("⚠️ इस DTR कोड के लिए कोई MSN उपलब्ध नहीं है | No MSN available for this DTR code")
            final_msn = st.text_input(
                "✏️ कृपया डीटीआर मीटर सीरियल नंबर दर्ज करें | Please enter DTR Meter Serial Number",
                placeholder="सीरियल नंबर दर्ज करें | Enter serial number"
            )
    
    except Exception as e:
        st.error(f"⚠️ MSN लोड करने में त्रुटि | Error loading MSN: {e}")
        final_msn = st.text_input(
            "✏️ कृपया डीटीआर मीटर सीरियल नंबर दर्ज करें | Please enter DTR Meter Serial Number",
            placeholder="सीरियल नंबर दर्ज करें | Enter serial number"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- SIMPLE TIME PICKER FUNCTION -----------------
def simple_time_picker(label, key_prefix):
    st.markdown(f"**{label}**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hour = st.selectbox(
            "घंटा | Hour", 
            options=[f"{i:02d}" for i in range(1, 13)],
            key=f"{key_prefix}_hour"
        )
    
    with col2:
        minute = st.selectbox(
            "मिनट | Minute", 
            options=[f"{i:02d}" for i in range(0, 60)],
            key=f"{key_prefix}_minute"
        )
    
    with col3:
        am_pm = st.selectbox(
            "AM/PM", 
            options=["AM", "PM"],
            key=f"{key_prefix}_ampm"
        )
    
    return f"{hour}:{minute} {am_pm}"

# ----------------- DATE & TIME SECTION -----------------
if 'final_msn' in locals() and final_msn:
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### ⏱️ डीटीआर संचालन समय | DTR Operation Timing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📅 दिनांक | Date")
        date = st.date_input(
            "तारीख चुनें | Select Date", 
            value=datetime.today(),
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("#### 🕒 समय | Time")
        dtr_off_time = simple_time_picker("बंद करने का समय | Shutdown Time", "off")
        dtr_on_time = simple_time_picker("चालू करने का समय | Startup Time", "on")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- OFFICER INFORMATION -----------------
    st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
    st.markdown("### 👤 अधिकारी जानकारी | Officer Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ae_je_name = st.text_input(
            "👨‍💼 AE/JE का नाम | AE/JE Name", 
            placeholder="अधिकारी का पूरा नाम दर्ज करें | Enter officer's full name"
        )
    
    with col2:
        mobile_number = st.text_input(
            "📱 मोबाइल नंबर | Mobile Number", 
            max_chars=10,
            placeholder="10 अंकों का नंबर दर्ज करें | Enter 10-digit number"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------- SUBMIT BUTTON -----------------
    st.markdown("<br>", unsafe_allow_html=True)
    
    submit_clicked = st.button("🚀 डेटा सबमिट करें | Submit Data", use_container_width=True, type="primary")
    
    if submit_clicked:
        # Validation
        errors = []
        
        if not ae_je_name:
            errors.append("❌ कृपया अधिकारी का नाम दर्ज करें | Please enter officer name")
        
        if not mobile_number:
            errors.append("❌ कृपया मोबाइल नंबर दर्ज करें | Please enter mobile number")
        elif len(mobile_number) != 10 or not mobile_number.isdigit():
            errors.append("❌ कृपया वैध 10-अंकीय मोबाइल नंबर दर्ज करें | Please enter valid 10-digit mobile number")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                # Generate application number
                application_number = f"{datetime.now().strftime('%d%m%Y')}{len(sheet.get_all_values()) + 1:04d}"
                
                # Prepare data for submission
                new_data = [
                    region if 'region' in locals() else "",
                    circle if 'circle' in locals() else "",
                    division if 'division' in locals() else "",
                    substation if 'substation' in locals() else "",
                    feeder if 'feeder' in locals() else "",
                    dtr if 'dtr' in locals() else "",
                    dtr_code if 'dtr_code' in locals() else "",
                    feeder_code if 'feeder_code' in locals() else "",
                    msn_auto if 'msn_auto' in locals() else "",
                    new_msn if 'new_msn' in locals() and new_msn else "",
                    final_msn,
                    dtr_off_time,
                    dtr_on_time,
                    date.strftime("%d-%m-%Y"),
                    ae_je_name,
                    mobile_number,
                    application_number
                ]
                
                # Submit to Google Sheets
                if sheet:
                    sheet.append_row(new_data)
                
                # SUCCESS MESSAGE
                st.balloons()
                st.markdown("<div class='custom-card success-card'>", unsafe_allow_html=True)
                st.markdown("### 🎉 सफलता | Success!")
                st.success("✅ डेटा सफलतापूर्वक सबमिट हो गया! | Data submitted successfully!")
                
                # CONFIRMATION DETAILS
                st.markdown(f"""
                    <div style="
                        border: 2px solid #28a745;
                        border-radius: 12px;
                        padding: 20px;
                        background: linear-gradient(135deg, #f8fff9 0%, #e8f5e8 100%);
                        margin: 15px 0;
                        font-size: 16px;
                        line-height: 1.8;
                    ">
                        <h4 style="color:#28a745; text-align:center; margin-bottom:15px;">
                            📋 सबमिट किया गया विवरण | Submitted Details
                        </h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div><b>🧾 आवेदन संख्या:</b><br>{application_number}</div>
                            <div><b>🌐 फीडर:</b><br>{feeder if 'feeder' in locals() else 'N/A'}</div>
                            <div><b>💡 फीडर कोड:</b><br>{feeder_code if 'feeder_code' in locals() else 'N/A'}</div>
                            <div><b>🧭 डीटीआर नाम:</b><br>{dtr if 'dtr' in locals() else 'N/A'}</div>
                            <div><b>🔢 डीटीआर MSN:</b><br>{final_msn}</div>
                            <div><b>⏰ बंद समय:</b><br>{dtr_off_time}</div>
                            <div><b>⚡ चालू समय:</b><br>{dtr_on_time}</div>
                            <div><b>📅 दिनांक:</b><br>{date.strftime('%d-%m-%Y')}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # SCREENSHOT MESSAGE
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
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;'>
            <div style='text-align: left; flex: 1;'>
                <h4 style='color: #ffd700; margin: 0;'>MPEZ - DTR Indexation</h4>
                <p style='margin: 5px 0; color: #bdc3c7;'>Smart Meter Implementation</p>
            </div>
            <div style='text-align: center; flex: 1;'>
                <p style='margin: 0; font-weight: bold;'>Developed by Esyasoft Team</p>
                <p style='margin: 5px 0; color: #bdc3c7;'>© 2025 All Rights Reserved</p>
            </div>
            <div style='text-align: right; flex: 1;'>
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
try:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("download (1).png", width=120, caption="Technology Partner: Esyasoft Technologies")
except:
    pass
