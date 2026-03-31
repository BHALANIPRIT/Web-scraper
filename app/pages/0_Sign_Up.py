import streamlit as st
import sys, os, time
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Sign Up — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styles import apply_theme, theme_selector
from utils.icons import icon

# Initialize Supabase Client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

t = apply_theme()

if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Dashboard.py")

st.markdown(f"""
<style>
[data-testid="stSidebar"] {{ display: none !important; }}
.block-container {{
    padding: 1rem 2rem 2rem !important;
    max-width: 100% !important;
}}
[data-testid="stTextInput"] > div > div > input {{
    background: {t['bg']} !important;
    border: 1.5px solid {t['border_l']} !important;
    border-radius: 10px !important;
    color: {t['text']} !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
}}
[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
}}
[data-testid="stTextInput"] > label {{
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    color: {t['text2']} !important;
    margin-bottom: 0.2rem !important;
}}
[data-testid="stTextInput"] > div > div > input::placeholder {{
    color: {t['muted']} !important;
}}
.signup-btn > div > button {{
    background: linear-gradient(135deg,{t['accent']},{t['accent_h']}) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-size: 0.95rem !important;
    font-weight: 700 !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important; padding: 0.75rem !important;
    box-shadow: 0 4px 20px {t['accent_glow']} !important;
    width: 100% !important; transform: none !important; filter: none !important;
}}
.signup-btn > div > button:hover {{
    box-shadow: 0 6px 28px {t['accent_glow']} !important;
}}
.signin-outline > div > button {{
    background: transparent !important; color: #fff !important;
    border: 2.5px solid #fff !important; border-radius: 10px !important;
    font-size: 0.9rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
    padding: 0.65rem !important; box-shadow: none !important;
    width: 100% !important; transform: none !important; filter: none !important;
}}
.signin-outline > div > button:hover {{
    background: rgba(255,255,255,0.18) !important;
}}
.back-btn > div > button {{
    background: {t['bg2']} !important; color: {t['text2']} !important;
    border: 1px solid {t['border']} !important; border-radius: 8px !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    box-shadow: none !important; transform: none !important;
}}
.social-row {{
    display:flex; gap:0.75rem; justify-content:center; margin:0.75rem 0;
}}
.soc-btn {{
    display:inline-flex; align-items:center; justify-content:center;
    width:46px; height:46px; border-radius:50%;
    cursor:pointer; transition:transform 0.15s, box-shadow 0.15s;
    text-decoration:none; flex-shrink:0;
}}
.soc-btn:hover {{
    transform:translateY(-2px);
    box-shadow:0 4px 12px rgba(0,0,0,0.2);
}}
.soc-google   {{ background:#fff; border:1.5px solid #ddd; }}
.soc-facebook {{ background:#1877F2; }}
.soc-github   {{ background:#24292e; }}
.soc-linkedin {{ background:#0A66C2;  }}
.soc-disabled-label {{
    font-size:0.65rem; color:{t['muted']}; text-align:center; margin-top:0.3rem;
}}
</style>
""", unsafe_allow_html=True)

tb1, _, tb3 = st.columns([1, 7, 1])
with tb1:
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("Back", key="su_back"):
        st.switch_page("Home.py")
    st.markdown('</div>', unsafe_allow_html=True)
with tb3:
    theme_selector("su_theme")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

gap, left_col, right_col, gap2 = st.columns([0.5, 1.8, 2.2, 0.5])

# LEFT — teal welcome panel + SIGN IN
with left_col:
    st.markdown(f"""
    <div style="background:linear-gradient(150deg,#12b8b0 0%,#0c7a90 45%,#0a4f72 100%);
         border-radius:20px;padding:3.5rem 2rem;min-height:400px;
         display:flex;flex-direction:column;align-items:center;
         justify-content:center;text-align:center;
         position:relative;overflow:hidden;">
      <div style="position:absolute;top:-60px;right:-50px;width:230px;height:230px;
           background:rgba(255,255,255,0.07);border-radius:50%;"></div>
      <div style="position:absolute;bottom:-80px;left:-40px;width:260px;height:260px;
           background:rgba(255,255,255,0.04);border-radius:50%;"></div>
      <div style="position:relative;z-index:2;">
        <div style="font-size:1.85rem;font-weight:800;color:#fff;
             margin-bottom:0.9rem;line-height:1.2;">Welcome Back!</div>
        <p style="font-size:0.88rem;color:rgba(255,255,255,0.88);
             line-height:1.7;max-width:220px;margin:0 auto 1.75rem;">
          To keep connected with us please login with your personal info
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    st.markdown('<div class="signin-outline">', unsafe_allow_html=True)
    if st.button("SIGN IN", key="goto_signin", use_container_width=True):
        st.switch_page("pages/0_Sign_In.py")
    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT — signup form
with right_col:
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-radius:20px 20px 0 0;padding:2rem 2.5rem 1rem;text-align:center;">
      <div style="font-size:1.7rem;font-weight:800;letter-spacing:-0.03em;
           color:{t['text']};margin-bottom:0.2rem;">Create Account</div>
      <div style="font-size:0.82rem;color:{t['muted']};">
        or use your email for registration
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown(f'<div style="background:{t["card"]};padding:0.5rem 1.5rem;'
                    f'border-left:1px solid {t["border"]};border-right:1px solid {t["border"]};">',
                    unsafe_allow_html=True)
        name  = st.text_input("Your Name",      placeholder="Your Name",        key="su_name")
        email = st.text_input("Your Email",      placeholder="Your Email",       key="su_email")
        pw    = st.text_input("Password",         placeholder="Password",
                              type="password",    key="su_pw")
        pw2   = st.text_input("Confirm Password", placeholder="Confirm Password",
                              type="password",    key="su_pw2")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-top:none;border-radius:0 0 20px 20px;
         padding:0.75rem 2.5rem 1.5rem;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="signup-btn">', unsafe_allow_html=True)
    if st.button("SIGN UP", key="signup_btn", use_container_width=True):
        if not all([name, email, pw, pw2]):
            st.error("Please fill in all fields.")
        elif pw != pw2:
            st.error("Passwords do not match.")
        elif len(pw) < 6:
            st.error("Password must be at least 6 characters.")
        else:
            try:
                # Supabase Sign Up
                # data.user contains the user object if successful
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": pw,
                    "options": {
                        "data": {
                            "full_name": name # Store name in user metadata
                        }
                    }
                })
                
                if response.user:
                    st.session_state["logged_in"]  = True
                    st.session_state["user_email"] = response.user.email
                    st.session_state["user_name"]  = name
                    st.session_state["user_id"]    = response.user.id
                    
                    st.success(f"Account created successfully for {name}!")
                    time.sleep(1.5)
                    st.switch_page("pages/1_Dashboard.py")
                    
            except Exception as e:
                # Handle errors (e.g., user already exists)
                error_msg = str(e)
                if "User already registered" in error_msg:
                    st.error("This email is already registered. Please sign in.")
                else:
                    st.error(f"Sign up failed: {error_msg}")
                    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;margin-top:0.75rem;font-size:0.83rem;color:{t['text2']};">
      Already a member?&nbsp;
      <a href="/Sign_In" style="color:{t['accent']};font-weight:600;text-decoration:none;">
        Sign in
      </a>
    </div>
    """, unsafe_allow_html=True)