# clean_app.py
# Compact two-page Streamlit app: Ledger (Add) + Analytics (Charts & Check)
from datetime import datetime
import os
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, text

# ---------- CONFIG ----------
DB_USER = "root"
DB_PASS = "12345"
DB_HOST = "localhost"
DB_NAME = "securecheck_db"
CSV_FALLBACK = "cleaned_traffic_stops.csv"

st.set_page_config(page_title="Digital Ledger for Patrol Post Logs", layout="wide")

# ---------- STYLE ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Caslon+Text&display=swap');
    html, body, .stApp { font-family: "Palatino Linotype", "Book Antiqua", Palatino, serif; background:#f7fbfa; color:#064b43; }
    .hdr{font-size:30px; font-weight:700; color:#075a4f;}
    .sub{color:#0b6b60; margin-bottom:8px;}
    .kpi{background:#eaf8f4;padding:12px;border-radius:10px;text-align:center;}
    .note{background:#eaf8f4;border-left:5px solid #0ea58b;padding:10px;border-radius:6px}
    .smallcard{background:#ffffff;border-radius:8px;padding:8px;border:1px solid #e6f3ef}
    </style>
    """, unsafe_allow_html=True
)

# ---------- HELPERS ----------
def engine_from_cfg():
    return create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

def load_df():
    try:
        eng = engine_from_cfg()
        with eng.connect() as c: c.execute(text("SELECT 1"))
        df = pd.read_sql("SELECT * FROM traffic_stops;", eng)
        return df, eng
    except Exception:
        if os.path.exists(CSV_FALLBACK):
            st.sidebar.warning("DB not reachable — using CSV fallback for viewing.")
            return pd.read_csv(CSV_FALLBACK), None
        st.sidebar.error("DB not reachable and no CSV fallback.")
        return pd.DataFrame(), None

def normalize(df):
    if df.empty: return df
    df = df.copy()
    df.columns = df.columns.str.strip()
    for c in ["driver_age","stop_hour","is_arrested","search_conducted","drugs_related_stop"]:
        if c in df.columns: df[c] = pd.to_numeric(df[c],errors="coerce").fillna(0).astype(int)
    if "driver_age" in df.columns:
        bins=[0,18,25,35,50,65,200]; labs=["<18","18-24","25-34","35-49","50-64","65+"]
        df["age_group"]=pd.cut(df["driver_age"],bins=bins,labels=labs)
    return df

def insert_row(engine, p):
    stmt = text("""
      INSERT INTO traffic_stops
       (stop_date, stop_time, country_name, driver_age, driver_gender, driver_race, violation,
        search_conducted, stop_outcome, is_arrested, drugs_related_stop, vehicle_number, stop_hour)
      VALUES
       (:stop_date, :stop_time, :country_name, :driver_age, :driver_gender, :driver_race, :violation,
        :search_conducted, :stop_outcome, :is_arrested, :drugs_related_stop, :vehicle_number, :stop_hour)
    """)
    with engine.begin() as conn: conn.execute(stmt, p)

# ---------- DATA ----------
df, engine = load_df()
df = normalize(df)

# ---------- NAV ----------
page = st.sidebar.radio("Go to", ["Ledger (Add Record)", "Analytics & Check"])

# ---------- PAGE: Ledger ----------
if page == "Ledger (Add Record)":
    st.markdown('<div class="hdr">Digital Ledger for Patrol Post Logs</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Add new patrol stop logs. After submit a single-paragraph summary appears below.</div>', unsafe_allow_html=True)

    # KPIs
    total = len(df) if not df.empty else 0
    arrests = int(df["is_arrested"].sum()) if "is_arrested" in df and not df.empty else 0
    avg_age = round(df["driver_age"].mean(),1) if "driver_age" in df and not df.empty else "N/A"
    searchpct = round(df["search_conducted"].mean()*100,2) if "search_conducted" in df and not df.empty else "N/A"
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="kpi"><b>Total Stops</b><div style="font-size:20px">{total:,}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><b>Total Arrests</b><div style="font-size:20px">{arrests:,}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><b>Average Age</b><div style="font-size:20px">{avg_age}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi"><b>Search Rate (%)</b><div style="font-size:20px">{searchpct}</div></div>', unsafe_allow_html=True)

    st.markdown("")  # gap
    st.markdown('<div style="background:#fff;padding:12px;border-radius:10px;">', unsafe_allow_html=True)
    st.subheader("Add New Traffic Stop Record")
    with st.form("add"):
        col1,col2,col3 = st.columns(3)
        with col1:
            stop_date = st.date_input("Stop Date", value=datetime.today())
            stop_time = st.text_input("Stop Time (HH:MM or '5 minutes')", "")
            country = st.text_input("Country", value="India")
            age = st.number_input("Driver Age", 16, 120, 30)
        with col2:
            gender = st.selectbox("Gender", ["M","F"])
            race = st.text_input("Race","Other")
            viol = st.selectbox("Violation", ["Speeding","Signal","Seatbelt","DUI","Other"])
            search = st.selectbox("Search Conducted", [0,1], format_func=lambda x: "Yes" if x==1 else "No")
        with col3:
            outcome = st.selectbox("Outcome", ["Ticket","Warning","Arrest"])
            arrested = st.selectbox("Is Arrested", [0,1], format_func=lambda x: "Yes" if x==1 else "No")
            drugs = st.selectbox("Drugs Related", [0,1], format_func=lambda x: "Yes" if x==1 else "No")
            vehicle = st.text_input("Vehicle No.")
        sent = st.form_submit_button("Add Record")
    st.markdown('</div>', unsafe_allow_html=True)

    if sent:
        if engine is None:
            st.error("Cannot insert: database not connected.")
        else:
            p = {
                "stop_date": stop_date.strftime("%Y-%m-%d"),
                "stop_time": (stop_time or "").strip(),
                "country_name": country.strip(),
                "driver_age": int(age),
                "driver_gender": gender,
                "driver_race": race.strip(),
                "violation": viol,
                "search_conducted": int(search),
                "stop_outcome": outcome,
                "is_arrested": int(arrested),
                "drugs_related_stop": int(drugs),
                "vehicle_number": vehicle.strip(),
                "stop_hour": 0
            }
            try:
                if ":" in p["stop_time"]:
                    p["stop_hour"] = int(p["stop_time"].split(":")[0])
            except Exception:
                p["stop_hour"] = 0
            try:
                insert_row(engine, p)
                st.success("Record added successfully.")
                gender_word = "male" if gender=="M" else "female"
                search_phrase = "No search was conducted" if search==0 else "A search was conducted"
                if outcome.lower()=="ticket": outcome_phrase="the driver received a citation."
                elif outcome.lower()=="warning": outcome_phrase="the driver received a warning."
                elif outcome.lower()=="arrest": outcome_phrase="the driver was arrested."
                else: outcome_phrase=f"the outcome was {outcome}."
                drugs_phrase = "The stop was drug-related." if drugs==1 else "The stop was not drug-related."
                time_phrase = f"at {p['stop_time']}" if p['stop_time'] else "at an unspecified time"
                paragraph = (f"A {age}-year-old {gender_word} driver was stopped for {viol} {time_phrase}. "
                             f"{search_phrase}, and {outcome_phrase} {drugs_phrase} Recorded in {country}.")
                st.markdown(f'<div class="note">{paragraph}</div>', unsafe_allow_html=True)
                df, engine = load_df(); df = normalize(df)
            except Exception as e:
                st.error(f"Insert failed: {e}")

# ---------- PAGE: Analytics & Check ----------
else:
    st.markdown('<div class="hdr">Analytics & Check</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub">Explore the data and run quick checks.</div>', unsafe_allow_html=True)

    # filters
    country_opts = sorted(df["country_name"].dropna().unique()) if not df.empty else []
    gender_opts = sorted(df["driver_gender"].dropna().unique()) if not df.empty else []
    viol_opts = sorted(df["violation"].dropna().unique()) if not df.empty else []

    f1,f2,f3,f4 = st.columns(4)
    sel_c = f1.multiselect("Country", options=country_opts, default=country_opts)
    sel_g = f2.multiselect("Gender", options=gender_opts, default=gender_opts)
    sel_v = f3.multiselect("Violation", options=viol_opts, default=viol_opts)
    chart_choice = f4.selectbox("Chart", ["Arrests by Gender (pie)","Violations by Country (bar)"])

    if df.empty:
        st.info("No data available.")
        filtered = df
    else:
        filtered = df[df["country_name"].isin(sel_c) & df["driver_gender"].isin(sel_g) & df["violation"].isin(sel_v)]

    # KPIs small
    k1,k2,k3,k4 = st.columns(4)
    tot = len(filtered)
    arr = int(filtered["is_arrested"].sum()) if "is_arrested" in filtered and not filtered.empty else 0
    avg = round(filtered["driver_age"].mean(),1) if "driver_age" in filtered and not filtered.empty else "N/A"
    srate = round(filtered["search_conducted"].mean()*100,2) if "search_conducted" in filtered and not filtered.empty else "N/A"
    k1.metric("Total Stops", f"{tot:,}")
    k2.metric("Total Arrests", f"{arr:,}")
    k3.metric("Average Age", avg)
    k4.metric("Search Rate (%)", srate)

    st.markdown("---")

    # --- Six short analytics (compact)
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Top 5 Violations")
        if filtered.empty:
            st.info("No data.")
        else:
            topv = filtered["violation"].value_counts().head(5).rename_axis("violation").reset_index(name="count")
            st.table(topv)  # small table
        st.subheader("Arrests by Violation (top 5)")
        if filtered.empty:
            st.info("No data.")
        else:
            ar = filtered[filtered["is_arrested"]==1].groupby("violation").size().reset_index(name="arrests").sort_values("arrests",ascending=False).head(5)
            if not ar.empty:
                figA = px.bar(ar, x="violation", y="arrests", color_discrete_sequence=["#0ea58b"])
                st.plotly_chart(figA, use_container_width=True)
            else:
                st.info("No arrests in selection.")
    with colB:
        st.subheader("Stops by Hour (counts)")
        if filtered.empty or "stop_hour" not in filtered:
            st.info("No hour data.")
        else:
            sh = filtered.groupby("stop_hour").size().reset_index(name="count").sort_values("stop_hour")
            figB = px.bar(sh, x="stop_hour", y="count", labels={"stop_hour":"hour"}, color_discrete_sequence=["#0b6b60"])
            st.plotly_chart(figB, use_container_width=True)

    st.markdown("---")
    colC, colD = st.columns(2)
    with colC:
        st.subheader("Drug-related stops (count)")
        if filtered.empty or "drugs_related_stop" not in filtered:
            st.info("No data.")
        else:
            dr = filtered["drugs_related_stop"].value_counts().rename_axis("drug").reset_index(name="count")
            dr["drug"] = dr["drug"].map({0:"Not drug-related",1:"Drug-related"}).fillna(dr["drug"])
            figC = px.pie(dr, names="drug", values="count", hole=0.4)
            st.plotly_chart(figC, use_container_width=True)
    with colD:
        st.subheader("Avg age by Violation (top 5)")
        if filtered.empty or "driver_age" not in filtered:
            st.info("No data.")
        else:
            av = filtered.groupby("violation")["driver_age"].mean().round(1).reset_index().sort_values("driver_age",ascending=False).head(5)
            st.table(av)

    st.markdown("---")
    st.subheader("Top Countries by Stops")
    if filtered.empty:
        st.info("No data.")
    else:
        topc = filtered["country_name"].value_counts().head(6).rename_axis("country").reset_index(name="count")
        figC2 = px.bar(topc, x="country", y="count", color_discrete_sequence=["#0ea58b"])
        st.plotly_chart(figC2, use_container_width=True)

    # narrative & quick check
    st.markdown("---")
    st.subheader("Narrative Summary")
    if filtered.empty:
        st.info("No summary available.")
    else:
        most_vi = filtered["violation"].mode()[0] if not filtered["violation"].dropna().empty else "N/A"
        top_ctry = filtered["country_name"].mode()[0] if not filtered["country_name"].dropna().empty else "N/A"
        narr = (f"Selected set: {len(filtered):,} stops, {arr:,} arrests. Most common violation: {most_vi}. "
                f"Avg age: {avg}. Approx {srate}% involved searches. Top country: {top_ctry}.")
        st.markdown(f'<div class="note">{narr}</div>', unsafe_allow_html=True)

    st.subheader("Quick Check")
    with st.form("qc"):
        a,b,c = st.columns(3)
        qc_country = a.selectbox("Country", ["All"] + country_opts)
        qc_gender = b.selectbox("Gender", ["All"] + gender_opts)
        qc_violation = c.selectbox("Violation", ["All"] + viol_opts)
        qc_submit = st.form_submit_button("Run")
    if qc_submit:
        q = df.copy()
        if qc_country != "All": q = q[q["country_name"]==qc_country]
        if qc_gender != "All": q = q[q["driver_gender"]==qc_gender]
        if qc_violation != "All": q = q[q["violation"]==qc_violation]
        if q.empty:
            st.warning("No matches.")
        else:
            s = int(q["is_arrested"].sum()) if "is_arrested" in q else 0
            avgq = round(q["driver_age"].mean(),1) if "driver_age" in q else "N/A"
            st.success(f"{len(q):,} matches — {s:,} arrests — avg age {avgq}.")

# ---------- FOOTER ----------
st.markdown('<div style="text-align:center;color:gray;margin-top:14px;">Developed by Bharanigeswari | Data Science Project</div>', unsafe_allow_html=True)
