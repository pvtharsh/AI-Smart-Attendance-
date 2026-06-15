import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import cv2
import face_recognition
import numpy as np
from datetime import datetime
import time

st.set_page_config(page_title="NeuroAttend", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background-color:#0a0e17;background-image:linear-gradient(rgba(20,25,45,.85) 1px,transparent 1px),linear-gradient(90deg,rgba(20,25,45,.85) 1px,transparent 1px);background-size:40px 40px;}
section[data-testid="stSidebar"]{background-color:#0a0e17;border-right:1px solid #1f2940;}
section[data-testid="stSidebar"] *{color:#fff!important;}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label{background:rgba(20,25,45,.6);border-radius:10px;padding:12px 16px;margin-bottom:8px;transition:all .25s ease;border:1px solid #1f2940;}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover{background:rgba(0,229,255,.08);border:1px solid #00e5ff;box-shadow:0 0 16px rgba(0,229,255,.4);transform:translateX(4px);}
.neon-tag{font-family:'Orbitron',sans-serif;font-size:13px;color:#00e5ff;font-weight:700;letter-spacing:4px;text-transform:uppercase;text-shadow:0 0 10px rgba(0,229,255,.6);}
.neon-title{font-family:'Orbitron',sans-serif;font-size:42px;font-weight:900;color:#fff;margin-top:-2px;text-shadow:0 0 20px rgba(0,229,255,.25);}
.neon-subtitle{font-size:14px;color:#6b7a99;margin-top:8px;margin-bottom:30px;}
.cyl-card{border-radius:20px;padding:24px 16px;background:rgba(13,18,30,.9);display:flex;flex-direction:column;align-items:center;gap:10px;transition:transform .3s ease,box-shadow .3s ease;}
.cyl-card:hover{transform:translateY(-8px);}
.cyl-card-cyan{border:2px solid #00e5ff;box-shadow:0 0 28px rgba(0,229,255,.3),inset 0 0 20px rgba(0,229,255,.05);}
.cyl-card-magenta{border:2px solid #ff2e92;box-shadow:0 0 28px rgba(255,46,146,.3),inset 0 0 20px rgba(255,46,146,.05);}
.cyl-card-purple{border:2px solid #a855f7;box-shadow:0 0 28px rgba(168,85,247,.3),inset 0 0 20px rgba(168,85,247,.05);}
.icon-3d-cyan{font-size:44px;text-shadow:0 6px 0 #007799,0 12px 0 #004455,0 0 30px #00e5ff;}
.icon-3d-magenta{font-size:44px;text-shadow:0 6px 0 #990055,0 12px 0 #440022,0 0 30px #ff2e92;}
.icon-3d-purple{font-size:44px;text-shadow:0 6px 0 #661199,0 12px 0 #330055,0 0 30px #a855f7;}
.cylinder-wrap{position:relative;width:90px;height:170px;}
.cylinder-top{position:absolute;top:0;left:0;width:90px;height:26px;border-radius:50%;background:rgba(30,40,60,.85);}
.cylinder-top-shine{position:absolute;top:5px;left:14px;width:62px;height:10px;background:rgba(255,255,255,.18);border-radius:50%;}
.cylinder-body{position:absolute;left:0;top:13px;width:90px;height:144px;border-radius:0 0 14px 14px;overflow:hidden;background:rgba(0,0,0,.45);}
.cylinder-fill{position:absolute;bottom:0;left:0;width:100%;border-radius:0 0 12px 12px;}
.cylinder-fill-cyan{background:linear-gradient(180deg,#00e5ffaa 0%,#00b8cc 45%,#007799 100%);}
.cylinder-fill-magenta{background:linear-gradient(180deg,#ff2e92aa 0%,#cc1166 45%,#880044 100%);}
.cylinder-fill-purple{background:linear-gradient(180deg,#a855f7aa 0%,#8833dd 45%,#551199 100%);}
.wave-overlay{position:absolute;top:0;left:-50%;width:200%;height:22px;border-radius:40%;animation:wave-anim 2.2s linear infinite;opacity:.5;}
.wave-cyan{background:#00e5ff;} .wave-magenta{background:#ff2e92;} .wave-purple{background:#a855f7;}
@keyframes wave-anim{0%{transform:translateX(0) rotate(0deg);}100%{transform:translateX(25%) rotate(360deg);}}
.cylinder-border{position:absolute;left:0;top:13px;width:90px;height:144px;border-radius:0 0 14px 14px;border:2px solid;border-top:none;pointer-events:none;}
.cb-cyan{border-color:rgba(0,229,255,.6);} .cb-magenta{border-color:rgba(255,46,146,.6);} .cb-purple{border-color:rgba(168,85,247,.6);}
.cyl-value{font-family:'Orbitron',sans-serif;font-size:40px;font-weight:900;line-height:1;}
.cyl-value-cyan{color:#00e5ff;text-shadow:0 0 18px #00e5ff;} .cyl-value-magenta{color:#ff2e92;text-shadow:0 0 18px #ff2e92;} .cyl-value-purple{color:#a855f7;text-shadow:0 0 18px #a855f7;}
.cyl-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;font-family:'Orbitron',sans-serif;}
.cyl-label-cyan{color:#00e5ff;} .cyl-label-magenta{color:#ff2e92;} .cyl-label-purple{color:#a855f7;}
.neon-content-card{background:rgba(13,18,30,.7);border:1px solid #1f2940;border-radius:16px;padding:24px;margin-bottom:22px;transition:border-color .25s,box-shadow .25s;}
.neon-content-card:hover{border-color:#00e5ff60;box-shadow:0 0 25px rgba(0,229,255,.1);}
.neon-card-heading{font-family:'Orbitron',sans-serif;font-size:16px;font-weight:700;color:#00e5ff;margin-bottom:18px;letter-spacing:1px;text-shadow:0 0 8px rgba(0,229,255,.4);}

/* ── NEW ATTENDANCE % BAR CHART ── */
.att-bar-row{display:flex;align-items:center;gap:12px;margin-bottom:14px;}
.att-avatar{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;flex-shrink:0;font-family:'Orbitron',sans-serif;}
.att-info{flex:1;}
.att-name{font-size:10px;letter-spacing:1.5px;margin-bottom:6px;color:#c0c8e0;}
.att-track{height:12px;background:#1a2035;border-radius:6px;overflow:hidden;position:relative;}
.att-fill{height:100%;border-radius:6px;position:relative;transition:width 1.4s cubic-bezier(.4,0,.2,1);}
.att-fill::after{content:'';position:absolute;top:2px;left:10px;width:28%;height:3px;background:rgba(255,255,255,.32);border-radius:2px;}
.att-pct{font-size:12px;font-family:'Orbitron',sans-serif;min-width:38px;text-align:right;font-weight:700;}

/* ── NEW ENGAGEMENT DONUT ── */
.eng-wrap{display:flex;gap:20px;align-items:center;}
.eng-legend{flex:1;display:flex;flex-direction:column;gap:12px;}
.eng-row{display:flex;align-items:center;gap:10px;}
.eng-icon{width:30px;height:30px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;}
.eng-right{flex:1;}
.eng-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;}
.eng-label{font-size:10px;color:#8b96b3;letter-spacing:1.5px;}
.eng-val{font-size:13px;font-weight:700;font-family:'Orbitron',sans-serif;}
.eng-mini-bar{height:4px;border-radius:2px;}

.stButton button{width:100%;border-radius:12px;background:transparent;color:#00e5ff;font-weight:700;font-size:16px;border:2px solid #00e5ff;padding:14px;transition:all .25s;box-shadow:0 0 14px rgba(0,229,255,.2);font-family:'Orbitron',sans-serif;letter-spacing:1px;}
.stButton button:hover{background:rgba(0,229,255,.1);box-shadow:0 0 30px rgba(0,229,255,.5);transform:translateY(-2px);color:#fff;}
.stTextInput input{background-color:rgba(10,14,23,.8);color:#fff;border-radius:10px;border:1px solid #1f2940;padding:12px;font-size:15px;}
.stTextInput input:focus{border-color:#00e5ff;box-shadow:0 0 12px rgba(0,229,255,.3);}
.stSelectbox div[data-baseweb="select"]{background-color:rgba(10,14,23,.8);border-radius:10px;border:1px solid #1f2940;}
[data-testid="stDataFrame"]{border-radius:14px;overflow:hidden;border:1px solid #1f2940;}
#MainMenu{visibility:hidden;}footer{visibility:hidden;}
h1,h2,h3{color:#fff;}p,label,span{color:#8b96b3;}
</style>
""", unsafe_allow_html=True)


def get_connection():
    return sqlite3.connect('data/attendai.db')

def get_students_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, name, roll_no, registered_on FROM students", conn)
    conn.close(); return df

def get_attendance_df():
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT students.name, students.roll_no, attendance.date, attendance.time, attendance.status
        FROM attendance JOIN students ON attendance.student_id = students.id
    ''', conn)
    conn.close(); return df

def get_engagement_df():
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT date, time, status FROM engagement_logs", conn)
    except Exception:
        df = pd.DataFrame(columns=["date","time","status"])
    conn.close(); return df

def load_known_faces():
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no, encoding FROM students")
    students = cursor.fetchall(); conn.close()
    known_encodings, known_ids, known_names, known_rolls = [], [], [], []
    for sid, name, roll_no, blob in students:
        known_encodings.append(np.frombuffer(blob, dtype=np.float64))
        known_ids.append(sid); known_names.append(name); known_rolls.append(roll_no)
    return known_encodings, known_ids, known_names, known_rolls

def mark_attendance_db(student_id):
    conn = get_connection(); cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    now_time = datetime.now().strftime('%H:%M:%S')
    cursor.execute('SELECT * FROM attendance WHERE student_id=? AND date=?', (student_id, today))
    if cursor.fetchone(): conn.close(); return False
    cursor.execute('INSERT INTO attendance (student_id, date, time, status) VALUES (?,?,?,?)',
                   (student_id, today, now_time, 'Present'))
    conn.commit(); conn.close(); return True

def make_cylinder_card(color, icon, value, label, fill_pct):
    fill_pct = max(4, min(96, fill_pct))
    st.markdown(f"""
    <div class="cyl-card cyl-card-{color}">
        <div class="icon-3d-{color}">{icon}</div>
        <div class="cylinder-wrap">
            <div class="cylinder-top cb-{color}"><div class="cylinder-top-shine"></div></div>
            <div class="cylinder-body">
                <div class="cylinder-fill cylinder-fill-{color}" style="height:{fill_pct}%">
                    <div class="wave-overlay wave-{color}"></div>
                </div>
            </div>
            <div class="cylinder-border cb-{color}"></div>
        </div>
        <div class="cyl-value cyl-value-{color}">{value}</div>
        <div class="cyl-label cyl-label-{color}">{label}</div>
    </div>""", unsafe_allow_html=True)


COLORS = ['#00e5ff','#ff2e92','#a855f7','#00e596','#ffaa00','#ff6b6b','#7fffd4']
COLOR_BG = ['rgba(0,229,255,.15)','rgba(255,46,146,.15)','rgba(168,85,247,.15)',
            'rgba(0,229,150,.15)','rgba(255,170,0,.15)','rgba(255,107,107,.15)']
COLOR_BORDER = ['rgba(0,229,255,.4)','rgba(255,46,146,.4)','rgba(168,85,247,.4)',
                'rgba(0,229,150,.4)','rgba(255,170,0,.4)','rgba(255,107,107,.4)']
GRADIENTS_FROM = ['#00b8cc','#cc1166','#7722cc','#00aa70','#cc8800','#cc3333']
EMOJIS = ['😎','🌸','⚡','🌿','🔥','💫','✨']

def render_attendance_bar_chart(attendance_df):
    """Render the cool avatar + glowing bar attendance % chart."""
    if attendance_df.empty:
        st.info("No attendance data yet."); return
    counts = attendance_df['name'].value_counts().reset_index()
    counts.columns = ['Student', 'Days Present']
    total_days = attendance_df['date'].nunique()
    counts['Percentage'] = (counts['Days Present'] / total_days * 100).round(0).astype(int)

    rows_html = ""
    for i, row in counts.iterrows():
        idx = i % len(COLORS)
        initial = row['Student'][0].upper()
        color = COLORS[idx]; bg = COLOR_BG[idx]; border = COLOR_BORDER[idx]
        grad_from = GRADIENTS_FROM[idx]
        pct = int(row['Percentage'])
        rows_html += f"""
        <div class="att-bar-row">
            <div class="att-avatar" style="background:{bg};color:{color};border:2px solid {border};">{initial}</div>
            <div class="att-info">
                <div class="att-name">{row['Student'].upper()}</div>
                <div class="att-track">
                    <div class="att-fill" style="width:{pct}%;background:linear-gradient(90deg,{grad_from},{color});"></div>
                </div>
            </div>
            <div class="att-pct" style="color:{color};">{pct}%</div>
        </div>"""
    st.markdown(rows_html, unsafe_allow_html=True)


def render_engagement_donut(engagement_df):
    """Render the glowing donut + mini-bar legend engagement chart."""
    if engagement_df.empty:
        st.info("No engagement data yet."); return

    sc = engagement_df['status'].value_counts()
    total = sc.sum()
    statuses = [
        ('Attentive',   '🧠', '#00e5ff', 'rgba(0,229,255,.15)'),
        ('Drowsy',      '😴', '#ff2e92', 'rgba(255,46,146,.15)'),
        ('Eyes Closed', '😪', '#a855f7', 'rgba(168,85,247,.15)'),
    ]

    circumference = 314.16  # 2*pi*50
    offset = 78.5
    segments_svg = ""
    legend_html = ""
    running_pct = 0

    for label, emoji, color, bg in statuses:
        count = sc.get(label, 0)
        pct = round(count / total * 100) if total > 0 else 0
        arc = circumference * pct / 100
        gap = circumference - arc
        dash = f"{arc:.1f} {gap:.1f}"
        segments_svg += f"""<circle cx="65" cy="65" r="50" fill="none" stroke="{color}" stroke-width="22"
            stroke-dasharray="{dash}" stroke-dashoffset="-{offset:.1f}" stroke-linecap="butt"
            style="transition:stroke-dasharray 1.5s ease;"/>"""
        offset += arc
        legend_html += f"""
        <div class="eng-row">
            <div class="eng-icon" style="background:{bg};">{emoji}</div>
            <div class="eng-right">
                <div class="eng-header">
                    <span class="eng-label">{label.upper()}</span>
                    <span class="eng-val" style="color:{color};">{pct}%</span>
                </div>
                <div class="eng-mini-bar" style="width:{pct}%;background:{color};box-shadow:0 0 6px {color}88;"></div>
            </div>
        </div>"""
        running_pct += pct

    top_label = statuses[0][0] if sc.get('Attentive',0) >= sc.get('Drowsy',0) else statuses[1][0]
    top_pct = round(sc.get('Attentive',0)/total*100) if total>0 else 0
    donut_center_color = statuses[0][2]

    donut_svg = f"""
    <svg width="140" height="140" viewBox="0 0 130 130" role="img" aria-label="Engagement breakdown donut chart">
        <circle cx="65" cy="65" r="50" fill="none" stroke="#1a2035" stroke-width="22"/>
        {segments_svg}
        <circle cx="65" cy="65" r="38" fill="rgba(13,18,30,0.95)"/>
        <text x="65" y="60" text-anchor="middle" fill="{donut_center_color}" font-size="20"
              font-family="Orbitron,sans-serif" font-weight="900">{top_pct}%</text>
        <text x="65" y="76" text-anchor="middle" fill="#6b7a99" font-size="8"
              font-family="Orbitron,sans-serif">FOCUS RATE</text>
    </svg>"""

    st.markdown(f"""
    <div class="eng-wrap">
        {donut_svg}
        <div class="eng-legend">{legend_html}</div>
    </div>""", unsafe_allow_html=True)


# ── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="text-align:center;padding:28px 0;">
    <div style="font-size:40px;text-shadow:0 0 20px rgba(0,229,255,.6);">🧠</div>
    <div style="font-family:'Orbitron',sans-serif;font-size:22px;font-weight:900;
         margin-top:10px;letter-spacing:2px;text-shadow:0 0 12px rgba(0,229,255,.4);">NEUROATTEND</div>
    <div style="font-size:11px;color:#6b7a99;margin-top:6px;letter-spacing:1px;">
        SMART ATTENDANCE &amp; ENGAGEMENT AI</div>
</div>""", unsafe_allow_html=True)

page = st.sidebar.radio("",
    ["⬡  Dashboard","⬡  Register Student","⬡  Mark Attendance",
     "⬡  Attendance Records","⬡  Analytics"])
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown("""<div style="font-size:11px;color:#3d4863;text-align:center;letter-spacing:1px;">
PYTHON · OPENCV · FACE_RECOGNITION<br>MEDIAPIPE · DEEPFACE · STREAMLIT</div>""", unsafe_allow_html=True)


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
if page == "⬡  Dashboard":
    st.markdown('<div class="neon-tag">⬡ NEON DATA</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-title">NeuroAttend</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Real-time attendance and engagement insights for your classroom</div>', unsafe_allow_html=True)

    students_df   = get_students_df()
    attendance_df = get_attendance_df()
    engagement_df = get_engagement_df()
    today         = datetime.now().strftime('%Y-%m-%d')
    today_att     = attendance_df[attendance_df['date']==today] if not attendance_df.empty else pd.DataFrame()
    attentive_cnt = len(engagement_df[engagement_df['status']=='Attentive']) if not engagement_df.empty else 0
    total_s = len(students_df); present_s = len(today_att); max_cap = max(total_s, 10)

    col1, col2, col3 = st.columns(3)
    with col1: make_cylinder_card("cyan",    "👥", total_s,       "Total Students", int(total_s/max_cap*90))
    with col2: make_cylinder_card("magenta", "✓",  present_s,     "Present Today",  int(present_s/total_s*90) if total_s else 0)
    with col3: make_cylinder_card("purple",  "◉",  attentive_cnt, "Attentive Logs", int(attentive_cnt/max(attentive_cnt,10)*90))

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
        st.markdown('<div class="neon-card-heading">⬡ ATTENDANCE TREND</div>', unsafe_allow_html=True)
        if not attendance_df.empty:
            dc = attendance_df.groupby('date').size().reset_index(name='Present Count')
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dc['date'], y=dc['Present Count'], mode='lines+markers',
                line=dict(color='#00e5ff', width=4, shape='spline', smoothing=1.3),
                marker=dict(size=9, color='#00e5ff', line=dict(width=2, color='#fff')),
                fill='tozeroy', fillcolor='rgba(0,229,255,0.15)', name='Present'))
            fig.add_trace(go.Scatter(x=dc['date'], y=dc['Present Count']*0.7, mode='lines',
                line=dict(color='#a855f7', width=3, shape='spline', smoothing=1.3, dash='dot'),
                fill='tozeroy', fillcolor='rgba(168,85,247,0.08)', name='Trend Avg'))
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#8b96b3'),
                xaxis=dict(showgrid=False, color='#6b7a99'),
                yaxis=dict(showgrid=True, gridcolor='#1f2940', color='#6b7a99'),
                margin=dict(l=10,r=10,t=10,b=10), height=300,
                legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(color='#8b96b3')))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance data yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
        st.markdown('<div class="neon-card-heading">⬡ ATTENDANCE %</div>', unsafe_allow_html=True)
        render_attendance_bar_chart(attendance_df)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
    st.markdown('<div class="neon-card-heading">⬡ REGISTERED STUDENTS</div>', unsafe_allow_html=True)
    if not students_df.empty:
        st.dataframe(students_df, use_container_width=True, hide_index=True)
    else:
        st.info("No students registered yet.")
    st.markdown('</div>', unsafe_allow_html=True)


# ── REGISTER STUDENT ──────────────────────────────────────────────────────────
elif page == "⬡  Register Student":
    st.markdown('<div class="neon-tag">⬡ SETUP</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-title">Register Student</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Capture a face and add them to the system</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
    with st.form("register_form"):
        name    = st.text_input("Student Name")
        roll_no = st.text_input("Roll Number")
        submit  = st.form_submit_button("◉  OPEN CAMERA & REGISTER")
    st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        if not name or not roll_no:
            st.error("Please enter both Name and Roll Number!")
        else:
            st.info("Camera window will open. Press 'S' to capture, 'Q' to cancel.")
            cap = cv2.VideoCapture(0); captured_frame = None
            while True:
                ret, frame = cap.read()
                if not ret: break
                frame = cv2.flip(frame, 1)
                cv2.putText(frame,"Press 'S' to Capture | 'Q' to Quit",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
                cv2.putText(frame,f"Student: {name} | Roll: {roll_no}",(10,60),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,0),2)
                cv2.imshow("NeuroAttend - Register Student", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'): captured_frame = frame.copy(); break
                elif key == ord('q'): break
            cap.release(); cv2.destroyAllWindows()
            if captured_frame is None:
                st.warning("Registration cancelled.")
            else:
                rgb = np.ascontiguousarray(cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB))
                locs = face_recognition.face_locations(rgb)
                if len(locs)==0: st.error("No face detected!")
                elif len(locs)>1: st.error("Multiple faces detected!")
                else:
                    enc = face_recognition.face_encodings(rgb, locs)[0]
                    photo_path = f"student_photos/{roll_no}_{name}.jpg"
                    cv2.imwrite(photo_path, captured_frame)
                    try:
                        conn = get_connection(); cursor = conn.cursor()
                        cursor.execute('INSERT INTO students (name,roll_no,encoding,photo_path) VALUES (?,?,?,?)',
                                       (name, roll_no, enc.tobytes(), photo_path))
                        conn.commit(); conn.close()
                        st.success(f"✅ {name} (Roll No: {roll_no}) registered!")
                        st.image(cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB), caption="Captured Photo", width=300)
                    except sqlite3.IntegrityError:
                        st.error(f"Roll No {roll_no} already registered!")


# ── MARK ATTENDANCE ───────────────────────────────────────────────────────────
elif page == "⬡  Mark Attendance":
    st.markdown('<div class="neon-tag">⬡ LIVE SESSION</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-title">Mark Attendance</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Live face recognition with blink-based liveness check</div>', unsafe_allow_html=True)

    EAR_THRESHOLD = 0.21; BLINK_CHECK_DURATION = 5.0

    def ear_dist(p1,p2): return np.linalg.norm(np.array(p1)-np.array(p2))
    def calc_ear(pts):
        return (ear_dist(pts[1],pts[5])+ear_dist(pts[2],pts[4]))/(2.0*ear_dist(pts[0],pts[3]))

    st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
    start = st.button("▶  START ATTENDANCE CAMERA")
    st.markdown('</div>', unsafe_allow_html=True)

    if start:
        known_encodings, known_ids, known_names, known_rolls = load_known_faces()
        if not known_encodings:
            st.error("No students registered yet!")
        else:
            st.info("Camera opening... Press 'Q' to stop.")
            cap = cv2.VideoCapture(0)
            blink_start, eyes_closed, blink_det, marked_today = {},{},{},set()
            marked_names = []
            while True:
                ret, frame = cap.read()
                if not ret: break
                frame = cv2.flip(frame, 1)
                rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                locs = face_recognition.face_locations(rgb)
                encs = face_recognition.face_encodings(rgb, locs)
                lmarks = face_recognition.face_landmarks(rgb, locs)
                for (top,right,bottom,left),fe,lm in zip(locs,encs,lmarks):
                    matches = face_recognition.compare_faces(known_encodings, fe, tolerance=0.5)
                    dists   = face_recognition.face_distance(known_encodings, fe)
                    name="Unknown"; color=(0,0,255); status_text=""
                    avg_ear=None
                    if 'left_eye' in lm and 'right_eye' in lm:
                        avg_ear=(calc_ear(lm['left_eye'])+calc_ear(lm['right_eye']))/2.0
                    if len(dists):
                        bmi=np.argmin(dists)
                        if matches[bmi]:
                            sid=known_ids[bmi]; name=known_names[bmi]; roll=known_rolls[bmi]
                            if sid in marked_today:
                                color=(0,255,0); status_text="Already Marked"
                            else:
                                if sid not in blink_start:
                                    blink_start[sid]=time.time(); eyes_closed[sid]=False; blink_det[sid]=False
                                elapsed=time.time()-blink_start[sid]
                                if avg_ear is not None:
                                    if avg_ear<EAR_THRESHOLD: eyes_closed[sid]=True
                                    else:
                                        if eyes_closed[sid]: blink_det[sid]=True
                                        eyes_closed[sid]=False
                                if blink_det[sid]:
                                    color=(0,255,0); status_text="LIVE - Marking..."
                                    if mark_attendance_db(sid): marked_names.append(f"{name} ({roll})")
                                    marked_today.add(sid)
                                elif elapsed>BLINK_CHECK_DURATION:
                                    color=(0,0,255); status_text="SPOOF? No blink"
                                else:
                                    color=(0,165,255); status_text=f"Checking... {int(BLINK_CHECK_DURATION-elapsed)}s"
                    cv2.rectangle(frame,(left,top),(right,bottom),color,2)
                    cv2.putText(frame,name,(left,top-30),cv2.FONT_HERSHEY_SIMPLEX,0.8,color,2)
                    cv2.putText(frame,status_text,(left,top-5),cv2.FONT_HERSHEY_SIMPLEX,0.6,color,2)
                cv2.imshow("NeuroAttend - Mark Attendance", frame)
                if cv2.waitKey(1)&0xFF==ord('q'): break
            cap.release(); cv2.destroyAllWindows()
            if marked_names:
                st.success("✅ Attendance marked for:")
                for n in marked_names: st.write(f"- {n}")
            else:
                st.info("No new attendance marked.")


# ── ATTENDANCE RECORDS ────────────────────────────────────────────────────────
elif page == "⬡  Attendance Records":
    st.markdown('<div class="neon-tag">⬡ RECORDS</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-title">Attendance Records</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Browse and filter all attendance logs</div>', unsafe_allow_html=True)

    attendance_df = get_attendance_df()
    if attendance_df.empty:
        st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
        st.warning("No attendance records yet.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
        st.markdown('<div class="neon-card-heading">⬡ ALL RECORDS</div>', unsafe_allow_html=True)
        st.dataframe(attendance_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
        st.markdown('<div class="neon-card-heading">⬡ FILTER BY DATE</div>', unsafe_allow_html=True)
        dates = sorted(attendance_df['date'].unique(), reverse=True)
        sel = st.selectbox("", dates)
        st.dataframe(attendance_df[attendance_df['date']==sel], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── ANALYTICS ─────────────────────────────────────────────────────────────────
elif page == "⬡  Analytics":
    st.markdown('<div class="neon-tag">⬡ INSIGHTS</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-subtitle">Visual insights into attendance &amp; engagement</div>', unsafe_allow_html=True)

    attendance_df = get_attendance_df()
    engagement_df = get_engagement_df()
    students_df   = get_students_df()
    today         = datetime.now().strftime('%Y-%m-%d')
    today_att     = attendance_df[attendance_df['date']==today] if not attendance_df.empty else pd.DataFrame()
    attentive_cnt = len(engagement_df[engagement_df['status']=='Attentive']) if not engagement_df.empty else 0
    total_s = len(students_df); present_s = len(today_att); max_cap = max(total_s, 10)

    c1, c2, c3 = st.columns(3)
    with c1: make_cylinder_card("cyan",    "👥", total_s,       "Total Students", int(total_s/max_cap*90))
    with c2: make_cylinder_card("magenta", "✓",  present_s,     "Present Today",  int(present_s/total_s*90) if total_s else 0)
    with c3: make_cylinder_card("purple",  "◉",  attentive_cnt, "Attentive Logs", int(attentive_cnt/max(attentive_cnt,10)*90))

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
        st.markdown('<div class="neon-card-heading">⬡ ATTENDANCE %</div>', unsafe_allow_html=True)
        render_attendance_bar_chart(attendance_df)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
        st.markdown('<div class="neon-card-heading">⬡ ENGAGEMENT BREAKDOWN</div>', unsafe_allow_html=True)
        render_engagement_donut(engagement_df)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-content-card">', unsafe_allow_html=True)
    st.markdown('<div class="neon-card-heading">⬡ ATTENDANCE TREND</div>', unsafe_allow_html=True)
    if not attendance_df.empty:
        dc = attendance_df.groupby('date').size().reset_index(name='Present Count')
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=dc['date'], y=dc['Present Count'], mode='lines+markers',
            line=dict(color='#a855f7', width=4, shape='spline', smoothing=1.3),
            marker=dict(size=10, color='#00e5ff', line=dict(width=2, color='#a855f7')),
            fill='tozeroy', fillcolor='rgba(168,85,247,0.12)'))
        fig3.add_trace(go.Scatter(x=dc['date'], y=dc['Present Count']*0.65, mode='lines',
            line=dict(color='#00e5ff', width=2, dash='dot', shape='spline', smoothing=1.3),
            fill='tozeroy', fillcolor='rgba(0,229,255,0.06)'))
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#8b96b3'),
            xaxis=dict(showgrid=False, color='#6b7a99'),
            yaxis=dict(showgrid=True, gridcolor='#1f2940', color='#6b7a99'),
            margin=dict(l=10,r=10,t=10,b=10), height=320, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No trend data yet.")
    st.markdown('</div>', unsafe_allow_html=True)