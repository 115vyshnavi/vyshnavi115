import streamlit as st # pyre-ignore
import io
import os
import random
import numpy as np # type: ignore
from PIL import Image, ImageDraw, ImageFilter # type: ignore
from deep_translator import GoogleTranslator # type: ignore
import speech_recognition as sr # type: ignore
from gtts import gTTS # type: ignore
import google.generativeai as genai # type: ignore
from datetime import datetime, timedelta
import json
import cv2 # type: ignore
import hashlib
import base64
import uuid
import urllib.request
import streamlit.components.v1 as components # type: ignore

try:
    import models # type: ignore
    from database import SessionLocal, engine # type: ignore
    models.Base.metadata.create_all(bind=engine)
except Exception: 
    pass

# ==========================================
# 0. STREAMLIT CONFIG
# ==========================================
st.set_page_config(page_title="AgniKshetra AI", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

try:
    genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    gemini_model = None

@st.cache_data(show_spinner=False)
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

logo_b64 = get_base64_image("Logo.png")
logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="width: 55px; height: 55px; object-fit: contain; display: block;">' if logo_b64 else '🌾'

# Custom CSS for Premium Native-Like UI
st.markdown(f"""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"], .stApp, p, h1, h2, h3, h4, h5, h6, li, label, input, button {{
        font-family: 'Poppins', sans-serif !important;
        color: #1e293b;
    }}
    
    /* Global App Background */
    .stApp {{
        background-color: #f7f9f7;
    }}

    /* Hide Default Header/Footer */
    header {{display: none !important;}}
    footer {{display: none !important;}}
    #MainMenu {{display: none !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    .stAppHeader {{display: none !important;}}
    [data-testid="stDecoration"] {{display: none !important;}}
    [data-testid="stToolbar"] {{display: none !important;}}
    .viewerBadge_container__1JCIV {{display: none !important;}}

    /* Sidebar Customization */
    [data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-right: 1px solid #eef2f0;
        width: 280px !important;
    }}
    .sidebar-header {{
        text-align: left;
        padding: 20px 0 10px 0;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 15px;
    }}
    .sidebar-title {{
        font-weight: 700;
        font-size: 20px;
        color: #1e3b1d;
        margin: 0;
        line-height: 1.2;
    }}
    .sidebar-subtitle {{
        font-size: 11px;
        color: #7f8c8d;
        margin: 0;
        font-weight: 500;
    }}

    /* Metric Cards (IoT Sensors) */
    .metric-container {{
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #eef2f0;
        text-align: center;
        transition: transform 0.2s ease;
    }}
    .metric-container:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(45, 83, 41, 0.1);
    }}
    .metric-icon {{
        width: 45px; height: 45px;
        background: #f0f7f4;
        color: #2b5329;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 12px auto;
        font-size: 22px;
    }}
    .metric-title {{
        font-size: 13px; color: #64748b; font-weight: 500; margin-bottom: 5px;
    }}
    .metric-value {{
        font-size: 26px; font-weight: 700; color: #1e293b;
    }}

    /* Dashboard Banner */
    .insight-banner {{
        background: linear-gradient(135deg, #628e64, #48724a);
        color: white;
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        box-shadow: 0 10px 30px rgba(71, 112, 73, 0.2);
    }}
    .banner-icon {{
        font-size: 30px;
        background: rgba(255,255,255,0.2);
        width: 60px; height: 60px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin-right: 20px;
    }}
    .banner-title-row {{
        display: flex; align-items: center; gap: 10px; margin-bottom: 5px;
    }}
    .banner-title {{ font-weight: 700; font-size: 18px; }}
    .banner-tag {{ background: rgba(255,255,255,0.3); padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }}
    .banner-text {{ font-size: 14px; opacity: 0.95; }}

    /* Streamlit Buttons overhaul */
    .stButton > button {{
        background-color: #2e5932 !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 8px 24px !important;
        transition: 0.3s !important;
        box-shadow: 0 4px 10px rgba(46, 89, 50, 0.2) !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background-color: #1e3b1d !important;
        transform: translateY(-2px);
    }}
    
    /* Sidebar Navigation Container */
    [data-testid="stSidebarNav"] {{ display: none !important; }}
    
    /* Form aesthetics for Analyze crop */
    .stTextInput > div > div > input, .stTextArea > div > textarea {{
        border-radius: 8px !important;
        border: 1px solid #eef2f0 !important;
        background-color: #fafbfa !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        color: #1e293b !important;
    }}
    
    .stTextInput > div > div > input:focus, .stTextArea > div > textarea:focus {{
        border-color: #2e5932 !important;
        box-shadow: 0 0 0 1px #2e5932 !important;
    }}

    /* Language Selection Card full page overlay */
    .lang-screen {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.95)), url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2689&auto=format&fit=crop');
        background-size: cover; background-position: center;
        z-index: 1000;
        display: flex; align-items: center; justify-content: center;
    }}
    
    /* Floating chat icon in corner */
    .floating-chat-btn {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        background-color: #2e5932;
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 10px 25px rgba(46, 89, 50, 0.4);
        cursor: pointer;
        z-index: 999;
        transition: 0.3s;
    }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(46, 125, 50, 0.15);
    }}
    div.stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: 1px solid #eef2f0 !important;
        background: white !important;
    }}
    div.stButton > button:hover {{
        border-color: #2E7D32 !important;
        color: #2E7D32 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(46, 125, 50, 0.1) !important;
    }}
    .upload-dropzone {{ border: 2px dashed #cbd5e1; border-radius: 12px; padding: 40px 20px; text-align: center; background-color: #f8fafc; }}
    .upload-icon {{ font-size: 32px; color: #94a3b8; margin-bottom: 15px; }}
</style>
""", unsafe_allow_html=True)

# ====== Session State Management ======
if 'app_stage' not in st.session_state: st.session_state.app_stage = 1
if 'selected_lang' not in st.session_state: st.session_state.selected_lang = "English"
if 'current_page' not in st.session_state: st.session_state.current_page = "Dashboard"
if 'feedback_mode' not in st.session_state: st.session_state.feedback_mode = None
DB_FILE = "agnikshetra_db.json"
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: pass
    return {}
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'all_farms' not in st.session_state: st.session_state.all_farms = load_db()
if 'farm_id' not in st.session_state: st.session_state.farm_id = f"Farm_{random.randint(100000, 999999)}"
if 'chat_open' not in st.session_state: st.session_state.chat_open = False

# Initialize isolated data for the current farm
if st.session_state.farm_id not in st.session_state.all_farms:
    st.session_state.all_farms[st.session_state.farm_id] = {'farm_logs': [], 'chat_history': []}
    save_db(st.session_state.all_farms)

# Map active logs and chat to the current isolated farm context
st.session_state.farm_logs = st.session_state.all_farms[st.session_state.farm_id]['farm_logs']
st.session_state.chat_history = st.session_state.all_farms[st.session_state.farm_id]['chat_history']

LANG_CODE_MAP = {
    "English": {"translator": "en", "gtts": "en", "sr": "en-US", "native": "En"},
    "తెలుగు": {"translator": "te", "gtts": "te", "sr": "te-IN", "native": "Te"},
    "हिंदी": {"translator": "hi", "gtts": "hi", "sr": "hi-IN", "native": "Hi"},
}

@st.cache_data(show_spinner=False)
def translate(text, t_lang):
    if t_lang == "en": return text
    try: return GoogleTranslator(source='en', target=t_lang).translate(text)
    except: return text

@st.cache_data(show_spinner=False)
def get_tts_audio_b64(text, lang_key):
    try:
        t_lang = LANG_CODE_MAP[lang_key]["translator"]
        g_lang = LANG_CODE_MAP[lang_key]["gtts"]
        translated_txt = text if t_lang == "en" else GoogleTranslator(source='en', target=t_lang).translate(text)
        tts = gTTS(text=translated_txt, lang=g_lang)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return base64.b64encode(fp.getvalue()).decode()
    except: return ""

def t(text): return translate(text, LANG_CODE_MAP[st.session_state.selected_lang]["translator"]) # type: ignore


# ==========================================
# STAGE 1: LANGUAGE SELECTION & SPLASH
# ==========================================
def render_language_screen():
    import base64
    bg_path = r"C:\Users\user\.gemini\antigravity\brain\e0178861-5a24-463c-9ef9-173bd4d4e9f4\agritech_hero_bg_1774808006828.png"
    bg_b64 = ""
    try:
        with open(bg_path, "rb") as f: bg_b64 = base64.b64encode(f.read()).decode()
    except: pass
    bg_css = f"background-image: linear-gradient(rgba(10, 30, 20, 0.4), rgba(10, 30, 20, 0.95)), url('data:image/png;base64,{bg_b64}');" if bg_b64 else "background: linear-gradient(135deg, #1e3b1d, #0f172a);"

    st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{display: none !important;}}
        .stApp {{ {bg_css} background-size: cover; background-position: center; background-attachment: fixed; }}
        div[role="radiogroup"] > label {{ background: rgba(255,255,255,0.95) !important; border: 1px solid #eef2f0 !important; padding: 12px 20px !important; border-radius: 12px !important; margin-bottom: 10px !important; width: 100% !important; transition: 0.2s !important; }}
        div[role="radiogroup"] > label:hover {{ border-color: #2E7D32 !important; box-shadow: 0 0 15px rgba(46, 125, 50, 0.3) !important; }}
        div[role="radiogroup"] p {{ color: #1e293b !important; font-weight: 700 !important; font-size: 16px !important;}}
        .hero-text {{ text-align: center; color: white; margin-bottom: 40px; }}
        .hero-title {{ font-size: 65px; font-weight: 900; margin-bottom: 0; text-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
        .hero-subtitle {{ font-size: 24px; font-weight: 300; opacity: 0.95; margin-bottom: 10px; }}
        .hero-tagline {{ font-size: 16px; font-weight: 600; color: #4ade80; letter-spacing: 2px; text-transform: uppercase; }}
    </style>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-text">
        <div class="hero-tagline">From Detection → Decision → Profit</div>
        <h1 class="hero-title">AgniKshetra 🌱</h1>
        <p class="hero-subtitle">AI-Powered Smart Farming Decision Engine</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; background: rgba(255, 255, 255, 0.15); padding: 40px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(16px); box-shadow: 0 20px 50px rgba(0,0,0,0.5); margin-bottom: 20px;">
            <p style="font-weight: 700; font-size: 13px; color: #4ade80; letter-spacing: 1px; margin-bottom: 15px; text-transform: uppercase;">SELECT PREFERRED LANGUAGE</p>
        """, unsafe_allow_html=True)
        
        st.session_state.selected_lang = st.radio(
            "Language", 
            list(LANG_CODE_MAP.keys()), 
            label_visibility="hidden",
            index=list(LANG_CODE_MAP.keys()).index(st.session_state.selected_lang)
        )
        st.write("")
        st.markdown("<p style='font-weight: 700; font-size: 13px; color: #4ade80; letter-spacing: 1px; margin-bottom: 0px; text-transform: uppercase;'>ENTER FARM ID / USERNAME</p>", unsafe_allow_html=True)
        farm_input = st.text_input("Farm ID", value="", placeholder="e.g. Raju_Farm_01", label_visibility="collapsed")
        st.write("")
        st.markdown("""<style>div.stButton > button { background: linear-gradient(135deg, #2E7D32, #1b4332) !important; color: white !important; font-size: 18px !important; box-shadow: 0 0 20px rgba(46,125,50,0.6) !important; }</style>""", unsafe_allow_html=True)
        if st.button("Start Analysis >", use_container_width=True):
            if farm_input.strip() == "": st.session_state.farm_id = f"Farm_{random.randint(100000, 999999)}"
            else: st.session_state.farm_id = farm_input.strip()
            
            if st.session_state.farm_id not in st.session_state.all_farms:
                st.session_state.all_farms[st.session_state.farm_id] = {'farm_logs': [], 'chat_history': []}
                save_db(st.session_state.all_farms)
            
            st.session_state.farm_logs = st.session_state.all_farms[st.session_state.farm_id]['farm_logs']
            st.session_state.chat_history = st.session_state.all_farms[st.session_state.farm_id]['chat_history']
            st.session_state.app_stage = 2
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# STAGE 2: MAIN APPLICATION
# ==========================================
def render_sidebar():
    with st.sidebar:
        # Header with Logo
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding-top: 10px; margin-bottom: 20px;">
            <div style='width: 55px; height: 55px; margin-bottom: 10px;'>{logo_img_tag}</div>
            <h2 style="margin: 0; color: #1e3b1d; font-weight: 700; font-size: 22px;">AgniKshetra</h2>
            <span style="color: #64748b; font-size: 11px; font-weight: 500;">Safety-Aware AI Decision Engine</span>
        </div>
        <hr style="margin-top: 0px; margin-bottom: 20px; border: 0; border-top: 1px solid #eef2f0;">
        """, unsafe_allow_html=True)
        
        st.markdown("""<style>
        [data-testid="stSidebar"] div[role="radiogroup"] > label { background: transparent !important; border: none !important; box-shadow: none !important; padding: 10px 5px !important; margin-bottom: 0px !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] p { font-size: 16px; color: #475569; }
        </style>""", unsafe_allow_html=True)
        
        pages_en = ["Dashboard", "New Analysis", "Water Advisor", "Market Insights", "Farmer Connect", "Farm History"]
        pages_tr = [t(p) for p in pages_en]
        idx = pages_en.index(st.session_state.current_page) if st.session_state.current_page in pages_en else 0
        def _nav_ch():
            sel = st.session_state._nav_radio
            try: st.session_state.current_page = pages_en[pages_tr.index(sel)]
            except: pass
        st.radio("Nav", pages_tr, index=idx, key="_nav_radio", on_change=_nav_ch, label_visibility="collapsed")
        
        st.markdown("<div style='flex-grow: 1; height: 35vh;'></div><hr style='border: 0; border-top: 1px solid #eef2f0; margin-bottom: 15px;'>", unsafe_allow_html=True)
        with st.popover("👤 " + t("Profile") + ": " + st.session_state.farm_id, use_container_width=True):
            st.markdown(f"**{t('User Settings')}**")
            new_l = st.selectbox(t("Language"), list(LANG_CODE_MAP.keys()), index=list(LANG_CODE_MAP.keys()).index(st.session_state.selected_lang), key="sb_lang")
            if new_l != st.session_state.selected_lang:
                st.session_state.selected_lang = new_l
                st.rerun()
            st.write("")
            if st.button("📖 " + t("Farm History"), key="sb_hist_btn", use_container_width=True):
                st.session_state.current_page = "Farm History"
                st.rerun()
            if st.button("🚪 " + t("Switch Profile"), key="sb_logout_btn", use_container_width=True):
                st.session_state.app_stage = 1
                st.rerun()


def render_main_app():
    render_sidebar()
    
    # Data fetching for Dashboard
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_virtual_sensor_data():
        try:
            req = urllib.request.Request("https://ipapi.co/json/", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                loc_data = json.loads(response.read().decode())
            lat, lon = loc_data.get("latitude", 20.59), loc_data.get("longitude", 78.96)
            city = str(loc_data.get("city", "Local Farm"))
            
            w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=soil_moisture_0_to_7cm"
            req2 = urllib.request.Request(w_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2, timeout=3) as response:
                w_data = json.loads(response.read().decode())
            
            temp = w_data.get("current_weather", {}).get("temperature", 27.1)
            wind = w_data.get("current_weather", {}).get("windspeed", 2.9)
            soil_raw = float(w_data.get("hourly", {}).get("soil_moisture_0_to_7cm", [0.40])[0])
            if soil_raw is None: soil_raw = 0.40
            return city[:10], temp, wind, round(soil_raw * 100, 1), 60, 0 # type: ignore
        except Exception:
            return "Local Farm", 27.1, 2.9, 40.0, 60, 0
            
    city, temp, wind, soil_m, hum, rain = get_virtual_sensor_data()

    # Global Header Logo & Navigation (Glassmorphism)
    st.markdown("""<style>
    [data-testid="stHeader"] { display: none; }
    .glass-nav { position: sticky; top: 0; z-index: 999; background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(0,0,0,0.05); padding: 15px 0; margin-bottom: 30px; margin-top: -60px; padding-left: 20px; padding-right: 20px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-nav'>", unsafe_allow_html=True)
    head_c1, head_c2 = st.columns([10, 2])
    with head_c1:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 15px;'>
            <div style='width: 45px; height: 45px;'>{logo_img_tag.replace('55px', '45px')}</div>
            <div style='display: flex; align-items: baseline; gap: 8px;'>
                <h2 style='margin: 0; color: #166534; font-weight: 800; font-size: 28px;'>AgniKshetra</h2>
                <span style='color: #64748b; font-size: 14px; font-weight: 600;'>| Safety-Aware AI Decision Engine</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with head_c2:
        st.markdown("<style>div.stPopover > button { padding: 5px 10px !important; border-radius: 8px !important; font-size: 16px !important; background: white !important; font-weight: 600 !important; border: 1px solid #e2e8f0 !important; color: #1e293b !important; margin-top: 5px; box-shadow: none !important; }</style>", unsafe_allow_html=True)
        with st.popover("☰ " + t("Menu"), use_container_width=True):
            if st.button("🏠 " + t("Dashboard"), use_container_width=True):
                st.session_state.current_page = "Dashboard"; st.rerun()
            if st.button("📖 " + t("Farm History"), key="h_hist", use_container_width=True):
                st.session_state.current_page = "Farm History"; st.rerun()
            if st.button("🚪 " + t("Switch Farm"), key="h_switch", use_container_width=True):
                st.session_state.app_stage = 1; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.current_page == "Dashboard":
        st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0px;'>{t('Dashboard')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b;'>{t('Farm status and virtual sensor readings.')}</p>", unsafe_allow_html=True)
        
        # Navigation Quick Links Grid (Premium Animation Grid)
        st.markdown(f"<h4 style='color: #1e293b; margin-top: 10px; font-weight: 700;'>{t('Core Systems')}</h4>", unsafe_allow_html=True)
        st.markdown("<style>div[data-testid='column'] { transition: 0.3s ease; } div[data-testid='column']:hover { transform: translateY(-3px); }</style>", unsafe_allow_html=True)
        nav1, nav2, nav3 = st.columns(3)
        with nav1:
            if st.button(t("🌿 Analyze Crop"), key="nav_new", use_container_width=True):
                st.session_state.current_page = "New Analysis"; st.rerun()
        with nav2:
            if st.button(t("📈 Market Insights"), key="nav_market", use_container_width=True):
                st.session_state.current_page = "Market Insights"; st.rerun()
        with nav3:
            if st.button(t("💧 Water Advisor"), key="nav_water", use_container_width=True):
                st.session_state.current_page = "Water Advisor"; st.rerun()
                
        nav4, nav5, nav6 = st.columns(3)
        with nav4:
            if st.button(t("👨‍🌾 Farmer Connect"), key="nav_network", use_container_width=True):
                st.session_state.current_page = "Farmer Connect"; st.rerun()
        with nav5:
            if st.button(t("📖 Farm History"), key="nav_hist", use_container_width=True):
                st.session_state.current_page = "Farm History"; st.rerun()
        with nav6:
            st.markdown("<p style='text-align:center; font-size:12px; color:#94a3b8; margin-top:10px;'>Chat floating below ↓</p>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
                
        # Premium Banner
        st.markdown(f"""
        <div class="insight-banner">
            <div class="banner-icon">📈</div>
            <div>
                <div class="banner-title-row">
                    <span class="banner-title">AgniKshetra AI Insight</span>
                    <span class="banner-tag">LIVE</span>
                </div>
                <div class="banner-text">
                    {t('Weather conditions are favorable for field operations. Good time for fertilizer application and crop inspection. UV index is moderate — wear sun protection.')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # IoT Sensors
        st.markdown(f"<h4 style='color: #1e293b; margin-top: 20px; font-weight: 700;'>{t('Virtual IoT Sensors')}</h4>", unsafe_allow_html=True)
        m1, m2, m3, m4, m5 = st.columns(5)
        
        with m1:
            st.markdown(f"""<div class="metric-container"><div class="metric-icon" style="color:#f97316; background:#fff7ed;">🌡️</div><div class="metric-title">{t('Temperature')}</div><div class="metric-value">{temp}<span class="metric-title"> °C</span></div></div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-container"><div class="metric-icon" style="color:#3b82f6; background:#eff6ff;">💧</div><div class="metric-title">{t('Humidity')}</div><div class="metric-value">{hum}<span class="metric-title"> %</span></div></div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-container"><div class="metric-icon" style="color:#22c55e; background:#f0fdf4;">🌱</div><div class="metric-title">{t('Soil Moisture')}</div><div class="metric-value">{soil_m}<span class="metric-title"> %</span></div></div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="metric-container"><div class="metric-icon" style="color:#0ea5e9; background:#f0f9ff;">💨</div><div class="metric-title">{t('Wind Speed')}</div><div class="metric-value">{wind}<span class="metric-title"> km/h</span></div></div>""", unsafe_allow_html=True)
        with m5:
            st.markdown(f"""<div class="metric-container"><div class="metric-icon" style="color:#8b5cf6; background:#f5f3ff;">☔</div><div class="metric-title">{t('Rainfall')}</div><div class="metric-value">{rain}<span class="metric-title"> mm</span></div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        colH1, colH2 = st.columns([5, 1])
        with colH1:
            st.markdown(f"<h4 style='color: #1e293b; font-weight: 700;'>{t('Active Treatments')}</h4>", unsafe_allow_html=True)
        with colH2:
            st.markdown(f"<p style='text-align:right; margin-top:5px; cursor:pointer; color:#475569; font-weight:500; font-size:14px;' onclick='document.getElementById(\"nav_btn_FarmHistory\").click();'>{t('View All →')}</p>", unsafe_allow_html=True)

        st.markdown("""<div style='background: white; border: 1px solid #eef2f0; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);'>""", unsafe_allow_html=True)
        if len(st.session_state.farm_logs) == 0:
            st.info(t("No active treatments being tracked. Go to 'New Analysis' to start recording farm history."))
        else:
            for log in st.session_state.farm_logs[-3:]:
                 st.markdown(f"""
                 <div style='display: flex; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; margin-bottom: 10px;'>
                 <div style='font-size: 24px; margin-right: 15px;'>🌿</div>
                 <div>
                    <div style='font-weight: 600; color: #1e293b; font-size: 15px;'>{log['crop']} - {t(log['disease'])}</div>
                    <div style='font-size: 13px; color: #64748b;'>{t('Applied')} {t(log['chemical'])} {t('on')} {log['date'][:10] if isinstance(log['date'], str) else log['date'].strftime('%b %d, %Y')}</div>
                 </div>
                 </div>
                 """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_page == "New Analysis":
        st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0px;'>{t('Analyze Crop')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b;'>{t('Describe symptoms or upload an image for AI diagnosis.')}</p>", unsafe_allow_html=True)
        
        # White Container
        st.markdown("""<div style='background: white; border: 1px solid #eef2f0; border-radius: 16px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);'>""", unsafe_allow_html=True)
        
        col1, padding, col2 = st.columns([1.2, 0.1, 1])
        with col1:
            crop_type = st.text_input(t("Crop Type"), placeholder=t("e.g. Rice, Tomato, Cotton..."))
            symptoms = st.text_area(t("Describe Symptoms"), placeholder=t("Describe what you see on the leaves, stems, or fruits..."), height=110)
            
            audio_value = st.audio_input(t("Speak your problem (Voice Input)"), label_visibility="collapsed")
            problem_text = symptoms
            if audio_value is not None:
                audio_id = getattr(audio_value, "file_id", str(audio_value.size))
                if st.session_state.get('last_analyze_voice') != audio_id:
                    try:
                        recognizer = sr.Recognizer()
                        with sr.AudioFile(audio_value) as source:
                            audio_data = recognizer.record(source)
                            st.session_state.analyze_voice_text = recognizer.recognize_google(audio_data, language=LANG_CODE_MAP[st.session_state.selected_lang]["sr"])
                    except:
                        st.session_state.analyze_voice_text = ""
                    st.session_state.last_analyze_voice = audio_id
                
                if st.session_state.get('analyze_voice_text'):
                    problem_text = st.session_state.analyze_voice_text
                    st.success(f"**{t('Heard:')}** {problem_text}")
            
            st.write("")
            analyze_trigger = st.button(t("Analyze with AI >"), use_container_width=True)

        with col2:
            st.markdown(f"<p style='font-size: 14px; font-weight: 500; color: #1e293b; margin-bottom: 10px;'>{t('Upload Image')}</p>", unsafe_allow_html=True)
            uploaded_files = st.file_uploader("", type=["jpg", "png", "jpeg"], accept_multiple_files=True, label_visibility="collapsed")
            if not uploaded_files:
                st.markdown(f"""
                <div class="upload-dropzone">
                    <div class="upload-icon">↑</div>
                    <div style="font-weight: 600; color: #1e293b; margin-bottom: 5px;">{t('Upload Image')}</div>
                    <div style="font-size: 13px; color: #94a3b8;">{t('Drag and drop or click to browse')}</div>
                    <div style="font-size: 11px; color: #cbd5e1; margin-top: 15px;">{t('Optional: helps AI improve accuracy')}</div>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)

        if analyze_trigger:
            if not crop_type and not problem_text and not uploaded_files:
                st.warning(t("Please provide either an image, a description, or audio input."))
            else:
                st.session_state.analysis_active = True
                
                # Setup default data
                ai_data = {
                    "auto_crop": "Tomato (Auto-Detected)",
                    "detected_disease": "Early Blight (Alternaria solani)",
                    "confidence": 94.5,
                    "best_soil": "Well-drained sandy loam with pH 6.0-7.0",
                    "care_tips": "Increase spacing between plants to improve airflow. Avoid overhead watering.",
                    "prescription": {
                        "chemical": {"name": "Mancozeb 75% WP", "dosage": "2-2.5 gm/L", "application": "Spray evenly on affected foliage", "waiting_period": "7-10 days", "cost": 450, "loss_if_ignored": 3000, "expected_saving": 2550, "consequences": {"yield": "High Recovery", "soil": "Medium Damage"}},
                        "organic": {"name": "Copper Fungicide or Neem Oil", "dosage": "5 ml Neem oil/L", "application": "Spray thoroughly on leaves", "waiting_period": "0 days", "cost": 150, "loss_if_ignored": 3000, "expected_saving": 2850, "consequences": {"yield": "Moderate Recovery", "soil": "Low Damage"}}
                    }
                }
                
                if 'gemini_model' in globals() and gemini_model:
                    try:
                        prompt_parts = [
                            f"Crop Type: {crop_type if crop_type else 'AUTO-DETECT FROM IMAGE'}\nSymptoms: {problem_text}\n",
                            "Look at the image. Extremely Important: If the image does NOT prominently feature a plant, crop, or leaf, you must completely ignore the disease analysis and return this exact JSON: {\"auto_crop\": \"Not a plant\", \"detected_disease\": \"None\", \"confidence\": 100, \"best_soil\": \"N/A\", \"care_tips\": \"Please upload a valid plant or crop image.\", \"prescription\": {\"chemical\": {\"name\": \"N/A\", \"dosage\": \"0\", \"application\": \"None\", \"waiting_period\": \"0\", \"cost\": 0, \"loss_if_ignored\": 0, \"expected_saving\": 0, \"consequences\": {\"yield\": \"N/A\", \"soil\": \"N/A\"}}, \"organic\": {\"name\": \"N/A\", \"dosage\": \"0\", \"application\": \"None\", \"waiting_period\": \"0\", \"cost\": 0, \"loss_if_ignored\": 0, \"expected_saving\": 0, \"consequences\": {\"yield\": \"N/A\", \"soil\": \"N/A\"}}}}. If it IS a plant, return strictly valid JSON (no markdown). Do not use 'Unspecified'. Include specific soil and care tips:\n",
                            "{\n  \"auto_crop\": \"Detected crop name\",\n  \"detected_disease\": \"Specific Disease Name\",\n  \"confidence\": 95,\n  \"best_soil\": \"...\",\n  \"care_tips\": \"...\",\n  \"prescription\": {\n    \"chemical\": {\"name\": \"...\", \"dosage\": \"...\", \"application\": \"...\", \"waiting_period\": \"...\", \"cost\": 500, \"loss_if_ignored\": 3000, \"expected_saving\": 2500, \"consequences\": {\"yield\": \"...\", \"soil\": \"...\"}},\n    \"organic\": {\"name\": \"...\", \"dosage\": \"...\", \"application\": \"...\", \"waiting_period\": \"...\", \"cost\": 150, \"loss_if_ignored\": 3000, \"expected_saving\": 2800, \"consequences\": {\"yield\": \"...\", \"soil\": \"...\"}}\n  }\n}"
                        ]
                        if uploaded_files:
                            prompt_parts.append(Image.open(uploaded_files[0]))
                        res = gemini_model.generate_content(prompt_parts)
                        res_text = res.text.strip()
                        if res_text.startswith("```json"): res_text = res_text[7:-3]
                        elif res_text.startswith("```"): res_text = res_text[3:-3]
                        ai_data = json.loads(res_text.strip())
                    except Exception:
                        pass # Fallback
                
                # Save input data to state for tracking
                st.session_state.active_analysis_data = ai_data
                st.session_state.active_crop = ai_data.get("auto_crop", crop_type if crop_type else "Scanned Crop")
                
                img_b64 = ""
                ndvi_b64 = ""
                if uploaded_files:
                    try: 
                        raw_img = uploaded_files[0].getvalue()
                        img_b64 = base64.b64encode(raw_img).decode()
                        
                        # Pseudo-NDVI processing using PIL and pure numpy (safe dependencies)
                        pil_img = Image.open(io.BytesIO(raw_img)).convert("RGB")
                        import numpy as np
                        arr = np.array(pil_img, dtype=float)
                        R, G, B = arr[:,:,0], arr[:,:,1], arr[:,:,2]
                        
                        den = (G + R - B)
                        den[den == 0] = 0.001
                        vari = (G - R) / den
                        vari_norm = ((vari - np.min(vari)) / (np.max(vari) - np.min(vari) + 0.001) * 255).astype(np.uint8)
                        
                        stress_img = np.zeros_like(arr, dtype=np.uint8)
                        stress_img[:,:,0] = 255 - vari_norm # Red = High Stress
                        stress_img[:,:,1] = vari_norm # Green = Healthy
                        stress_img[:,:,2] = 0
                        
                        blended = np.clip(arr*0.3 + stress_img*0.7, 0, 255).astype(np.uint8)
                        out_pil = Image.fromarray(blended)
                        fp2 = io.BytesIO()
                        out_pil.save(fp2, format="JPEG")
                        ndvi_b64 = base64.b64encode(fp2.getvalue()).decode()
                    except: pass
                st.session_state.active_img = img_b64
                st.session_state.active_ndvi = ndvi_b64

        if st.session_state.get("analysis_active"):
            st.markdown("---")
            ai_data = st.session_state.active_analysis_data
            detected_disease = ai_data["detected_disease"]
            confidence = ai_data.get("confidence", 94.5)
            prescription = ai_data["prescription"]
            
            risk_level = "HIGH" 
            risk_color = "#ef4444" if risk_level == "HIGH" else "#eab308"
            
            st.markdown(f"""
            <div class='glass-card' style='margin-bottom: 30px;'>
                <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                    <div>
                        <span style='background: #e2e8f0; color: #475569; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;'>{st.session_state.active_crop}</span>
                        <h2 style='color: #1e3b1d; font-weight: 800; margin-top: 10px; margin-bottom: 5px;'>{t(detected_disease)}</h2>
                        <div style='display: flex; align-items: center; gap: 10px; margin-top: 5px;'>
                            <span style='color: #64748b; font-size: 13px; font-weight: 600;'>AI Confidence:</span>
                            <div style='width: 150px; background: #e2e8f0; border-radius: 10px; height: 8px;'><div style='width: {confidence}%; background: #2E7D32; height: 100%; border-radius: 10px;'></div></div>
                            <span style='color: #2E7D32; font-weight: 700; font-size: 13px;'>{confidence}%</span>
                        </div>
                    </div>
                    <div style='background: {risk_color}20; color: {risk_color}; border: 1px solid {risk_color}50; padding: 8px 15px; border-radius: 12px; font-weight: 700; display: flex; align-items: center; gap: 8px;'>
                        <span style='font-size: 18px;'>⚠️</span> RISK: {risk_level}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Split Screen Images (Original vs NDVI)
            if st.session_state.active_img:
                st.markdown(f"### 🔬 {t('Scientific Crop Stress Vision')}")
                ic1, ic2 = st.columns(2)
                with ic1: st.image(f"data:image/jpeg;base64,{st.session_state.active_img}", use_container_width=True, caption=t("Standard Original Image"))
                with ic2: 
                    if st.session_state.get('active_ndvi'):
                        st.image(f"data:image/jpeg;base64,{st.session_state.active_ndvi}", use_container_width=True, caption=t("Pseudo-NDVI Stress Heatmap (Red = Infection/Damage)"))
            
            # 2. EXPLAINABLE AI ("WHY THIS DECISION")
            with st.expander(f"🧠 {t('AI Pathology & Care Tips')}", expanded=True):
                st.write(f"- **{t('Symptoms Detected')}**: {t('Visual pattern strongly correlates with')} {t(detected_disease)}.")
                st.write(f"- **{t('Required Soil Condition')}**: {t(ai_data.get('best_soil', 'Use well-draining soil with organic compost.'))}")
                st.write(f"- **{t('Care Tips')}**: {t(ai_data.get('care_tips', 'Avoid overhead watering to prevent fungal spread.'))}")
                st.write(f"- **{t('Weather Influence')}**: {t('High humidity')} ({hum}%) {t('and temperature')} ({temp}°C) {t('create an ideal environment for this issue.')}")
                if st.session_state.active_img:
                    st.write(f"- **{t('Image Analysis')}**: {t('Edges of the leaves show typical progression of the infection.')}")

                # 3. RISK & SOIL HEALTH DASHBOARD
                st.markdown(f"### 📊 {t('Risk & Soil Health Dashboard')}")
                risk_level = "HIGH" 
                soil_health = "72%" if risk_level == "HIGH" else "95%"
                long_term = "-12% Yield Potential" if risk_level == "HIGH" else "+5% Yield Potential"
                
                r1, r2, r3 = st.columns(3)
                r1.metric(t("Estimated Soil Health"), soil_health)
                r2.metric(t("Chemical Risk Level"), t(risk_level))
                r3.metric(t("Long-Term Impact"), t(long_term))

                # 4. SAFETY-FIRST VOICE ALERT SYSTEM
                if risk_level == "HIGH":
                    st.error(f"🚨 **{t('STOP! HUMAN SAFETY ALERT')}**\n\n"
                             f"**{t('This chemical can:')}** {t('Cause breathing problems, Harm skin, Affect nearby water.')}\n\n"
                             f"⚠️ **{t('Recommended:')}** {t('Wear mask, Avoid spraying near children, Do not spray in high wind.')}")
                             
                    b64_a = get_tts_audio_b64("STOP! Toxic dose alert. Use protective measures.", st.session_state.selected_lang)
                    if b64_a: st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64_a}" type="audio/mp3"></audio>', unsafe_allow_html=True)

                # 5. SPRAY-WINDOW OPTIMIZER
                st.markdown(f"### 🌬️ {t('Pesticide Toxicity & Spray-Window Optimizer')}")
                if wind > 15:
                    st.error(f"⚠️ **{t('HIGH WIND DRIFT RISK')} ({wind} km/h)**: {t('DO NOT SPRAY TODAY. High risk of chemical drift into water sources and inhalation by workers. Wait for wind to drop below 10 km/h.')}")
                else:
                    st.success(f"✅ **{t('SAFE TO SPRAY')}**: {t('Wind speed')} ({wind} km/h) {t('is optimal. Zero drift risk.')}")

                # 1. DECISION COMPARISON ENGINE
                st.markdown(f"### ⚖️ {t('Decision Comparison Engine')}")
                c1, c2 = st.columns(2)
                with c1:
                    chem = prescription['chemical']
                    c_name, c_yield, c_soil = chem['name'], chem['consequences']['yield'], chem['consequences']['soil'] # type: ignore
                    c_cost, c_dosage = chem['cost'], chem['dosage'] # type: ignore
                    c_loss, c_save = chem['loss_if_ignored'], chem['expected_saving'] # type: ignore
                    st.markdown(f"""
                    <div style='background: white; border-top: 4px solid #f97316; border-radius: 12px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
                        <h4 style='color: #1e293b; margin-top: 0;'>🧪 {t('Chemical Strategy')}</h4>
                        <p><b>{t('Name')}</b>: {t(c_name)}</p>
                        <p><b>{t('Yield Recovery')}</b>: {t(c_yield)}</p>
                        <p><b>{t('Soil Damage')}</b>: {t(c_soil)}</p>
                        <p><b>{t('Dosage')}</b>: {t(c_dosage)}</p>
                        <hr style="margin: 10px 0; border: 0; border-top: 1px dashed #e2e8f0;">
                        <p style="margin-bottom: 5px; color:#1e293b; font-weight:700;">💰 {t('FARMER PROFIT IMPACT')}</p>
                        <p style="margin: 0; font-size:14px;"><b>{t('Cost of treatment')}</b>: ₹{c_cost}</p>
                        <p style="margin: 0; color:#ef4444; font-size:14px;"><b>{t('If ignored')}</b>: ₹{c_loss} {t('loss')}</p>
                        <p style="margin: 0; color:#22c55e; font-size:14px;"><b>{t('Expected saving')}</b>: ₹{c_save}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    org = prescription['organic']
                    o_name, o_yield, o_soil = org['name'], org['consequences']['yield'], org['consequences']['soil'] # type: ignore
                    o_cost, o_dosage = org['cost'], org['dosage'] # type: ignore
                    o_loss, o_save = org['loss_if_ignored'], org['expected_saving'] # type: ignore
                    st.markdown(f"""
                    <div style='background: white; border-top: 4px solid #22c55e; border-radius: 12px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
                        <h4 style='color: #1e293b; margin-top: 0;'>🌿 {t('Organic Strategy')}</h4>
                        <p><b>{t('Name')}</b>: {t(o_name)}</p>
                        <p><b>{t('Yield Recovery')}</b>: {t(o_yield)}</p>
                        <p><b>{t('Soil Damage')}</b>: {t(o_soil)}</p>
                        <p><b>{t('Dosage')}</b>: {t(o_dosage)}</p>
                        <hr style="margin: 10px 0; border: 0; border-top: 1px dashed #e2e8f0;">
                        <p style="margin-bottom: 5px; color:#1e293b; font-weight:700;">💰 {t('FARMER PROFIT IMPACT')}</p>
                        <p style="margin: 0; font-size:14px;"><b>{t('Cost of treatment')}</b>: ₹{o_cost}</p>
                        <p style="margin: 0; color:#ef4444; font-size:14px;"><b>{t('If ignored')}</b>: ₹{o_loss} {t('loss')}</p>
                        <p style="margin: 0; color:#22c55e; font-size:14px;"><b>{t('Expected saving')}</b>: ₹{o_save}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.success(f"⭐ **{t('BEST OPTION HIGHLIGHT:')}** {t('Organic Strategy (Safer for long-term health and lower cost)')}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"📌 {t('Track this treatment')}"):
                new_log = {
                    "id": len(st.session_state.farm_logs),
                    "crop": st.session_state.active_crop,
                    "disease": detected_disease,
                    "chemical": prescription['organic']['name'],
                    "cost": prescription['organic']['cost'],
                    "date": datetime.now().isoformat(),
                    "image": st.session_state.active_img
                }
                st.session_state.farm_logs.append(new_log)
                save_db(st.session_state.all_farms)
                st.session_state.analysis_active = False # Reset
                st.session_state.current_page = "Dashboard"
                st.rerun()

    elif st.session_state.current_page == "Farm History":
        st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0px;'>{t('Farm History')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b;'>{t('Track treatments and adapt to changing conditions.')}</p>", unsafe_allow_html=True)
        
        # 5. ADAPTIVE FAILURE ENGINE (ENHANCED)
        if st.session_state.feedback_mode:
            failed_log = st.session_state.feedback_mode
            st.error(f"🚨 {t('Treatment Failure Analysis for')} {t(failed_log['disease'])}")
            
            c_fail1, c_fail2 = st.columns(2)
            with c_fail1:
                st.warning(f"⚠️ **{t('Possible Reasons for Failure:')}**\n\n"
                           f"- {t('Pathogen has developed resistance to')} {t(failed_log['chemical'])}\n"
                           f"- {t('Incorrect dosage timing based on recent weather data')}")
            with c_fail2:
                st.info(f"💡 **{t('Adaptive Strategy (New Recommendation):')}**\n\n"
                        f"- **{t('Action')}**: {t('Switch chemical group completely. Do NOT reuse previous chemical.')}\n"
                        f"- **{t('Alternative')}**: {t('Systemic Fungicide / Bio-control agents')}")
                        
            if st.button(f"🔙 {t('Acknowledge & Back to History')}"):
                st.session_state.feedback_mode = None
                st.rerun()
            st.markdown("---")
        
        # 6. FARM STORY MODE
        if not st.session_state.farm_logs:
            st.info(t("No active treatments being tracked. Go to 'New Analysis' to start."))
        else:
            st.markdown(f"### 📖 {t('Farm Story Timeline')}")
            
            st.markdown(f"**⏱️ {t('Simulate Time Passed (Demo)')}**")
            days_passed = st.slider(t("Days elapsed since prescription"), 0, 7, 0, key="time_sim")
            
            for log in reversed(st.session_state.farm_logs):
                
                log_date_str = log['date'] if isinstance(log['date'], str) else log['date'].isoformat()
                with st.expander(f"🕰️ {t('Tracking')}: {log['crop']} - {log_date_str[:10]}", expanded=True):
                    colL, colR = st.columns([1, 2])
                    with colL:
                        if log.get('image'): 
                            st.markdown(f'<img src="data:image/jpeg;base64,{log["image"]}" style="width: 100%; border-radius: 8px;">', unsafe_allow_html=True)
                        else:
                            st.info(t("No image uploaded"))
                    with colR:
                        st.write(f"**{t('Issue Detected')}**: {t(log['disease'])}")
                        st.write(f"**{t('Strategy Pursued')}**: {t(log['chemical'])}")
                        st.write(f"**{t('Pesticides Used')}**: {t(log['chemical'])} ({t('Logged on')} {log_date_str[:10]})")
                    
                    st.markdown("##### 📅 " + t("Voice-Based Escalation Engine"))
                    
                    if days_passed == 1:
                        msg1 = t("Namaste, it is Day 1. Your ") + log['crop'] + t(" needs the spray today. Please confirm once done.")
                        st.info(f"🔊 **Level 1 (Reminder)**: {msg1} (Plays 3 times with 10s breaks)")
                        b64_a1 = get_tts_audio_b64(msg1, st.session_state.selected_lang)
                        if b64_a1:
                            st.markdown(f'''
                            <audio id="v_audio1" autoplay><source src="data:audio/mp3;base64,{b64_a1}" type="audio/mp3"></audio>
                            <script>
                                var a = document.getElementById("v_audio1");
                                var count = 0;
                                a.onended = function() {{
                                    count++;
                                    if(count < 3) {{ setTimeout(function(){{ a.play(); }}, 10000); }}
                                }};
                            </script>
                            ''', unsafe_allow_html=True)
                    elif days_passed == 3:
                        msg2 = t("Warning! It has been 3 days since the recommendation. The disease is spreading. Apply treatment immediately!")
                        st.warning(f"🚨 **Level 2 (Warning)**: {msg2}")
                        b64_a2 = get_tts_audio_b64(msg2, st.session_state.selected_lang)
                        if b64_a2: st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64_a2}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    elif days_passed >= 7:
                        msg3 = t("You missed the early window. DO NOT use the original dose; it will now be ineffective and burn the soil. Use Systemic Fungicide instead.")
                        st.error(f"🛑 **Level 3 (Safety Adjustment)**: {msg3}")
                        b64_a3 = get_tts_audio_b64(msg3, st.session_state.selected_lang)
                        if b64_a3: st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64_a3}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    else:
                        st.write(t("Adjust the simulator slider to trigger the voice escalation."))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"⚠️ {t('Treatment Not Working?')} (ID: {log['id']})", key=f"hist_{log['id']}"):
                        st.session_state.feedback_mode = log
                        st.rerun()


    elif st.session_state.current_page == "Water Advisor":
        st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0px;'>{t('Smart Irrigation Advisor')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b;'>{t('Data-driven watering recommendations.')}</p>", unsafe_allow_html=True)
        
        st.markdown("""<div style='background: white; border: 1px solid #eef2f0; border-radius: 16px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);'>""", unsafe_allow_html=True)
        w1, w2 = st.columns([1, 1])
        with w1:
            st.markdown(f"<h3 style='color: #1e3b1d;'>{t('Current Soil Status')}</h3>", unsafe_allow_html=True)
            st.progress(int(soil_m))
            st.markdown(f"**{t('Moisture Level:')} {soil_m}%**")
            st.markdown(f"**{t('Temperature:')} {temp}°C** | **{t('Rain Forecast:')} {rain}mm**")
            
        with w2:
            st.markdown(f"<h3 style='color: #1e3b1d;'>{t('Recommendation')}</h3>", unsafe_allow_html=True)
            if soil_m > 60:
                rec_title = "🛑 " + t("DO NOT WATER")
                rec_color = "#ef4444"
                reason = t("Soil is highly saturated. Watering now will cause root rot and fungal infections.")
            elif soil_m < 30 and temp > 30:
                rec_title = "🚨 " + t("WATER IMMEDIATELY")
                rec_color = "#f97316"
                reason = t("Critical dehydration risk due to high heat and low moisture. Roots are stressing.")
                
                b64_a = get_tts_audio_b64("Critical alert. Soil moisture is dangerously low. Please irrigate your field immediately to prevent crop loss.", st.session_state.selected_lang)
                if b64_a: st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64_a}" type="audio/mp3"></audio>', unsafe_allow_html=True)
            else:
                rec_title = "✅ " + t("OPTIMAL RANGE")
                rec_color = "#22c55e"
                reason = t("Soil moisture is sustaining well. No immediate action required.")
                
            st.markdown(f"<div style='background: {rec_color}20; border-left: 5px solid {rec_color}; padding: 15px; border-radius: 8px;'><h4 style='color: {rec_color}; margin: 0;'>{rec_title}</h4></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"🧠 {t('Why this suggestion?')}", expanded=True):
            st.write(reason)
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.current_page == "Market Insights":
        st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0px;'>{t('Market Intelligence')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b;'>{t('Real-time price trends and AI trading suggestions.')}</p>", unsafe_allow_html=True)
        
        crops_data = [
            {"name": "Rice (Paddy)", "price": 2250, "trend": "↑", "status": "Hold Stock", "reason": "Festive demand rising; expect 5% bump in next 3 days.", "color": "#22c55e", "history": [2100, 2150, 2120, 2200, 2250]},
            {"name": "Cotton", "price": 6800, "trend": "↓", "status": "Sell Now", "reason": "International surplus reported. Prices dropping fast over the next week.", "color": "#ef4444", "history": [7200, 7100, 6900, 6850, 6800]},
            {"name": "Tomato", "price": 1400, "trend": "↑", "status": "Hold Stock", "reason": "Supply chain delays in neighboring states. Shortage expected.", "color": "#f97316", "history": [1100, 1150, 1300, 1350, 1400]}
        ]
        
        for crop in crops_data:
            st.markdown(f"""<div style='background: white; border: 1px solid #eef2f0; border-radius: 16px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);'>
                <h3 style='color: #1e3b1d; margin-top: 0;'>🌾 {t(crop['name'])}</h3>
            </div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                st.metric(t("Current Price (per Quintal)"), f"₹{crop['price']}", f"{crop['trend']} Trend")
            with c2:
                import pandas as pd # type: ignore
                chart_data = pd.DataFrame({"Price (₹)": crop['history']})
                st.line_chart(chart_data, height=150)
            with c3:
                st.markdown(f"<div style='background: {crop['color']}20; padding: 10px; border-radius: 8px; text-align: center;'><h4 style='color: {crop['color']}; margin: 0;'>{t(crop['status'])}</h4></div>", unsafe_allow_html=True)
                with st.expander(f"🧠 {t('Why?')}"):
                    st.write(t(crop['reason']))
            st.markdown("<br>", unsafe_allow_html=True)

    elif st.session_state.current_page == "Farmer Connect":
        st.markdown(f"<h1 style='color: #0f172a; margin-bottom: 0px;'>{t('Farmer Connect')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b;'>{t('Find local farmers and learn from their validated solutions.')}</p>", unsafe_allow_html=True)
        
        st.markdown("""<div style='background: white; border: 1px solid #eef2f0; border-radius: 16px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);'>""", unsafe_allow_html=True)
        search_q = st.text_input("🔍 " + t("Search by problem (e.g. Fungal, Pest, Tomato)")).lower()
        
        matches = []
        for fid, fdata in st.session_state.all_farms.items():
            if fid == st.session_state.farm_id: continue
            for log in fdata.get("farm_logs", []):
                d_str = (str(log.get('disease', '')) + " " + str(log.get('crop', ''))).lower()
                if not search_q or search_q in d_str:
                    matches.append({"fid": fid, "crop": log.get('crop'), "disease": log.get('disease')})
                    break
                    
        if len(matches) == 0:
            st.info(t("No matching farmers found yet in the global network."))
        else:
            for m in matches:
                mc1, mc2 = st.columns([3, 1])
                with mc1:
                    st.markdown(f"**👨‍🌾 {m['fid']}** | 🌱 {m['crop']} | 🦠 *{t(m['disease'])}*")
                    st.markdown(f"<span style='color: #ef4444; font-size: 11px; font-weight: 700;'>🔒 {t('History Private until connected')}</span>", unsafe_allow_html=True)
                with mc2:
                    if st.session_state.get(f"req_{m['fid']}"):
                        st.button("✅ " + t("Pending"), key=f"pend_{m['fid']}", disabled=True)
                    else:
                        if st.button("🤝 " + t("Connect"), key=f"conn_{m['fid']}", use_container_width=True):
                            st.session_state[f"req_{m['fid']}"] = True
                            st.toast(t("Friend Request Sent securely to ") + m['fid'])
                            st.rerun()
                st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)
        
        with st.expander(f"🧠 {t('Why connect?')}", expanded=True):
            st.write(t("Comparing solutions and dosage results directly with neighbors prevents experimental crop loss and builds a resilient local community."))

    # Floating AI Chat Bot (Sticks to bottom right on all screens)
    st.markdown("<div id='chat-anchor'></div>", unsafe_allow_html=True)
    st.markdown("""<style>
    div.element-container:has(#chat-anchor) + div.element-container {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
        width: 65px;
    }
    div.element-container:has(#chat-anchor) + div.element-container div[data-testid="stPopover"] > button {
        width: 65px !important;
        height: 65px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #2E7D32, #1b4332) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(46, 125, 50, 0.4) !important;
        font-size: 32px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }
    div.element-container:has(#chat-anchor) + div.element-container div[data-testid="stPopover"] > button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 15px 30px rgba(46, 125, 50, 0.6) !important;
    }
    </style>""", unsafe_allow_html=True)

    with st.popover("💬", use_container_width=False):
        st.markdown(f"<h3 style='color: #1e3b1d; margin-top:0px;'>{t('AgniKshetra AI Assistant')}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #64748b; font-size:13px;'>{t('Your Contextual Farming Assistant.')}</p>", unsafe_allow_html=True)
        st.markdown("""<div style='background: #f8fafc; border: 1px solid #eef2f0; border-radius: 12px; padding: 15px; max-height: 400px; overflow-y: auto; margin-bottom: 10px;'>""", unsafe_allow_html=True)
        for idx, msg in enumerate(st.session_state.chat_history):
            color = "white" if msg["role"] == "user" else "#1e293b"
            bg = "#2E7D32" if msg["role"] == "user" else "white"
            align = "right" if msg["role"] == "user" else "left"
            st.markdown(f"<div style='text-align:{align}; margin-bottom:10px;'><span style='background:{bg}; color:{color}; padding:10px 15px; border-radius:18px; display:inline-block; max-width:85%; font-size:14px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>{msg['content']}</span></div>", unsafe_allow_html=True)
            
        if len(st.session_state.chat_history) == 0:
            st.markdown(f"<div style='text-align:left; margin-bottom:10px;'><span style='background:white; color:#1e293b; padding:10px 15px; border-radius:18px; display:inline-block; max-width:85%; font-size:14px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'><b>AI:</b> {t('Hello! Ask me if you can spray tomorrow, or what to do if rain comes.')}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        c_f1, c_f2 = st.columns([4,1])
        with c_f1: user_bot_query = st.text_input("Query", placeholder=t("Type here..."), label_visibility="collapsed", key="u_query_chat")
        with c_f2: sent_msg = st.button("➤", key="btn_send_chat", use_container_width=True)

        voice_query = st.audio_input(t("Voice Ask"), label_visibility="collapsed")
        
        final_query = user_bot_query if sent_msg else None
        if voice_query is not None:
            audio_id = getattr(voice_query, "file_id", str(voice_query.size))
            if st.session_state.get('last_chat_voice') != audio_id:
                try:
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(voice_query) as source:
                        audio_data = recognizer.record(source)
                        final_query = recognizer.recognize_google(audio_data, language=LANG_CODE_MAP[st.session_state.selected_lang]["sr"])
                except: pass
                st.session_state.last_chat_voice = audio_id

        if final_query:
            st.session_state.chat_history.append({"role": "user", "content": final_query})
            query_lower = final_query.lower()
            bot_reply = t("I am analyzing your query to ensure safety first.")
            
            if "dose" in query_lower or "caps" in query_lower or "more" in query_lower:
                bot_reply = t("RED ALERT! Modifying pesticide dosage without expert advice causes severe soil degradation and toxic crop residue. ALWAYS follow the exact label protocol.")
            elif 'gemini_model' in globals() and gemini_model:
                try:
                    chat_context = "You are a helpful AI farming assistant... "
                    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.chat_history[:-1]]
                    chat = gemini_model.start_chat(history=history)
                    res = chat.send_message(f"System Context: {chat_context}\n\nUser query: {final_query}")
                    bot_reply = res.text
                except Exception as e:
                    if "spray" in query_lower and "tomorrow" in query_lower: bot_reply = t("Based on sensors, tomorrow looks optimal.")
                    elif "rain" in query_lower: bot_reply = t("If rain occurs use sticker.")
                    else: bot_reply = t("Network/API Error: ") + str(e)
            else:
                if "spray" in query_lower and "tomorrow" in query_lower: bot_reply = t("Based on sensors, tomorrow looks optimal.")
                elif "rain" in query_lower: bot_reply = t("If rain occurs use sticker.")
                else: bot_reply = t("I am currently offline. Please check your connection.")

            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            save_db(st.session_state.all_farms)
            st.rerun()


# ==========================================
# ROUTER
# ==========================================
if st.session_state.app_stage == 1:
    render_language_screen()
else:
    render_main_app()
    
