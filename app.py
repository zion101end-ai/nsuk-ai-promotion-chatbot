import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import calendar

import pandas as pd
import streamlit as st
import plotly.express as px
from fpdf import FPDF

# ============================================================
# NSUK AI PROMOTION INTERVIEW CHATBOT
# Home page styled to closely follow the user's supplied
# dashboard reference. All dashboard records are live DB data.
# ============================================================

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
LOGO = ASSETS / "nsuk_logo.png"
ROBOT = ASSETS / "nsuk_robot.png"
DB = Path(os.getenv("DB_PATH", str(BASE / "nsuk_interviews.db")))
ADMIN_PASSWORD = os.getenv("NSUK_ADMIN_PASSWORD", "")

st.set_page_config(
    page_title="NSUK AI Promotion Interview Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#061638"
NAVY2 = "#09295D"
BLUE = "#075BC8"
GREEN = "#07843D"
GOLD = "#F2C500"
BG = "#F2F5FA"
INK = "#081D49"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: Inter, Arial, sans-serif; }}
    .stApp {{ background:{BG}; color:{INK}; }}
    [data-testid="stSidebar"] {{
        background:linear-gradient(180deg,#031433 0%,#082451 76%,#031433 100%);
        border-right:1px solid #173B70;
    }}
    [data-testid="stSidebar"] * {{ color:#fff !important; }}
    [data-testid="stSidebar"] .stButton button {{
        width:100%; text-align:left; color:#fff !important;
        background:transparent !important; border:0 !important;
        border-radius:9px !important; min-height:43px;
        padding-left:14px; font-weight:600;
    }}
    [data-testid="stSidebar"] .stButton button:hover {{
        background:#075BC8 !important;
    }}
    .side-brand {{text-align:center;font-weight:800;line-height:1.4;font-size:17px;margin:8px 0 22px}}
    .side-powered {{border-top:1px solid #52709C;padding-top:18px;margin-top:24px;font-size:13px}}
    .top-header {{
        background:linear-gradient(90deg,#061638,#09295D);
        color:#fff;border-bottom:5px solid {GOLD};border-radius:0 0 3px 3px;
        padding:12px 20px 10px;text-align:center;margin:-1rem -1rem 0.7rem;
    }}
    .top-header h1 {{color:#fff!important;font-size:clamp(18px,2.3vw,30px);margin:0;font-weight:800;letter-spacing:.3px}}
    .top-header p {{color:{GOLD};font-style:italic;font-weight:700;margin:0;font-size:15px}}
    .user-chip {{
        background:#09295D;border:1px solid #1A4B8C;border-radius:25px;
        padding:8px 13px;color:white;text-align:center;font-size:13px;font-weight:600;
    }}
    .hero-wrap {{
        background:linear-gradient(100deg,rgba(255,255,255,.98) 0%,rgba(239,246,255,.92) 58%,rgba(218,235,255,.72) 100%);
        border:1px solid #D8E3F1;border-radius:14px;padding:24px 22px;
        min-height:350px;box-shadow:0 3px 14px rgba(4,25,61,.08);
    }}
    .hero-kicker {{font-size:22px;font-weight:800;color:{INK};margin:0 0 6px}}
    .hero-title {{font-size:clamp(28px,3.2vw,46px);font-weight:800;line-height:1.08;color:{INK};margin:0 0 14px}}
    .hero-title span {{color:{GREEN}}}
    .hero-copy {{font-size:17px;line-height:1.45;color:#10213F;max-width:560px}}
    .category-card {{
        background:rgba(255,255,255,.96);border:1px solid #D8E3F1;
        border-radius:14px;padding:17px 13px;min-height:220px;
        box-shadow:0 3px 12px rgba(4,25,61,.07);text-align:center;
    }}
    .category-icon {{
        width:76px;height:76px;border-radius:50%;display:flex;align-items:center;
        justify-content:center;margin:0 auto 10px;color:white;font-size:34px;font-weight:800;
    }}
    .category-title {{font-size:15px;font-weight:800;color:#08152F;margin-bottom:7px}}
    .category-desc {{font-size:12px;min-height:36px;color:#25344C}}
    .white-panel {{
        background:white;border:1px solid #DCE4EF;border-radius:14px;
        padding:12px;box-shadow:0 2px 10px rgba(4,25,61,.06);margin-bottom:12px;
    }}
    .panel-heading {{
        background:linear-gradient(90deg,#061638,#09295D);color:white;
        padding:12px 15px;border-radius:9px;font-size:18px;font-weight:800;
        margin-bottom:10px;
    }}
    .metric-card {{
        border-radius:12px;padding:15px 8px;text-align:center;
        min-height:112px;border:1px solid #E1E7F0;
    }}
    .metric-value {{font-size:28px;font-weight:800;color:#071A3C;line-height:1.3}}
    .metric-label {{font-size:12px;color:#14233D;font-weight:600}}
    .section-title {{font-size:22px;font-weight:800;color:{INK};margin:8px 0 12px}}
    .figure-tag {{
        display:inline-block;background:#E8F0FF;color:#09295D;
        border:1px solid #C8D9F3;border-radius:18px;padding:4px 10px;
        font-size:10px;font-weight:800;margin-bottom:8px;letter-spacing:.3px;
    }}
    .form-card {{background:white;border:1px solid #DCE4EF;border-radius:12px;padding:18px}}
    .flow-step {{
        background:#fff;border:1px solid #DCE4EF;border-left:5px solid {BLUE};
        border-radius:9px;padding:12px 15px;margin:7px 0;
    }}
    .stButton>button,.stDownloadButton>button {{
        background:{BLUE};color:#fff;border:0;border-radius:8px;
        font-weight:700;min-height:42px;
    }}
    .stButton>button:hover,.stDownloadButton>button:hover {{background:{GREEN};color:#fff}}
    div[data-testid="stForm"] {{
        background:#fff;padding:16px;border:1px solid #DCE4EF;border-radius:12px;
    }}
    [data-testid="stDataFrame"] {{background:#fff;border-radius:9px}}
    .footer-bar {{
        background:#061638;color:white;border-top:3px solid {GOLD};
        padding:12px 15px;text-align:center;border-radius:4px;font-size:12px;
        margin-top:18px;
    }}
    @media(max-width:900px) {{
        .top-header {{margin-left:-.5rem;margin-right:-.5rem}}
        .hero-wrap {{padding:16px;min-height:unset}}
    }}
    #MainMenu,footer {{visibility:hidden}}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------- Question banks --------------------------

ACADEMIC = [
    ("Teaching and Learning", "How do you contribute to teaching and learning? Discuss your teaching methods, student support and academic impact.", ["teaching","learning","student","curriculum","lecture","pedagogy"]),
    ("Research and Scholarship", "What are your major research contributions, and how have they influenced your field?", ["research","publication","journal","scholarship","grant","conference"]),
    ("Leadership and Service", "Describe your administrative, committee or university service contributions and results.", ["leadership","committee","service","management","coordination","team"]),
    ("Ethics and Integrity", "How do you demonstrate professional ethics, fairness, academic integrity and compliance?", ["ethics","integrity","fairness","policy","regulation","compliance"]),
    ("Professional Development and Vision", "What professional development have you undertaken and what is your vision?", ["development","training","workshop","vision","plan","professional"]),
]
NON_ACADEMIC = [
    ("Professional Competence", "Describe your responsibilities and how your work has improved efficiency and service quality.", ["responsibility","efficiency","service","quality","process","performance"]),
    ("Problem-Solving", "Describe a difficult administrative or technical problem you resolved and the outcome.", ["problem","solution","resolved","challenge","improvement","service"]),
    ("Leadership and Teamwork", "How have you supported teamwork, supervised colleagues or coordinated unit activities?", ["teamwork","leadership","supervision","coordination","staff","communication"]),
    ("Ethics and Accountability", "How do you protect confidential information, follow procedures and show accountability?", ["confidential","ethics","accountability","procedure","policy","integrity"]),
    ("Professional Development and Vision", "What training or skills have you developed and what improvements would you introduce?", ["training","skills","development","improvement","plan","innovation"]),
]

# ------------------------------ Database ------------------------------

def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=30)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS interviews(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_category TEXT NOT NULL, full_name TEXT NOT NULL,
            staff_id TEXT NOT NULL, department TEXT NOT NULL,
            email TEXT NOT NULL, phone TEXT,
            responses_json TEXT NOT NULL, total_score REAL NOT NULL,
            outcome TEXT NOT NULL, interview_date TEXT NOT NULL,
            review_status TEXT DEFAULT 'Pending Review',
            reviewer_comments TEXT DEFAULT '')""")
        con.commit()

def records():
    with db() as con:
        return con.execute("SELECT * FROM interviews ORDER BY id DESC").fetchall()

def record_by_id(rid):
    with db() as con:
        return con.execute("SELECT * FROM interviews WHERE id=?", (rid,)).fetchone()

def report_records(staff_id, email):
    with db() as con:
        return con.execute(
            "SELECT * FROM interviews WHERE lower(staff_id)=lower(?) AND lower(email)=lower(?) ORDER BY id DESC",
            (staff_id.strip(), email.strip())
        ).fetchall()

def save_interview(profile, items, total, verdict):
    with db() as con:
        cur = con.execute("""INSERT INTO interviews
            (staff_category,full_name,staff_id,department,email,phone,responses_json,
             total_score,outcome,interview_date,review_status,reviewer_comments)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (profile["staff_category"],profile["full_name"],profile["staff_id"],
             profile["department"],profile["email"],profile["phone"],
             json.dumps(items, ensure_ascii=False),total,verdict,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Pending Review",""))
        con.commit()
        return cur.lastrowid

def update_review(rid, status, comments):
    with db() as con:
        con.execute("UPDATE interviews SET review_status=?,reviewer_comments=? WHERE id=?",
                    (status,comments,rid))
        con.commit()

init_db()

# -------------------------- Assessment logic --------------------------

def bank_for(category):
    return ACADEMIC if category == "Academic Staff" else NON_ACADEMIC

def score_answer(answer, keywords):
    text = (answer or "").strip().lower()
    if len(text) < 15:
        return 0.0, "Response is too short for assessment."
    hits = sum(1 for word in keywords if word in text)
    coverage = min(hits / max(len(keywords) * 0.4, 1), 1.0)
    length = min(len(text.split()) / 40, 1.0)
    mark = round((0.60 * coverage + 0.40 * length) * 20, 1)
    return mark, f"{hits}/{len(keywords)} keywords matched; {len(text.split())} words."

def assess(category, answers):
    items, total = [], 0.0
    for (area, question, keywords), answer in zip(bank_for(category), answers):
        mark, note = score_answer(answer, keywords)
        total += mark
        items.append({"area":area,"question":question,"answer":answer,"score":mark,"note":note})
    return items, round(total, 1)

def verdict(score):
    if score >= 75: return "Highly Recommended"
    if score >= 50: return "Recommended"
    return "Deferred / Further Review Required"

# ------------------------------ PDF report -----------------------------

def safe_pdf(value):
    return str(value or "").encode("latin-1", "replace").decode("latin-1")

def make_pdf(row, items):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica","B",16)
    pdf.cell(0,10,"NASARAWA STATE UNIVERSITY, KEFFI",ln=1,align="C")
    pdf.set_font("Helvetica","B",12)
    pdf.multi_cell(0,8,"STAFF PROMOTION INTERVIEW ASSESSMENT REPORT",align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica","B",11)
    pdf.cell(0,7,"CANDIDATE INFORMATION",ln=1)
    pdf.set_font("Helvetica","",10)
    for label,key in [("Name","full_name"),("Staff ID","staff_id"),("Category","staff_category"),
                      ("Department / Unit","department"),("Email","email"),("Interview Date","interview_date"),
                      ("Total Score","total_score"),("Preliminary Outcome","outcome"),("Review Status","review_status")]:
        pdf.multi_cell(0,6,f"{label}: {safe_pdf(row[key])}")
    pdf.ln(4)
    pdf.set_font("Helvetica","B",11)
    pdf.cell(0,7,"ASSESSMENT DETAILS",ln=1)
    for i,item in enumerate(items,1):
        pdf.set_font("Helvetica","B",10)
        pdf.multi_cell(0,6,f"{i}. {safe_pdf(item['area'])} - {item['score']}/20")
        pdf.set_font("Helvetica","",9)
        pdf.multi_cell(0,5,"Question: "+safe_pdf(item["question"]))
        pdf.multi_cell(0,5,"Response: "+safe_pdf(item["answer"]))
        pdf.multi_cell(0,5,"Scoring note: "+safe_pdf(item["note"]))
        pdf.ln(2)
    if row["reviewer_comments"]:
        pdf.set_font("Helvetica","B",10); pdf.cell(0,7,"REVIEWER COMMENTS",ln=1)
        pdf.set_font("Helvetica","",9); pdf.multi_cell(0,5,safe_pdf(row["reviewer_comments"]))
    pdf.ln(4)
    pdf.set_font("Helvetica","I",8)
    pdf.multi_cell(0,5,"This is a preliminary rule-based decision-support assessment, not an official university promotion decision. Final decisions remain with the authorised university committee.")
    return bytes(pdf.output())

# ---------------------------- Session state ----------------------------

defaults = {
    "page":"Home", "category":"", "profile":{}, "answers":[""]*5,
    "result_id":None, "admin_ok":False, "dashboard_filter":"All",
}
for key,value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def go(page):
    st.session_state.page = page
    st.rerun()

def figure(number, title):
    st.markdown(f'<div class="figure-tag">FIGURE {number} · {title.upper()}</div>', unsafe_allow_html=True)

def df_records():
    rows = records()
    return pd.DataFrame([dict(x) for x in rows]) if rows else pd.DataFrame()

# ------------------------------- Sidebar -------------------------------

with st.sidebar:
    if LOGO.exists():
        st.image(str(LOGO), use_container_width=True)
    else:
        st.markdown("## 🎓 NSUK")
    st.markdown('<div class="side-brand">AI PROMOTION<br>INTERVIEW CHATBOT</div>', unsafe_allow_html=True)
    nav = [
        ("🏠  Home","Home"),
        ("☏  Start Interview","Staff Promotion Interview Module"),
        ("▥  Dashboard","Dashboard"),
        ("▤  My Reports","My Reports"),
        ("ⓘ  About NSUK","About NSUK"),
        ("ⓘ  Help","Help"),
    ]
    for label,destination in nav:
        if st.button(label, key="nav_"+destination, use_container_width=True):
            go(destination)
    st.markdown(
        '<div class="side-powered">🎓 &nbsp; Powered by<br>&nbsp;&nbsp;&nbsp;&nbsp; NSUK AI Solutions</div>',
        unsafe_allow_html=True,
    )
    st.caption("Prototype interface")

# ------------------------------- Top bar --------------------------------

current_page = st.session_state.page
active_name = st.session_state.profile.get("full_name", "Staff Portal")
top_left, top_right = st.columns([5,1.2])
with top_left:
    st.markdown(
        '<div class="top-header"><h1>NASARAWA STATE UNIVERSITY, KEFFI</h1>'
        '<p>Knowledge for Development</p></div>',
        unsafe_allow_html=True,
    )
with top_right:
    st.markdown(f'<div class="user-chip">👤 {active_name}　⌄</div>', unsafe_allow_html=True)
    if st.button("Logout", key="top_logout", use_container_width=True):
        st.session_state.profile = {}
        st.session_state.category = ""
        st.session_state.answers = [""]*5
        st.session_state.result_id = None
        go("Home")

# ============================================================
# FIGURE 4.1 — HOME / PORTAL DASHBOARD
# ============================================================
if current_page == "Home":
    figure("4.1","Portal Home Interface")
    hero_left, hero_right = st.columns([1.55,1], gap="medium")
    with hero_left:
        st.markdown(
            f"""
            <div class="hero-wrap">
                <p class="hero-kicker">Welcome to the</p>
                <h1 class="hero-title"><span>AI</span> PROMOTION<br>INTERVIEW CHATBOT</h1>
                <p class="hero-copy">Your smart assistant for a transparent,
                structured and efficient promotion interview process.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        start_col, dash_col = st.columns(2)
        with start_col:
            if st.button("▶  Start Interview", use_container_width=True):
                go("Staff Promotion Interview Module")
        with dash_col:
            if st.button("▥  View Dashboard", use_container_width=True):
                go("Dashboard")
    with hero_right:
        st.markdown('<div class="white-panel">', unsafe_allow_html=True)
        st.markdown("### Choose Your Category")
        st.write("Select the option that best describes you:")
        cat_a, cat_b = st.columns(2)
        with cat_a:
            st.markdown(
                '<div class="category-card"><div class="category-icon" style="background:#124A9B">🎓</div>'
                '<div class="category-title">Academic Staff</div><div class="category-desc">For academic staff (lecturers and researchers)</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Select Academic", key="home_select_academic", use_container_width=True):
                st.session_state.category = "Academic Staff"
                go("Staff Biodata Registration Form")
        with cat_b:
            st.markdown(
                '<div class="category-card"><div class="category-icon" style="background:#07843D">👥</div>'
                '<div class="category-title">Non-Academic Staff</div><div class="category-desc">For administrative staff</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Select Non-Academic", key="home_select_nonacademic", use_container_width=True):
                st.session_state.category = "Non-Academic Staff"
                go("Staff Biodata Registration Form")
        st.markdown('</div>', unsafe_allow_html=True)

    # Dashboard overview below the hero: only real submitted records are shown.
    data = df_records()
    st.markdown('<div class="white-panel">', unsafe_allow_html=True)
    left_panel, right_panel = st.columns([1,1.35], gap="small")
    with left_panel:
        st.markdown('<div class="panel-heading">▥ &nbsp; Interview Dashboard</div>', unsafe_allow_html=True)
        total = len(data)
        approved = int((data.review_status == "Approved").sum()) if total else 0
        pending = int((data.review_status.isin(["Pending Review","Under Review"])).sum()) if total else 0
        average = float(data.total_score.mean()) if total else 0.0
        cards = st.columns(2)
        metric_specs = [
            (total,"Total Interviews","#E8F1FF","👥"),
            (approved,"Approved","#E4F8E9","✔"),
            (pending,"Pending Review","#FFF5D9","◷"),
            (f"{average:.1f}%","Average Score","#F0E9FF","★"),
        ]
        for col,(value,label,color,icon) in zip(cards*2,metric_specs):
            col.markdown(
                f'<div class="metric-card" style="background:{color}"><div style="font-size:22px">{icon}</div>'
                f'<div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )
        if not data.empty:
            data["month"] = pd.to_datetime(data["interview_date"], errors="coerce").dt.to_period("M").astype(str)
            monthly = data.groupby("month",as_index=False).agg(average_score=("total_score","mean"))
            monthly["month_label"] = monthly["month"].apply(
                lambda value: datetime.strptime(value,"%Y-%m").strftime("%b") if value and value!="NaT" else "Unknown"
            )
            chart = px.line(monthly,x="month_label",y="average_score",markers=True,
                            title="Performance Overview",range_y=[0,100])
            chart.update_traces(line_width=3,marker_size=9)
            chart.update_layout(height=235,margin=dict(l=10,r=10,t=45,b=10),
                                paper_bgcolor="white",plot_bgcolor="white",
                                yaxis_title="Average score",xaxis_title="")
            st.plotly_chart(chart,use_container_width=True)
        else:
            st.markdown("**Performance Overview**")
            st.info("The performance chart will appear after interviews are submitted.")
    with right_panel:
        head_left, head_right = st.columns([4,1])
        with head_left:
            st.markdown('<div class="panel-heading">📁 &nbsp; Recent Interviews</div>', unsafe_allow_html=True)
        with head_right:
            if st.button("View All →",key="view_all_recent",use_container_width=True):
                go("Dashboard")
        if data.empty:
            st.info("No interview submissions yet. Recent records will appear here.")
        else:
            recent = data.head(7).copy()
            recent.insert(0,"S/N",range(1,len(recent)+1))
            recent["Category"] = recent["staff_category"].replace({
                "Academic Staff":"Academic","Non-Academic Staff":"Non-Academic"
            })
            recent["Date"] = pd.to_datetime(recent["interview_date"],errors="coerce").dt.strftime("%d/%m/%Y")
            display = recent[["S/N","full_name","Category","total_score","review_status","Date"]].rename(
                columns={"full_name":"Name","total_score":"Score","review_status":"Status"}
            )
            st.dataframe(display,use_container_width=True,hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# FIGURE 4.2 — STAFF PROMOTION INTERVIEW MODULE
# ============================================================
elif current_page == "Staff Promotion Interview Module":
    figure("4.2","Staff Promotion Interview Module")
    st.markdown('<div class="section-title">Staff Promotion Interview Module</div>',unsafe_allow_html=True)
    st.write("Choose the category that best describes your current appointment.")
    a,b = st.columns(2)
    with a:
        st.markdown('<div class="white-panel"><h2>🎓 Academic Staff</h2><p>For lecturers, researchers and academic employees.</p><b>Focus areas:</b> teaching, research, service, ethics and development.</div>',unsafe_allow_html=True)
        if st.button("Select Academic Staff",use_container_width=True):
            st.session_state.category="Academic Staff"; go("Staff Biodata Registration Form")
    with b:
        st.markdown('<div class="white-panel"><h2>👥 Non-Academic Staff</h2><p>For administrative, technical and other non-academic employees.</p><b>Focus areas:</b> competence, problem-solving, teamwork, accountability and development.</div>',unsafe_allow_html=True)
        if st.button("Select Non-Academic Staff",use_container_width=True):
            st.session_state.category="Non-Academic Staff"; go("Staff Biodata Registration Form")

# ============================================================
# FIGURE 4.3 — STAFF BIODATA REGISTRATION FORM
# ============================================================
elif current_page == "Staff Biodata Registration Form":
    figure("4.3","Staff Biodata Registration Form")
    st.markdown('<div class="section-title">Staff Biodata Registration Form</div>',unsafe_allow_html=True)
    if not st.session_state.category:
        st.warning("Select a staff category first.")
        if st.button("Choose Category"): go("Staff Promotion Interview Module")
    else:
        st.info(f"Selected category: **{st.session_state.category}**")
        old = st.session_state.profile
        with st.form("biodata_form"):
            c1,c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *",old.get("full_name",""))
                staff_id = st.text_input("Staff ID / Personnel Number *",old.get("staff_id",""))
                department = st.text_input("Department / Unit *",old.get("department",""))
            with c2:
                email = st.text_input("Email Address *",old.get("email",""))
                phone = st.text_input("Phone Number",old.get("phone",""))
                st.text_input("Staff Category",st.session_state.category,disabled=True)
            submitted = st.form_submit_button("Continue to Interview")
        if submitted:
            if not all([name.strip(),staff_id.strip(),department.strip(),email.strip()]):
                st.error("Complete all required fields.")
            elif "@" not in email or "." not in email.rsplit("@",1)[-1]:
                st.error("Enter a valid email address.")
            else:
                st.session_state.profile = {
                    "full_name":name.strip(),"staff_id":staff_id.strip(),
                    "department":department.strip(),"email":email.strip(),
                    "phone":phone.strip(),"staff_category":st.session_state.category
                }
                st.session_state.answers=[""]*5
                go("Interactive Interview Questions")
        if st.button("Back to Category"): go("Staff Promotion Interview Module")

# ============================================================
# FIGURE 4.4 — INTERACTIVE INTERVIEW QUESTIONS
# ============================================================
elif current_page == "Interactive Interview Questions":
    figure("4.4","Interactive Interview Questions")
    st.markdown('<div class="section-title">Interactive Staff Promotion Interview Questions</div>',unsafe_allow_html=True)
    if not st.session_state.profile:
        st.warning("Complete the biodata form before continuing.")
        if st.button("Open Biodata Form"): go("Staff Biodata Registration Form")
    else:
        bank = bank_for(st.session_state.category)
        st.caption("Five questions • 20 marks each • Total 100 marks")
        with st.form("question_form"):
            answers=[]
            for i,(area,question,keywords) in enumerate(bank):
                st.markdown(f"**Question {i+1} of 5 — {area}**")
                st.info(question)
                answers.append(st.text_area(f"Your response — {area}",value=st.session_state.answers[i],
                                            height=125,key=f"answer_{i}"))
            submitted=st.form_submit_button("Review My Answers")
        if submitted:
            st.session_state.answers=answers
            go("Review Answers")
        if st.button("Back to Biodata"): go("Staff Biodata Registration Form")

elif current_page == "Review Answers":
    st.markdown('<div class="section-title">Review Your Answers</div>',unsafe_allow_html=True)
    bank=bank_for(st.session_state.category)
    for i,((area,question,keywords),answer) in enumerate(zip(bank,st.session_state.answers),1):
        with st.expander(f"{i}. {area}",expanded=(i==1)):
            st.caption(question); st.write(answer or "_No answer entered._")
    left,right=st.columns(2)
    with left:
        if st.button("Edit Answers",use_container_width=True): go("Interactive Interview Questions")
    with right:
        if st.button("Submit Answers for Assessment",use_container_width=True):
            items,total=assess(st.session_state.category,st.session_state.answers)
            rid=save_interview(st.session_state.profile,items,total,verdict(total))
            st.session_state.result_id=rid
            go("Assessment Result and Preliminary Verdict")

# ============================================================
# FIGURE 4.5 — ASSESSMENT RESULT AND PRELIMINARY VERDICT
# ============================================================
elif current_page == "Assessment Result and Preliminary Verdict":
    figure("4.5","Assessment Result and Preliminary Verdict")
    st.markdown('<div class="section-title">Staff Promotion Assessment Result and Preliminary Verdict</div>',unsafe_allow_html=True)
    row=record_by_id(st.session_state.result_id) if st.session_state.result_id else None
    if not row:
        st.warning("No result is selected.")
        if st.button("Home"): go("Home")
    else:
        items=json.loads(row["responses_json"])
        a,b,c=st.columns(3)
        a.metric("Total Score",f"{row['total_score']}/100")
        b.metric("Preliminary Outcome",row["outcome"])
        c.metric("Review Status",row["review_status"])
        st.progress(min(float(row["total_score"])/100,1))
        st.dataframe(pd.DataFrame([{"Assessment Area":x["area"],"Score":x["score"],"Maximum":20} for x in items]),
                     use_container_width=True,hide_index=True)
        st.warning("This is a preliminary rule-based assessment, not an official university promotion decision.")
        st.download_button("⬇ Download Assessment Report (PDF)",make_pdf(row,items),
                           f"NSUK_Assessment_{row['staff_id']}.pdf","application/pdf",use_container_width=True)
        if st.button("Return Home"):
            st.session_state.category="";st.session_state.profile={};st.session_state.answers=[""]*5
            st.session_state.result_id=None;go("Home")

# ============================================================
# FIGURE 4.6 — SAMPLE ASSESSMENT REPORT / MY REPORTS
# ============================================================
elif current_page == "My Reports":
    figure("4.6","Sample Assessment Report")
    st.markdown('<div class="section-title">My Assessment Reports</div>',unsafe_allow_html=True)
    st.write("Enter the staff ID and registered email used for the interview.")
    with st.form("report_search"):
        sid=st.text_input("Staff ID / Personnel Number")
        email=st.text_input("Registered Email")
        find=st.form_submit_button("Find Reports")
    if find:
        if not sid.strip() or not email.strip():
            st.error("Enter both staff ID and email.")
        else:
            matches=report_records(sid,email)
            if not matches: st.error("No matching reports found.")
            for item in matches:
                with st.expander(f"Report #{item['id']} — {item['interview_date']}"):
                    st.write(f"**Name:** {item['full_name']}")
                    st.write(f"**Score:** {item['total_score']}/100")
                    st.write(f"**Preliminary Outcome:** {item['outcome']}")
                    st.write(f"**Review Status:** {item['review_status']}")
                    st.download_button("Download PDF Report",make_pdf(item,json.loads(item["responses_json"])),
                                       f"NSUK_Report_{item['staff_id']}_{item['id']}.pdf",
                                       "application/pdf",key=f"report_{item['id']}")

# ------------------------------- Dashboard ------------------------------

elif current_page == "Dashboard":
    st.markdown('<div class="section-title">Interview Dashboard</div>',unsafe_allow_html=True)
    data=df_records()
    if data.empty:
        st.info("No submitted interviews yet. Dashboard statistics will appear when records are saved.")
    else:
        a,b,c,d=st.columns(4)
        a.metric("Total Interviews",len(data))
        b.metric("Academic Staff",int((data.staff_category=="Academic Staff").sum()))
        c.metric("Non-Academic Staff",int((data.staff_category=="Non-Academic Staff").sum()))
        d.metric("Average Score",f"{data.total_score.mean():.1f}%")
        l,r=st.columns(2)
        with l:
            counts=data.groupby("staff_category").size().reset_index(name="Interviews")
            st.plotly_chart(px.bar(counts,x="staff_category",y="Interviews",title="Interviews by Staff Category"),use_container_width=True)
        with r:
            st.plotly_chart(px.histogram(data,x="total_score",nbins=10,title="Assessment Score Distribution"),use_container_width=True)
        st.markdown("### Recent Interviews")
        st.dataframe(data[["id","full_name","staff_category","department","total_score","outcome","review_status","interview_date"]].head(30),
                     use_container_width=True,hide_index=True)
        st.download_button("Export Records as CSV",data.to_csv(index=False).encode("utf-8"),
                           "nsuk_interviews.csv","text/csv")

# ============================================================
# FIGURE 4.7 — CHATBOT WORKFLOW
# ============================================================
elif current_page == "Chatbot Workflow":
    figure("4.7","Chatbot Workflow")
    st.markdown('<div class="section-title">Workflow of the AI Promotion Interview Chatbot</div>',unsafe_allow_html=True)
    steps=[
        ("1","Open Portal","Staff member opens the NSUK chatbot home page."),
        ("2","Select Category","Academic or non-academic staff category is selected."),
        ("3","Enter Biodata","Staff member completes the biodata form."),
        ("4","Answer Questions","The system displays five category-specific questions."),
        ("5","Review Answers","Staff member checks responses before submission."),
        ("6","Assess Responses","Rule-based keyword and answer-length scoring is applied."),
        ("7","Display Result","The total score and preliminary verdict are displayed."),
        ("8","Generate Report","The PDF assessment report is generated and can be retrieved."),
        ("9","Human Review","An authorised reviewer checks the submission and records a review status."),
    ]
    for number,title,description in steps:
        st.markdown(f'<div class="flow-step"><b>{number}. {title}</b><br>{description}</div>',unsafe_allow_html=True)
        if number!="9": st.markdown("<div style='text-align:center;color:#07843D;font-size:20px'>↓</div>",unsafe_allow_html=True)
    st.info("The current assessment is rule-based. It is not a trained machine-learning model.")

# -------------------------------- About ---------------------------------

elif current_page == "About NSUK":
    st.markdown('<div class="section-title">About NSUK and the Project</div>',unsafe_allow_html=True)
    a,b=st.columns([1,2])
    with a:
        if LOGO.exists(): st.image(str(LOGO),use_container_width=True)
    with b:
        st.markdown("### Nasarawa State University, Keffi")
        st.write("This prototype supports a structured staff promotion interview process for academic and non-academic staff.")
        st.write("It collects biodata, presents interview questions, calculates a preliminary rule-based assessment, stores records and generates reports.")
    st.warning("The system does not replace authorised university promotion procedures or committee decisions.")

# -------------------------------- Help ----------------------------------

elif current_page == "Help":
    st.markdown('<div class="section-title">Help and User Guide</div>',unsafe_allow_html=True)
    help_items=[
        ("How do I start?","Select Start Interview or choose a staff category from the home page, then complete the biodata form."),
        ("How many questions are asked?","The current prototype presents five questions for the selected staff category."),
        ("Can I edit answers?","Yes. Review your responses and select Edit Answers before submitting."),
        ("How do I download a report?","Download it on the result page or use My Reports with your staff ID and registered email."),
        ("How is the score calculated?","The prototype uses keyword matching (60%) and answer length (40%) for each 20-mark question."),
        ("Does the chatbot make final promotion decisions?","No. Its result is preliminary decision support. The authorised university committee makes official decisions."),
    ]
    for title,body in help_items:
        with st.expander(title): st.write(body)

# ------------------------- Administrator review ------------------------

elif current_page == "Admin Review":
    st.markdown('<div class="section-title">Administrator / Human Review</div>',unsafe_allow_html=True)
    if not ADMIN_PASSWORD:
        st.error("Admin access is disabled. Configure NSUK_ADMIN_PASSWORD in the deployment environment.")
    elif not st.session_state.admin_ok:
        with st.form("admin_login"):
            password=st.text_input("Administrator Password",type="password")
            login=st.form_submit_button("Sign In")
        if login:
            if password==ADMIN_PASSWORD:
                st.session_state.admin_ok=True;st.rerun()
            else: st.error("Incorrect password.")
    else:
        if st.button("Sign Out Administrator"):
            st.session_state.admin_ok=False;st.rerun()
        rows=records()
        if not rows: st.info("No interview records are available.")
        else:
            options={f"#{x['id']} | {x['full_name']} | {x['staff_id']}":x["id"] for x in rows}
            selected=st.selectbox("Select candidate record",list(options.keys()))
            row=record_by_id(options[selected])
            st.write(f"**Candidate:** {row['full_name']}")
            st.write(f"**Category:** {row['staff_category']}")
            st.write(f"**Department:** {row['department']}")
            st.write(f"**System score:** {row['total_score']}/100")
            with st.expander("View submitted responses"):
                for item in json.loads(row["responses_json"]):
                    st.markdown(f"**{item['area']} — {item['score']}/20**")
                    st.caption(item["question"]);st.write(item["answer"])
            statuses=["Pending Review","Under Review","Approved","Not Approved","Further Review Required"]
            current=row["review_status"]
            idx=statuses.index(current) if current in statuses else 0
            with st.form("review_update"):
                status=st.selectbox("Human review status",statuses,index=idx)
                comments=st.text_area("Reviewer comments",value=row["reviewer_comments"] or "")
                save=st.form_submit_button("Save Review")
            if save:
                update_review(row["id"],status,comments.strip())
                st.success("Review updated.");st.rerun()

st.markdown(
    '<div class="footer-bar"><i>Building a Smarter University Together</i><br>'
    '© Nasarawa State University, Keffi. All Rights Reserved.　|　'
    '<span style="color:#F2C500;font-style:italic">Knowledge for Development</span></div>',
    unsafe_allow_html=True,
)
