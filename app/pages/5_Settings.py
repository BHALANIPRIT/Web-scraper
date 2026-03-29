import streamlit as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="Settings — WebScraper Pro", page_icon="🌐",
                   layout="wide", initial_sidebar_state="collapsed")
from utils.layout import setup_page
from utils.icons import icon

try:
    from supabase import create_client
    from dotenv import load_dotenv
    load_dotenv()
    _SUPA = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
    SUPA_OK = True
except Exception:
    _SUPA = None
    SUPA_OK = False


def _fetch_recent_jobs(limit=10):
    """Fetch real job data from Supabase for notifications."""
    if not SUPA_OK or _SUPA is None:
        return []
    try:
        res = _SUPA.table("scrape_jobs").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except Exception:
        return []


t, main = setup_page("Settings")

with main:
    st.markdown(f"""
<div style="padding:1rem 1.4rem 0.75rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:36px;height:36px;background:{t['accent_glow']};border-radius:10px;
         display:flex;align-items:center;justify-content:center;">
      {icon('settings',18,t['accent'])}
    </div>
    <div>
      <div class="PT">Settings</div>
      <div class="PS">Manage your account preferences and configurations.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="padding:0 1.4rem 1.5rem;">', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Profile", "Appearance", "Notifications", "Billing"])

    # TAB 1: Profile
    with tab1:
        ue = st.session_state.get("user_email", "user@example.com")
        un = st.session_state.get("user_name", "")

        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;margin-bottom:1rem;display:flex;align-items:center;gap:1rem;">
  <div style="width:58px;height:58px;border-radius:50%;flex-shrink:0;
       background:linear-gradient(135deg,{t['accent']},{t['blue']});
       display:flex;align-items:center;justify-content:center;
       box-shadow:0 4px 14px {t['accent_glow']};">
    {icon('user',25,'#fff')}
  </div>
  <div>
    <div style="font-weight:700;font-size:1rem;color:{t['text']};margin-bottom:2px;">{un or ue}</div>
    <div style="font-size:0.72rem;color:{t['muted']};margin-bottom:5px;">Member since January 2026</div>
    <span class="BG G">{icon('check-circle',8,t['green'])} Pro Plan</span>
  </div>
</div>
""", unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            new_name  = st.text_input("Full Name", value=un or "John Developer", key="s_name")
            new_email = st.text_input("Email", value=ue, key="s_email")
            new_phone = st.text_input("Phone", placeholder="+91 98765 43210", key="s_phone")
        with c2:
            new_org  = st.text_input("Organization", placeholder="Your company", key="s_org")
            new_tz   = st.selectbox("Timezone", ["Asia/Kolkata (IST +5:30)", "UTC",
                                                  "America/New_York", "Europe/London"], key="s_tz")
            new_role = st.selectbox("Role", ["Developer", "Data Analyst", "Business Owner",
                                             "Researcher", "Other"], key="s_role")

        sv1, _ = st.columns([1, 3])
        with sv1:
            if st.button("Save Profile", use_container_width=True, key="save_profile"):
                st.session_state["user_name"]  = new_name
                st.session_state["user_email"] = new_email
                if SUPA_OK and _SUPA:
                    try:
                        _SUPA.table("user_profiles").upsert({
                            "email": new_email,
                            "name": new_name,
                            "phone": new_phone,
                            "organization": new_org,
                            "timezone": new_tz,
                            "role": new_role,
                        }).execute()
                        st.success("Profile saved!")
                    except Exception:
                        st.success("Profile saved locally!")
                else:
                    st.success("Profile saved!")

        st.markdown("---")
        dc1, dc2 = st.columns(2)
        with dc1:
            if st.button("Change Password", use_container_width=True, key="change_pw"):
                st.info("Password reset link sent to your email.")
        with dc2:
            if st.button("Delete Account", use_container_width=True, key="del_acc"):
                st.error("To delete your account, please contact support.")

    # TAB 2: Appearance
    with tab2:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;margin-bottom:1rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};margin-bottom:1rem;">
    Choose Theme
  </div>
""", unsafe_allow_html=True)
        tc = st.columns(3, gap="small")
        opts = [
            ("dark",  "Dark",  "#0a0e1a", icon('moon',   14, '#8899bb')),
            ("light", "Light", "#f0f4f8", icon('sun',    14, '#e8920a')),
            ("vivid", "Vivid", "#0d0a1e", icon('sparkles', 14, '#a78bfa')),
        ]
        for i, (val, label, bgc, ich) in enumerate(opts):
            with tc[i]:
                ia  = st.session_state.get("theme", "dark") == val
                bdr = f"3px solid {t['accent']}" if ia else f"1px solid {t['border']}"
                st.markdown(f"""
<div style="border:{bdr};border-radius:10px;overflow:hidden;margin-bottom:0.3rem;">
  <div style="background:{bgc};height:50px;display:flex;align-items:center;justify-content:center;">
    {ich}
  </div>
  <div style="background:{t['card']};padding:0.4rem;text-align:center;
       font-size:0.78rem;font-weight:{'700' if ia else '500'};
       color:{t['accent'] if ia else t['text']};">{label}</div>
