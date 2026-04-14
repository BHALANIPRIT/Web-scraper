import streamlit as st, sys, os, uuid
from datetime import datetime, date, time as dtime, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
  sys.path.insert(0, PROJECT_ROOT)
st.set_page_config(page_title="Scheduler — WebScraper Pro", page_icon="🌐",
                   layout="wide", initial_sidebar_state="collapsed")
from utils.layout import setup_page
from utils.icons import icon
from scheduler.models import ScrapeJob
from scheduler.scheduler_manager import SchedulerManager
from scheduler.job_registry import JobRegistry

if "scheduler" not in st.session_state:
  st.session_state.scheduler = SchedulerManager()
if "registry" not in st.session_state:
  st.session_state.registry = JobRegistry()

scheduler_manager = st.session_state.scheduler
job_registry = st.session_state.registry

SCRAPERS       = ["Custom Scraper", "E-commerce Scraper", "News Scraper", "Job Listings Scraper"]
FREQ_OPTIONS   = ["Hourly", "Every 6h", "Daily", "Weekly", "Monthly"]
FORMAT_OPTIONS = ["CSV", "JSON", "Excel"]

# How often each frequency runs per day (for next runs table)
FREQ_INTERVALS = {
    "Hourly":    timedelta(hours=1),
    "Every 6h":  timedelta(hours=6),
    "Daily":     timedelta(days=1),
    "Weekly":    timedelta(weeks=1),
    "Monthly":   timedelta(days=30),
}

t, main = setup_page("Scheduler")

STATUS_COLORS = {
    "Active":    (t["accent_glow"], t["green"]),
    "Paused":    (t["accent_glow"], t["accent"]),
    "Completed": ("rgba(59,130,246,0.14)", t["blue"]),
}
SCRAPER_COLORS = {
    "Custom Scraper":       t.get("cyan", "#06b6d4"),
    "E-commerce Scraper":   t["accent"],
    "News Scraper":         t["blue"],
    "Job Listings Scraper": t["purple"],
}


def _get_next_run_label(job):
  if not getattr(job, "is_active", False):
    return "—"
  try:
    aps_job = scheduler_manager.scheduler.get_job(job.job_id)
    if aps_job and aps_job.next_run_time:
      return aps_job.next_run_time.strftime("%Y-%m-%d %H:%M")
  except Exception:
    pass
  return "Scheduled"


def _to_row(job):
  return {
    "id": job.job_id,
    "scraper": job.scraper_type,
    "url": job.target_url,
    "query": job.query,
    "frequency": job.frequency,
    "start_time": job.start_time,
    "start_date": job.start_date,
    "format": job.export_format,
    "max_rows": int(job.max_rows),
    "email_notify": bool(job.email_notification),
    "status": "Active" if bool(job.is_active) else "Paused",
    "next_run": _get_next_run_label(job),
  }

