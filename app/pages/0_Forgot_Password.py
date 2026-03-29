import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Reset Password — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styles import apply_theme
from utils.icons import icon

t = apply_theme()

# Supabase (safe init)
try:
    from supabase import create_client
    from dotenv import load_dotenv
    load_dotenv()
    _SUPA = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
    SUPA_OK = True
except Exception:
    _SUPA = None
    SUPA_OK = False


st.markdown(f"""
<style>
[data-testid="stSidebar"] {{ display: none !important; }}
.block-container {{
    padding: 2rem !important;
    max-width: 100% !important;
}}
[data-testid="stTextInput"] > div > div > input {{
    background: {t['bg']} !important;
    border: 1.5px solid {t['border_l']} !important;
    border-radius: 10px !important;
    color: {t['text']} !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.92rem !important;
}}
[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
}}
.send-btn > div > button {{
    background: linear-gradient(135deg, {t['accent']}, {t['accent_h']}) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 0.75rem !important;
    box-shadow: 0 4px 20px {t['accent_glow']} !important;
    width: 100% !important;
}}
</style>
""", unsafe_allow_html=True)

_, col, _ = st.columns([1, 2, 1])
with col:
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-radius:20px;padding:3rem 2.5rem;margin-top:2rem;text-align:center;">
      <div style="width:56px;height:56px;margin:0 auto 1.2rem;
           background:{t['accent_glow']};border-radius:14px;
           display:flex;align-items:center;justify-content:center;">
        {icon('lock', 26, t['accent'])}
      </div>
      <div style="font-size:1.6rem;font-weight:800;color:{t['text']};margin-bottom:0.4rem;">
        Reset Password
      </div>
      <div style="font-size:0.85rem;color:{t['muted']};margin-bottom:1.5rem;line-height:1.6;">
        Enter your registered email address and we will send you a link to reset your password.
      </div>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("Email Address", placeholder="Enter your registered email", key="fp_email")

    st.markdown('<div class="send-btn">', unsafe_allow_html=True)
    if st.button("Send Reset Link", use_container_width=True, key="fp_send"):
        if not email:
            st.error("Please enter your email address.")
        elif "@" not in email:
            st.error("Please enter a valid email address.")
        else:
            # Try Supabase password reset
            sent = False
            if SUPA_OK and _SUPA:
                try:
                    _SUPA.auth.reset_password_email(email)
                    sent = True
                except Exception:
                    sent = False

            if sent:
                st.success(f"Password reset link sent to {email}. Please check your inbox.")
            else:
                # Fallback message (Supabase not configured or error)
                st.success(f"If {email} is registered, you will receive a reset link shortly.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    if st.button("Back to Sign In", use_container_width=True, key="fp_back"):
        st.switch_page("pages/0_Sign_In.py")