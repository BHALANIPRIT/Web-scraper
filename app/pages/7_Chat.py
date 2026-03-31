import streamlit as st
import time, sys, os
from supabase import create_client, Client
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- PATH FIX ----------------
_here = os.path.dirname(os.path.abspath(__file__))
_app  = os.path.dirname(_here)
_root = os.path.dirname(_app)
for _p in (_root, _app):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Chat — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.layout import setup_page
from utils.icons  import icon
from llm.groq_client import call_llm_api

# ---------------- SYSTEM ----------------
_SYSTEM = """You are the AI assistant for WebScraper Pro, an AI-driven web scraping platform.

Your role:
- Help users design scraping strategies (CSS selectors, HTML tags, class names)
- Explain Dashboard features: URL input, query box, export buttons
- Advise on Data Analysis: chart types, column selection, AI Analysis tab
- Explain Scheduler: frequency options (hourly/daily/weekly), export format
- Answer questions about export formats: CSV, JSON, Excel
- Debug scraping issues: 0 items extracted, wrong data, selector problems

Key platform facts:
- Uses Playwright headless browser + Groq LLaMA 3.3 70B for intelligence
- Scraping modes: E-commerce, News, Job Listings, Custom
- Data Analysis Canvas: Table View, Charts (bar/line/area), AI Analysis

Tone: concise, expert, friendly. Use markdown.
"""

# ---------------- LLM ----------------
def _llm_response(user_msg: str, history: list) -> str:
    messages = [{"role": "system", "content": _SYSTEM}]
    for m in history[-40:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_msg})

    try:
        reply = call_llm_api(prompt=messages, temperature=0.45, max_tokens=1024)
        return reply or "I couldn't generate a response. Please try again."
    except Exception as e:
        return f"LLM error: {str(e)}"

# ---------------- SUPABASE FUNCTIONS ----------------
def load_sessions():
    res = supabase.table("chat_sessions").select("*").order("created_at", desc=True).execute()
    return res.data or []

def load_messages(session_id):
    res = supabase.table("chat_messages") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at") \
        .execute()
    return res.data or []

def create_session():
    sid = f"s_{int(time.time()*1000)}"
    session = {
        "id": sid,
        "title": "New Chat",
        "ts": time.strftime("%b %d, %H:%M")
    }
    supabase.table("chat_sessions").insert(session).execute()
    return session

def save_message(session_id, role, content):
    supabase.table("chat_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()

def update_title(session_id, title):
    supabase.table("chat_sessions").update({"title": title}).eq("id", session_id).execute()

# ---------------- INIT ----------------
def _init():
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = load_sessions()
    if "active_sid" not in st.session_state:
        st.session_state.active_sid = None
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = {}

def _new_session():
    session = create_session()
    st.session_state.chat_sessions.insert(0, session)
    st.session_state.chat_messages[session["id"]] = []
    st.session_state.active_sid = session["id"]

_init()
t, main = setup_page("Chat")

# Ensure at least one session
if not st.session_state.chat_sessions:
    _new_session()

ids = [s["id"] for s in st.session_state.chat_sessions]
if st.session_state.active_sid not in ids:
    st.session_state.active_sid = st.session_state.chat_sessions[0]["id"]

sid = st.session_state.active_sid

# Load messages from DB if not loaded
if sid not in st.session_state.chat_messages:
    db_msgs = load_messages(sid)
    st.session_state.chat_messages[sid] = [
        {"role": m["role"], "content": m["content"]} for m in db_msgs
    ]

messages = st.session_state.chat_messages.get(sid, [])

with main:

    # HEADER (UNCHANGED)
    st.markdown(f"""
<div style="padding:0.9rem 1.4rem 0.6rem;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:40px;height:40px;flex-shrink:0;
         background:linear-gradient(135deg,{t['accent']},{t['purple']});
         border-radius:12px;display:flex;align-items:center;justify-content:center;
         box-shadow:0 4px 16px {t['accent_glow']};">
      {icon('bot', 20, '#fff')}
    </div>
    <div>
      <div class="PT" style="margin:0;">AI Chat Assistant</div>
      <div class="PS" style="margin:0;">Powered by Groq · LLaMA 3.3 70B</div>
    </div>
  </div>
</div>
<div style="padding:0 1.4rem;">
  <div style="height:1px;background:{t['border']};margin-bottom:0.75rem;"></div>
</div>
""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 3], gap="medium")

    # ---------------- LEFT ----------------
    with left_col:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.75rem;overflow-y:auto;max-height:75vh;">
""", unsafe_allow_html=True)

        if st.button("New Chat", key="new_chat_btn", use_container_width=True):
            _new_session()
            st.rerun()

        st.markdown("<div style='margin-top:0.4rem;'>", unsafe_allow_html=True)

        for sess in st.session_state.chat_sessions:
            is_active = sess["id"] == sid

            st.markdown(f"""
<div style="padding:0.4rem;margin-bottom:0.3rem;">
  <div style="font-size:0.75rem;">{sess['title']}</div>
</div>
""", unsafe_allow_html=True)

            if not is_active:
                if st.button("Open", key=f"open_{sess['id']}", use_container_width=True):
                    st.session_state.active_sid = sess["id"]
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # ---------------- RIGHT ----------------
    with right_col:

        chat_container = st.container(height=460)

        with chat_container:
            if not messages:
                st.markdown("### How can I help you today?")
            else:
                for msg in messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        user_input = st.chat_input("Ask anything...")

        if user_input:

            # Update title if first message
            for s in st.session_state.chat_sessions:
                if s["id"] == sid and s["title"] == "New Chat":
                    new_title = user_input[:28]
                    s["title"] = new_title
                    update_title(sid, new_title)

            # Save USER
            st.session_state.chat_messages[sid].append({
                "role": "user",
                "content": user_input
            })
            save_message(sid, "user", user_input)

            # AI
            with st.spinner("Thinking…"):
                ai_reply = _llm_response(user_input, messages)

            # Save AI
            st.session_state.chat_messages[sid].append({
                "role": "assistant",
                "content": ai_reply
            })
            save_message(sid, "assistant", ai_reply)

            st.rerun()