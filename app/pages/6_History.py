import streamlit as st, pandas as pd, sys, os, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="History — WebScraper Pro", page_icon="🌐",
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


def fetch_history():
    if not SUPA_OK or _SUPA is None:
        return []
    try:
        res = _SUPA.table("scrape_jobs").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def delete_job(job_id):
    if not SUPA_OK or _SUPA is None:
        return False
    try:
        _SUPA.table("scrape_jobs").delete().eq("id", job_id).execute()
        return True
    except Exception:
        return False


def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="History")
    return buf.getvalue()


t, main = setup_page("History")

with main:
    st.markdown(f"""
<div style="padding:1rem 1.4rem 0.75rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:36px;height:36px;background:{t['accent_glow']};border-radius:10px;
         display:flex;align-items:center;justify-content:center;">
      {icon('clock',18,t['accent'])}
    </div>
    <div>
      <div class="PT">History</div>
      <div class="PS">Complete record of all your past scraping activity.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    history = fetch_history()

    total_jobs   = len(history)
    total_rows   = sum(int(str(r.get("rows_extracted", 0) or 0))
                       for r in history
                       if str(r.get("rows_extracted", "0")).isdigit())
    completed    = sum(1 for r in history if r.get("status") == "Completed")
    failed       = sum(1 for r in history if r.get("status") == "Failed")
    success_rate = f"{(completed / total_jobs * 100):.1f}%" if total_jobs else "—"

    # Stats cards
    st.markdown(f'<div style="padding:0 1.4rem 1rem;">', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4, gap="small")
    for col, val, lbl, clr in [
        (sc1, total_jobs,        "Total Jobs",    t['blue']),
        (sc2, f"{total_rows:,}", "Rows Scraped",  t['green']),
        (sc3, f"{completed}",    "Completed",     t['accent']),
        (sc4, success_rate,      "Success Rate",  t['purple']),
    ]:
        with col:
            col.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem;border-top:3px solid {clr};">
  <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;
       letter-spacing:0.06em;color:{t['text2']};margin-bottom:0.2rem;">{lbl}</div>
  <div style="font-size:1.75rem;font-weight:700;color:{t['text']};">{val}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not SUPA_OK:
        st.warning("Supabase not connected. Add SUPABASE_URL and SUPABASE_KEY to your .env file.")

    # Filters
    st.markdown(f'<div style="padding:0 1.4rem 0.75rem;">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.2, 0.8])
    with f1:
        search = st.text_input("Search", "", placeholder="Search by URL or scraper...",
                               label_visibility="collapsed")
    with f2:
        sf = st.selectbox("Status", ["All Status", "Completed", "Failed", "Running"],
                          label_visibility="collapsed")
    with f3:
        pf = st.selectbox("Period", ["All Time", "Today", "This Week", "This Month"],
                          label_visibility="collapsed")
    with f4:
        if st.button("Refresh", use_container_width=True, key="hist_refresh"):
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Filter
    filtered = history
    if sf != "All Status":
        filtered = [r for r in filtered if r.get("status") == sf]
    if search:
        s = search.lower()
        filtered = [r for r in filtered
                    if s in str(r.get("url", "")).lower()
                    or s in str(r.get("scraper_name", "")).lower()]

    # History table
    st.markdown(f'<div style="padding:0 1.4rem 0.5rem;">', unsafe_allow_html=True)
    bm = {
        "Completed": ("rgba(16,185,129,0.14)", t['green'],  icon('check-circle', 9, t['green'])),
        "Failed":    ("rgba(239,68,68,0.14)",  t['red'],    icon('x-circle',     9, t['red'])),
        "Running":   (t['accent_glow'],        t['accent'], icon('loader',       9, t['accent'])),
    }
    th_s = (f"text-align:left;padding:0.5rem 0.8rem;font-size:0.67rem;font-weight:600;"
            f"color:{t['muted']};text-transform:uppercase;letter-spacing:0.06em;"
            f"border-bottom:1px solid {t['border']};")
    th = "".join(f'<th style="{th_s}">{h}</th>'
                 for h in ["Job ID", "Scraper", "URL", "Date", "Duration", "Rows", "Status", "Actions"])

    rows = ""
    for row in filtered:
        jid   = str(row.get("id", "—"))
        jid_s = jid[:8]
        sc    = row.get("scraper_name", "—")
        url_r = str(row.get("url", "—"))
        date  = str(row.get("created_at", "") or "")[:16]
        dur   = row.get("duration", "—")
        rn    = str(row.get("rows_extracted", "—"))
        stat  = row.get("status", "—")
        bg, fg, ich = bm.get(stat, (t['card'], t['text2'], ""))
        act = ""
        if stat == "Completed":
            act = (f'<span style="background:{t["card"]};border:1px solid {t["border"]};'
                   f'color:{t["text2"]};padding:2px 6px;border-radius:6px;font-size:0.67rem;">'
                   f'{icon("download",9,t["text2"])} Export</span>')
        elif stat == "Failed":
            act = (f'<span style="background:{t["card"]};border:1px solid {t["border"]};'
                   f'color:{t["red"]};padding:2px 6px;border-radius:6px;font-size:0.67rem;">'
                   f'{icon("refresh-cw",9,t["red"])} Retry</span>')

        td = f"padding:0.62rem 0.8rem;border-bottom:1px solid {t['border']};"
        rows += (f'<tr>'
                 f'<td style="{td}font-family:monospace;font-size:0.7rem;color:{t["text"]};">{jid_s}</td>'
                 f'<td style="{td}color:{t["text"]};font-weight:500;">{sc}</td>'
                 f'<td style="{td}font-family:monospace;font-size:0.69rem;color:{t["text2"]};">'
                 f'{url_r[:40]}{"..." if len(url_r)>40 else ""}</td>'
                 f'<td style="{td}color:{t["text2"]};font-size:0.79rem;">{date}</td>'
                 f'<td style="{td}color:{t["text2"]};font-size:0.79rem;">{dur}</td>'
                 f'<td style="{td}color:{t["text"]};font-weight:600;">{rn}</td>'
                 f'<td style="{td}"><span style="background:{bg};color:{fg};padding:2px 6px;'
                 f'border-radius:20px;font-size:0.67rem;font-weight:600;'
                 f'display:inline-flex;align-items:center;gap:2px;">{ich} {stat}</span></td>'
                 f'<td style="{td}">{act}</td>'
                 f'</tr>')

    empty = (f'<tr><td colspan="8" style="text-align:center;padding:2.5rem;'
             f'color:{t["muted"]};font-size:0.83rem;">'
             f'No history yet. Start a scraping job from the Dashboard.</td></tr>'
             if not filtered else "")

    st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem;overflow-x:auto;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.7rem;display:flex;align-items:center;justify-content:space-between;">
    <span style="display:flex;align-items:center;gap:6px;">
      {icon('clock',13,t['accent'])} Scraping History
      <span style="font-size:0.67rem;font-weight:400;color:{t['muted']};margin-left:3px;">
        ({len(filtered)} records)
      </span>
    </span>
  </div>
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr>{th}</tr></thead>
    <tbody>{rows}{empty}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Delete buttons for each row (working action)
    if filtered and SUPA_OK:
        st.markdown(f'<div style="padding:0 1.4rem 0.25rem;">', unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-size:0.74rem;color:{t['muted']};margin-bottom:0.4rem;">
  Select a job to delete it from history:
</div>
""", unsafe_allow_html=True)
        del_cols = st.columns(min(len(filtered), 5))
        for i, row in enumerate(filtered[:5]):
            jid = str(row.get("id", ""))
            jid_s = jid[:6]
            with del_cols[i % 5]:
                if st.button(f"Delete #{jid_s}", key=f"del_job_{i}", use_container_width=True):
                    if delete_job(jid):
                        st.success(f"Job {jid_s} deleted.")
                        st.rerun()
                    else:
                        st.error("Delete failed.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Export buttons
    st.markdown(f'<div style="padding:0 1.4rem 1.5rem;">', unsafe_allow_html=True)
    ec1, ec2, ec3, _ = st.columns([1, 1, 1, 2])

    df_export = pd.DataFrame([{
        "Job ID":   str(r.get("id", ""))[:8],
        "Scraper":  r.get("scraper_name", ""),
        "URL":      r.get("url", ""),
        "Date":     str(r.get("created_at", ""))[:16],
        "Duration": r.get("duration", ""),
        "Rows":     r.get("rows_extracted", ""),
        "Status":   r.get("status", ""),
    } for r in filtered]) if filtered else pd.DataFrame(
        columns=["Job ID", "Scraper", "URL", "Date", "Duration", "Rows", "Status"])

    with ec1:
        st.download_button("Export CSV", df_export.to_csv(index=False),
                           "history.csv", "text/csv", use_container_width=True,
                           key="exp_csv")
    with ec2:
        st.download_button("Export JSON", df_export.to_json(orient="records"),
                           "history.json", "application/json", use_container_width=True,
                           key="exp_json")
    with ec3:
        st.download_button("Export Excel", to_excel(df_export), "history.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True, key="exp_excel")
    st.markdown('</div>', unsafe_allow_html=True)