with main:
    PAD = "padding:0 1.4rem"

    st.markdown(f"""
<div style="{PAD} 0.4rem;padding-top:1rem;margin-bottom:0.8rem;">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:36px;height:36px;
         background:linear-gradient(135deg,{t['blue']},{t['purple']});
         border-radius:10px;display:flex;align-items:center;justify-content:center;">
      {icon('calendar',18,'#fff')}
    </div>
    <div>
      <div class="PT">Automated Scheduler</div>
      <div class="PS">Set up recurring scrape jobs with custom frequencies and exports.</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="{PAD} 0;">', unsafe_allow_html=True)

    # Create Schedule form
    st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.2rem;margin-bottom:1rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};
       margin-bottom:0.9rem;display:flex;align-items:center;gap:7px;">
    {icon('plus',14,t['accent'])} Create New Schedule
  </div>
""", unsafe_allow_html=True)

    r1c1, r1c2 = st.columns(2, gap="medium")
    with r1c1:
        scraper_name = st.selectbox("Scraper Type", SCRAPERS, key="sch_scraper")
    with r1c2:
        url_input = st.text_input("Target URL", placeholder="https://example.com/page", key="sch_url")

    # Query input — what to extract (like Dashboard)
    query_input = st.text_input(
        "Query — What do you want to extract?",
        placeholder="e.g. Extract all product names, prices, and ratings",
        key="sch_query",
    )

    r2c1, r2c2, r2c3 = st.columns(3, gap="medium")
    with r2c1:
        frequency = st.selectbox("Frequency", FREQ_OPTIONS, key="sch_freq")
    with r2c2:
        start_time_val = st.time_input("Start Time", value=dtime(9, 0), key="sch_time")
    with r2c3:
        start_date_val = st.date_input("Start Date", value=date.today(), key="sch_date")

    # Match demo scheduler behavior: allow explicit minute override for hourly jobs.
    start_minute = int(start_time_val.minute)
    if frequency == "Hourly":
      start_minute = st.number_input(
        "Minute of hour (0-59)",
        min_value=0,
        max_value=59,
        value=int(start_time_val.minute),
        key="sch_minute",
      )

    r3c1, r3c2, r3c3 = st.columns(3, gap="medium")
    with r3c1:
        exp_format = st.selectbox("Export Format", FORMAT_OPTIONS, key="sch_format")
    with r3c2:
        max_rows = st.number_input("Max Rows", min_value=10, max_value=10000,
                                   value=500, step=50, key="sch_rows")
    with r3c3:
        email_notify = st.toggle("Email Notification", value=False, key="sch_email")

    # Active on creation toggle
    start_active = st.toggle("Start as Active", value=True, key="sch_start_active")

    st.markdown('</div>', unsafe_allow_html=True)

    sc1, _ = st.columns([1, 4])
    with sc1:
        do_schedule = st.button("Schedule Scraper", key="btn_schedule", use_container_width=True)

    if do_schedule:
        if not url_input:
            st.error("Please enter a target URL.")
        elif not query_input:
            st.error("Please enter a query describing what to extract.")
        else:
            job = ScrapeJob(
                job_id=str(uuid.uuid4()),
                scraper_type=scraper_name,
                target_url=url_input,
                query=query_input,
                frequency=frequency,
                start_time=start_time_val.strftime("%H:%M"),
                start_date=start_date_val.strftime("%Y-%m-%d"),
                export_format=exp_format,
                max_rows=int(max_rows),
                email_notification=bool(email_notify),
                is_active=bool(start_active),
                start_minute=int(start_minute),
            )
            job_registry.add_job(job)
            if job.is_active:
                scheduler_manager.add_job(job)
            st.success(
                f"Scheduled — {scraper_name} runs {frequency} starting {job.start_date} at {job.start_time} "
                f"(Status: {'Active' if job.is_active else 'Paused'})"
            )
            st.rerun()

    st.markdown(f'<div style="height:0.75rem"></div>', unsafe_allow_html=True)

    # Summary stats
    scheds = [_to_row(job) for job in job_registry.get_all_jobs()]
    total    = len(scheds)
    active   = sum(1 for s in scheds if s["status"] == "Active")
    paused   = sum(1 for s in scheds if s["status"] == "Paused")
    next_run = next((s["next_run"] for s in scheds if s["status"] == "Active"), "—")

    mc1, mc2, mc3, mc4 = st.columns(4, gap="small")
    for col, val, lbl, clr in [
        (mc1, total,    "Total Scheduled", t['blue']),
        (mc2, active,   "Active",          t['green']),
        (mc3, paused,   "Paused",          t['accent']),
        (mc4, next_run, "Next Run",        t['purple']),
    ]:
        with col:
            col.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:0.9rem 1.1rem;border-top:3px solid {clr};">
  <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;
       letter-spacing:0.06em;color:{t['text2']};margin-bottom:0.2rem;">{lbl}</div>
  <div style="font-size:1.3rem;font-weight:700;color:{t['text']};
       word-break:break-all;line-height:1.2;">{val}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="height:0.75rem"></div>', unsafe_allow_html=True)

    # Active Schedules Table
    if scheds:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem;margin-bottom:0.75rem;overflow-x:auto;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};
       margin-bottom:0.75rem;display:flex;align-items:center;gap:7px;">
    {icon('list-checks',14,t['accent'])} Scheduled Jobs
  </div>