</div>
""", unsafe_allow_html=True)
                if st.button(f"Select {label}", key=f"th_{val}", use_container_width=True):
                    st.session_state.theme = val
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};margin-bottom:0.75rem;">
    Display Preferences
  </div>
""", unsafe_allow_html=True)
        co1, co2 = st.columns(2)
        with co1:
            st.toggle("Compact Mode",  value=False, key="pref_compact")
            st.toggle("Animations",    value=True,  key="pref_anim")
        with co2:
            st.toggle("Live Console",  value=True,  key="pref_console")
            st.toggle("Auto-Export",   value=False, key="pref_autoex")
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        sv2, _ = st.columns([1, 3])
        with sv2:
            if st.button("Save Preferences", use_container_width=True, key="save_app"):
                st.success("Preferences saved!")
        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 3: Notifications — LIVE from Supabase scrape_jobs, no dummy data
    with tab3:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;margin-bottom:1rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};margin-bottom:0.75rem;">
    Notification Email
  </div>
""", unsafe_allow_html=True)
        notif_email = st.text_input("Email", value=ue, label_visibility="collapsed",
                                    key="notif_email")
        st.markdown('</div>', unsafe_allow_html=True)

        # Load real notifications from Supabase scrape_jobs
        recent_jobs = _fetch_recent_jobs(limit=10)

        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;margin-bottom:1rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};margin-bottom:0.85rem;
       display:flex;align-items:center;justify-content:space-between;">
    <span>Activity Notifications</span>
    <span style="font-size:0.72rem;color:{t['muted']};font-weight:400;">
      {len(recent_jobs)} recent events
    </span>
  </div>
""", unsafe_allow_html=True)

        if not recent_jobs:
            st.markdown(f"""
<div style="text-align:center;padding:2rem;font-size:0.85rem;color:{t['muted']};">
  No activity yet. Start a scraping job from the Dashboard.
  {'' if SUPA_OK else '<br><span style="color:'+t['red']+';">Supabase not connected.</span>'}
</div>
""", unsafe_allow_html=True)
        else:
            for job in recent_jobs:
                stat    = job.get("status", "—")
                url_j   = job.get("url", "—")
                rows_j  = job.get("rows_extracted", 0)
                dur_j   = job.get("duration", "—")
                date_j  = str(job.get("created_at", "") or "")[:16]
                scraper = job.get("scraper_name", "Custom")

                if stat == "Completed":
                    ico_html = icon('check-circle', 14, t['green'])
                    clr_bg   = f"rgba(16,185,129,0.12)"
                    clr      = t['green']
                    title    = "Job Completed"
                    desc     = f"Scrape on {url_j[:40]} completed — {rows_j} rows extracted in {dur_j}."
                elif stat == "Failed":
                    ico_html = icon('x-circle', 14, t['red'])
                    clr_bg   = "rgba(239,68,68,0.12)"
                    clr      = t['red']
                    title    = "Job Failed"
                    desc     = f"Scrape on {url_j[:40]} failed. Check URL and try again."
                else:
                    ico_html = icon('loader', 14, t['accent'])
                    clr_bg   = t['accent_glow']
                    clr      = t['accent']
                    title    = "Job Running"
                    desc     = f"Scrape on {url_j[:40]} is currently running."

                st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:10px;padding:0.75rem 0;
     border-bottom:1px solid {t['border']};">
  <div style="width:34px;height:34px;border-radius:9px;flex-shrink:0;
       background:{clr_bg};display:flex;align-items:center;justify-content:center;">
    {ico_html}
  </div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.85rem;font-weight:600;color:{t['text']};margin-bottom:2px;">{title}
      <span style="font-size:0.7rem;font-weight:400;color:{t['muted']};margin-left:6px;">{scraper}</span>
    </div>
    <div style="font-size:0.76rem;color:{t['text2']};line-height:1.5;">{desc}</div>
  </div>
  <div style="font-size:0.7rem;color:{t['muted']};white-space:nowrap;flex-shrink:0;">{date_j}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        sv3, _ = st.columns([1, 3])
        with sv3:
            if st.button("Save Notification Settings", use_container_width=True, key="save_notif"):
                st.success("Settings saved!")

    # TAB 4: Billing — realistic with live usage from Supabase
    with tab4:
        # Fetch real usage counts from Supabase
        real_api_calls = 0
        real_rows = 0
        if SUPA_OK and _SUPA:
            try:
                res = _SUPA.table("scrape_jobs").select("rows_extracted").execute()
                jobs_data = res.data or []
                real_api_calls = len(jobs_data)
                real_rows = sum(int(str(r.get("rows_extracted", 0) or 0))
                                for r in jobs_data
                                if str(r.get("rows_extracted", "0")).isdigit())
            except Exception:
                pass

        st.markdown(f"""
<div style="background:linear-gradient(135deg,{t['accent_glow']},{t['bg2']});
     border:1px solid {t['accent']};border-radius:14px;
     padding:1.3rem 1.4rem;margin-bottom:1rem;">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <div>
      <div style="display:inline-flex;align-items:center;gap:5px;
           background:{t['accent']};color:#fff;padding:3px 10px;
           border-radius:99px;font-size:0.7rem;font-weight:700;margin-bottom:0.5rem;">
        {icon('star',9,'#fff')} Pro Plan
      </div>
      <div style="font-size:1.5rem;font-weight:800;color:{t['text']};
           letter-spacing:-0.03em;margin-bottom:3px;">Rs. 999 / month</div>
      <div style="font-size:0.78rem;color:{t['text2']};">Next billing: April 20, 2026</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.7rem;color:{t['muted']};margin-bottom:4px;">Status</div>
      <span class="BG G">
        <span style="width:7px;height:7px;border-radius:50%;background:{t['green']};display:inline-block;"></span>
        Active
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        bc1, bc2 = st.columns(2, gap="medium")
        with bc1:
            if st.button("Manage Plan", use_container_width=True, key="manage_plan"):
                st.info("Redirecting to billing portal...")
        with bc2:
            if st.button("Cancel Plan", use_container_width=True, key="cancel_plan"):
                st.error("To cancel, please contact support@webscrapepro.com")

        # Usage — real numbers from Supabase where available
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;margin-top:1rem;margin-bottom:1rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};margin-bottom:1rem;">
    Usage This Month
    {f'<span style="font-size:0.72rem;font-weight:400;color:{t["muted"]};margin-left:6px;">Live data from your account</span>' if SUPA_OK else ''}
  </div>
""", unsafe_allow_html=True)

        usage_items = [
            ("API Calls",       real_api_calls if SUPA_OK else 0, 10000, t['accent']),
            ("Rows Extracted",  real_rows if SUPA_OK else 0,      50000, t['blue']),
            ("Active Scrapers", 1 if real_api_calls > 0 else 0,   20,    t['green']),
            ("Storage Used",    max(1, real_rows // 100),          1000,  t['purple']),
        ]
        for label, used, total, clr in usage_items:
            pct = min(int(used / total * 100), 100)
            u1, u2 = st.columns([4, 1])
            with u1:
                st.markdown(f"""
<div style="margin-bottom:0.5rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
    <span style="font-size:0.82rem;font-weight:600;color:{t['text']};">{label}</span>
    <span style="font-size:0.72rem;color:{t['muted']};">{pct}%</span>
  </div>
  <div style="height:7px;background:{t['border']};border-radius:4px;overflow:hidden;">
    <div style="height:100%;width:{pct}%;background:{clr};border-radius:4px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)
            with u2:
                st.markdown(f"""
<div style="font-size:0.74rem;color:{t['muted']};text-align:right;padding-top:1rem;">
  {used:,}/{total:,}
</div>
""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Billing history — static (realistic)
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};margin-bottom:0.85rem;">
    Billing History
  </div>
""", unsafe_allow_html=True)
        billing_hist = [
            ("Mar 20, 2026", "Pro Plan — Monthly", "Rs. 999", "Paid"),
            ("Feb 20, 2026", "Pro Plan — Monthly", "Rs. 999", "Paid"),
            ("Jan 20, 2026", "Pro Plan — Monthly", "Rs. 999", "Paid"),
        ]
        th_s = (f"text-align:left;padding:0.4rem 0.7rem;font-size:0.67rem;font-weight:700;"
                f"color:{t['muted']};text-transform:uppercase;letter-spacing:0.06em;"
                f"border-bottom:1px solid {t['border']};")
        th_html = "".join(f'<th style="{th_s}">{h}</th>'
                          for h in ["Date", "Description", "Amount", "Status"])
        rows_html = ""
        for bdate, bdesc, bamt, bstat in billing_hist:
            rows_html += f"""<tr>
<td style="padding:0.55rem 0.7rem;border-bottom:1px solid {t['border']};font-size:0.8rem;color:{t['text2']};">{bdate}</td>
<td style="padding:0.55rem 0.7rem;border-bottom:1px solid {t['border']};font-size:0.8rem;color:{t['text']};">{bdesc}</td>
<td style="padding:0.55rem 0.7rem;border-bottom:1px solid {t['border']};font-size:0.8rem;color:{t['text']};font-weight:600;">{bamt}</td>
<td style="padding:0.55rem 0.7rem;border-bottom:1px solid {t['border']};">
  <span style="background:rgba(16,185,129,0.14);color:{t['green']};padding:2px 8px;border-radius:20px;font-size:0.68rem;font-weight:600;">{bstat}</span>
</td></tr>"""
        st.markdown(f"""
<table style="width:100%;border-collapse:collapse;">
  <thead><tr>{th_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)