""", unsafe_allow_html=True)

        th_style = (f"text-align:left;padding:0.45rem 0.7rem;font-size:0.67rem;"
                    f"font-weight:600;color:{t['muted']};text-transform:uppercase;"
                    f"letter-spacing:0.06em;border-bottom:1px solid {t['border']};")
        headers = ["Scraper", "URL", "Query", "Frequency", "Next Run", "Format", "Status"]
        th_html = "".join(f'<th style="{th_style}">{h}</th>' for h in headers)
        rows_html = ""
        td = (f"padding:0.55rem 0.7rem;border-bottom:1px solid {t['border']};"
              f"font-size:0.8rem;color:{t['text']};vertical-align:middle;")
        for s in scheds:
            sbg, sfg = STATUS_COLORS.get(s["status"], ("transparent", t["text2"]))
            scol = SCRAPER_COLORS.get(s["scraper"], t["accent"])
            q_display = s.get("query", "—")
            if len(q_display) > 40:
                q_display = q_display[:37] + "..."
            rows_html += f"""
<tr>
  <td style="{td}">
    <span style="display:inline-flex;align-items:center;gap:5px;">
      <span style="width:8px;height:8px;border-radius:50%;background:{scol};flex-shrink:0;"></span>
      <span style="font-weight:600;">{s['scraper']}</span>
    </span>
  </td>
  <td style="{td}font-family:monospace;font-size:0.72rem;color:{t['text2']};
       max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
    {s['url']}</td>
  <td style="{td}font-size:0.74rem;color:{t['text2']};
       max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
       title="{s.get('query', '')}">
    {q_display}</td>
  <td style="{td}">{s['frequency']}</td>
  <td style="{td}color:{t['text2']};">{s['next_run']}</td>
  <td style="{td}">
    <span style="background:rgba(59,130,246,0.14);color:{t['blue']};padding:2px 7px;
          border-radius:20px;font-size:0.67rem;font-weight:600;">{s['format']}</span>
  </td>
  <td style="{td}">
    <span style="background:{sbg};color:{sfg};padding:2px 8px;border-radius:20px;
          font-size:0.67rem;font-weight:600;">{s['status']}</span>
  </td>
</tr>"""
        st.markdown(f"""
<table style="width:100%;border-collapse:collapse;">
  <thead><tr>{th_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

        # Action buttons per schedule
        for s in scheds:
            ac1, ac2, _ = st.columns([1, 1, 5])
            with ac1:
                if s["status"] == "Active":
                    if st.button("Pause", key=f"pause_{s['id']}", use_container_width=True):
                        job = job_registry.jobs.get(s["id"])
                        if job:
                            try:
                                scheduler_manager.remove_job(job.job_id)
                            except Exception:
                                pass
                            job.is_active = False
                        st.rerun()
                else:
                    if st.button("Resume", key=f"resume_{s['id']}", use_container_width=True):
                        job = job_registry.jobs.get(s["id"])
                        if job and not job.is_active:
                            job.is_active = True
                            scheduler_manager.add_job(job)
                        st.rerun()
            with ac2:
                if st.button("Delete", key=f"del_{s['id']}", use_container_width=True):
                    job = job_registry.jobs.get(s["id"])
                    if job and job.is_active:
                        try:
                            scheduler_manager.remove_job(job.job_id)
                        except Exception:
                            pass
                    job_registry.remove_job(s["id"])
                    st.rerun()

    else:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:2rem;text-align:center;margin-bottom:0.75rem;">
  <div style="font-size:0.85rem;color:{t['muted']};">No schedules yet. Create one above.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f'<div style="height:0.75rem"></div>', unsafe_allow_html=True)

    # Upcoming Runs
    active_scheds = [s for s in scheds if s["status"] == "Active"]

    if active_scheds:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem;margin-bottom:1rem;">
  <div style="font-size:0.92rem;font-weight:700;color:{t['text']};
       margin-bottom:0.85rem;display:flex;align-items:center;gap:7px;">
    {icon('clock',14,t['accent'])} Upcoming Runs
    <span style="font-size:0.72rem;font-weight:400;color:{t['muted']};margin-left:4px;">
      Next scheduled executions for active jobs
    </span>
  </div>
""", unsafe_allow_html=True)

        # Build upcoming runs for next 3 occurrences per active schedule
        upcoming = []
        now = datetime.now()
        for s in active_scheds:
            interval = FREQ_INTERVALS.get(s["frequency"], timedelta(days=1))
            try:
              job = job_registry.jobs.get(s["id"])
              aps_job = scheduler_manager.scheduler.get_job(job.job_id) if job else None
              if aps_job and aps_job.next_run_time:
                next_dt = aps_job.next_run_time
              else:
                next_dt = datetime.strptime(f"{s['start_date']} {s['start_time']}", "%Y-%m-%d %H:%M")
            except Exception:
              next_dt = now + interval
            for i in range(3):  # next 3 runs per schedule
                run_dt = next_dt + interval * i
                upcoming.append({
                    "scraper": s["scraper"],
                    "url": s["url"],
                    "query": s.get("query", "—"),
                    "run_at": run_dt,
                    "frequency": s["frequency"],
                    "format": s["format"],
                })
        # Sort by run time
        upcoming.sort(key=lambda x: x["run_at"])
        upcoming = upcoming[:15]  # show max 15

        th_s = (f"text-align:left;padding:0.4rem 0.7rem;font-size:0.67rem;font-weight:600;"
                f"color:{t['muted']};text-transform:uppercase;letter-spacing:0.06em;"
                f"border-bottom:1px solid {t['border']};")
        th_html = "".join(f'<th style="{th_s}">{h}</th>'
                          for h in ["Scraper", "URL", "Query", "Scheduled At", "Frequency", "Format"])

        rows_html = ""
        today = date.today()
        for run in upcoming:
            run_date = run["run_at"].date()
            is_today = run_date == today
            date_str = run["run_at"].strftime("%Y-%m-%d %H:%M")
            date_lbl = f"Today {run['run_at'].strftime('%H:%M')}" if is_today else date_str
            date_clr = t['accent'] if is_today else t['text2']
            scol = SCRAPER_COLORS.get(run["scraper"], t["accent"])
            url_s = run["url"][:35] + ("..." if len(run["url"]) > 35 else "")
            q_s = run.get("query", "—")
            if len(q_s) > 30:
                q_s = q_s[:27] + "..."
            td = f"padding:0.5rem 0.7rem;border-bottom:1px solid {t['border']};font-size:0.79rem;"
            rows_html += f"""<tr>
<td style="{td}">
  <span style="display:inline-flex;align-items:center;gap:5px;">
    <span style="width:7px;height:7px;border-radius:50%;background:{scol};flex-shrink:0;"></span>
    <span style="font-weight:600;color:{t['text']};">{run['scraper']}</span>
  </span>
</td>
<td style="{td}font-family:monospace;font-size:0.71rem;color:{t['text2']};">{url_s}</td>
<td style="{td}font-size:0.73rem;color:{t['text2']};" title="{run.get('query', '')}">{q_s}</td>
<td style="{td}color:{date_clr};font-weight:{'700' if is_today else '400'};">{date_lbl}</td>
<td style="{td}color:{t['text2']};">{run['frequency']}</td>
<td style="{td}">
  <span style="background:rgba(59,130,246,0.14);color:{t['blue']};padding:2px 7px;
        border-radius:20px;font-size:0.67rem;font-weight:600;">{run['format']}</span>
</td>
</tr>"""

        st.markdown(f"""
<div style="overflow-x:auto;">
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr>{th_html}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
</div>
""", unsafe_allow_html=True)

    else:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1.5rem;text-align:center;margin-bottom:1rem;">
  <div style="font-size:0.85rem;color:{t['muted']};">
    No active schedules. Create a schedule above to see upcoming runs.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
