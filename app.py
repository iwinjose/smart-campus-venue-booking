import calendar
from datetime import date, datetime, time, timedelta
import html

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database import (
    OCCUPANCY_STATUSES,
    add_booking,
    check_conflicts_and_stock,
    fetch_dataframe,
    get_equipment_stock,
    get_monthly_booking_counts,
    get_slot_availability,
    init_db,
    now_ist,
    reset_demo_data,
    simulate_incoming_request,
    update_booking_status,
)

# ---------------------------------------------------------------------------
# Calm, Friendly Design Palette
# ---------------------------------------------------------------------------
BG_COLOR = "#F7F9FB"
CARD_BG = "#FFFFFF"
BORDER = "#E2E8F0"
TEXT_MAIN = "#0F172A"
TEXT_SUB = "#64748B"
PRIMARY = "#059669"
PRIMARY_HOVER = "#047857"
PRIMARY_SOFT = "#ECFDF5"
BUSY_TEXT = "#DC2626"
BUSY_SOFT = "#FEF2F2"
AMBER_TEXT = "#B45309"
AMBER_SOFT = "#FFFBEB"

# ---------------------------------------------------------------------------
# Page Setup & Database Bootstrapping
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Christ Venue Booking",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

if "selected_date" not in st.session_state:
    st.session_state["selected_date"] = now_ist().date()
if "cal_year" not in st.session_state:
    st.session_state["cal_year"] = st.session_state["selected_date"].year
if "cal_month" not in st.session_state:
    st.session_state["cal_month"] = st.session_state["selected_date"].month

# ---------------------------------------------------------------------------
# Clean, Breathable Modern CSS
# ---------------------------------------------------------------------------
st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {TEXT_MAIN};
    }}
    .stApp {{
        background-color: {BG_COLOR};
    }}

    /* Clean minimal Streamlit chrome */
    #MainMenu, footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 0.35rem !important;
    }}
    [data-testid="stToolbar"] {{
        right: 0.75rem;
        top: 0.2rem;
        opacity: 0.25;
    }}
    [data-testid="stToolbar"]:hover {{ opacity: 1; }}

    .block-container {{
        padding-top: 1.4rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1240px;
    }}

    /* Header Brand */
    .vp-brand {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }}
    .vp-brand-icon {{
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: {PRIMARY};
        color: #FFFFFF;
        font-size: 1.25rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(5, 150, 105, 0.22);
    }}
    .vp-brand-name {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {TEXT_MAIN};
        line-height: 1.15;
        letter-spacing: -0.02em;
    }}
    .vp-brand-sub {{
        font-size: 0.85rem;
        color: {TEXT_SUB};
        margin-top: 1px;
    }}

    /* Live Status Pill */
    .vp-live-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background: {PRIMARY_SOFT};
        color: {PRIMARY};
        border: 1px solid #A7F3D0;
        padding: 0.32rem 0.85rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .vp-live-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {PRIMARY};
    }}

    /* Simple Summary Metric Cards */
    .vp-stat-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }}
    .vp-stat-label {{
        font-size: 0.82rem;
        font-weight: 500;
        color: {TEXT_SUB};
        margin-bottom: 0.35rem;
    }}
    .vp-stat-value {{
        font-size: 1.65rem;
        font-weight: 700;
        color: {TEXT_MAIN};
        line-height: 1.15;
        letter-spacing: -0.02em;
    }}
    .vp-stat-hint {{
        font-size: 0.78rem;
        color: {TEXT_SUB};
        margin-top: 0.25rem;
    }}
    .vp-stat-hint.good {{ color: {PRIMARY}; font-weight: 600; }}
    .vp-stat-hint.warn {{ color: {AMBER_TEXT}; font-weight: 600; }}

    /* Clean Hall Cards (With Integrated Book Button Below) */
    [class*="st-key-hall_card_"] {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 1.15rem 1.2rem 1rem 1.2rem;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    [class*="st-key-hall_card_"]:hover {{
        border-color: #CBD5E1;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    }}
    .vp-hall-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 0.5rem;
        margin-bottom: 0.45rem;
    }}
    .vp-hall-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {TEXT_MAIN};
        line-height: 1.25;
    }}
    .vp-hall-sub {{
        font-size: 0.8rem;
        color: {TEXT_SUB};
        margin-bottom: 0.65rem;
    }}
    .vp-pill-free {{
        background: {PRIMARY_SOFT};
        color: {PRIMARY};
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
        white-space: nowrap;
    }}
    .vp-pill-busy {{
        background: {BUSY_SOFT};
        color: {BUSY_TEXT};
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
        white-space: nowrap;
    }}
    .vp-hall-info-box {{
        background: #F8FAFC;
        border-radius: 10px;
        padding: 0.65rem 0.8rem;
        font-size: 0.82rem;
        color: #334155;
        min-height: 62px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 0.55rem;
    }}
    .vp-hall-info-box.busy {{
        background: #FEF7F7;
        border: 1px solid #FEE2E2;
    }}

    /* Clean Content Section Cards */
    .st-key-timeline_card,
    .st-key-finder_card,
    .st-key-chart_eq,
    .st-key-chart_hall {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }}

    /* Approval & Handover Queue Cards */
    .vp-req-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 0.9rem 1.15rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
    }}
    .vp-req-title {{
        font-size: 0.96rem;
        font-weight: 600;
        color: {TEXT_MAIN};
        margin-bottom: 0.25rem;
    }}
    .vp-req-meta {{
        font-size: 0.83rem;
        color: {TEXT_SUB};
        line-height: 1.45;
    }}
    .vp-badge-pending {{
        background: {AMBER_SOFT};
        color: {AMBER_TEXT};
        font-size: 0.74rem;
        font-weight: 600;
        padding: 2px 9px;
        border-radius: 999px;
        margin-left: 6px;
    }}
    .vp-badge-approved {{
        background: {PRIMARY_SOFT};
        color: {PRIMARY};
        font-size: 0.74rem;
        font-weight: 600;
        padding: 2px 9px;
        border-radius: 999px;
        margin-left: 6px;
    }}
    .vp-badge-dispatched {{
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 2px 9px;
        border-radius: 999px;
        margin-left: 6px;
    }}

    /* Clean Section Headings */
    .vp-section-title {{
        font-size: 1.12rem;
        font-weight: 700;
        color: {TEXT_MAIN};
        letter-spacing: -0.01em;
        margin: 0.35rem 0 0.15rem 0;
    }}
    .vp-section-sub {{
        font-size: 0.85rem;
        color: {TEXT_SUB};
        margin-bottom: 0.75rem;
    }}

    /* Clean Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: #FFFFFF;
        padding: 0.35rem;
        border-radius: 12px;
        border: 1px solid {BORDER};
        margin-bottom: 1rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px !important;
        padding: 0.5rem 1.1rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: {TEXT_SUB} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {PRIMARY_SOFT} !important;
        color: {PRIMARY} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}

    /* Friendly Buttons */
    .stButton > button[kind="primary"] {{
        background-color: {PRIMARY} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 1rem !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: {PRIMARY_HOVER} !important;
    }}
    .stButton > button[kind="secondary"] {{
        background-color: #FFFFFF !important;
        color: {TEXT_MAIN} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 0.42rem 0.95rem !important;
    }}
    .stButton > button[kind="secondary"]:hover {{
        border-color: {PRIMARY} !important;
        color: {PRIMARY} !important;
        background-color: {PRIMARY_SOFT} !important;
    }}

    /* Interactive Highlighted Calendar Popover */
    [data-testid="stPopoverBody"] {{
        min-width: 340px !important;
        padding: 0.9rem 1rem !important;
        border-radius: 14px !important;
    }}
    .vp-cal-month-title {{
        text-align: center;
        font-size: 0.96rem;
        font-weight: 700;
        color: {TEXT_MAIN};
        padding-top: 0.35rem;
    }}
    .vp-cal-weekdays {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        text-align: center;
        font-size: 0.74rem;
        font-weight: 600;
        color: {TEXT_SUB};
        margin: 0.4rem 0 0.25rem 0;
    }}
    .vp-cal-legend {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.6rem;
        padding-top: 0.55rem;
        border-top: 1px solid #F1F5F9;
        font-size: 0.74rem;
        color: {TEXT_SUB};
    }}
    .vp-leg-item {{
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }}
    .vp-leg-swatch {{
        width: 10px;
        height: 10px;
        border-radius: 3px;
        display: inline-block;
    }}
    [class*="st-key-cal_open_"] button,
    [class*="st-key-cal_booked_"] button,
    [class*="st-key-cal_pending_"] button,
    [class*="st-key-cal_sel_"] button {{
        padding: 0.2rem 0 !important;
        min-height: 2.25rem !important;
        font-size: 0.82rem !important;
        border-radius: 8px !important;
        position: relative !important;
    }}
    [class*="st-key-cal_open_"] button {{
        background-color: #FFFFFF !important;
        border: 1px solid #F1F5F9 !important;
        color: #475569 !important;
        font-weight: 500 !important;
    }}
    [class*="st-key-cal_open_"] button:hover {{
        border-color: #CBD5E1 !important;
        background-color: #F8FAFC !important;
    }}
    [class*="st-key-cal_booked_"] button {{
        background-color: #DCFCE7 !important;
        border: 1.5px solid #10B981 !important;
        color: #065F46 !important;
        font-weight: 700 !important;
    }}
    [class*="st-key-cal_booked_"] button::after {{
        content: "";
        position: absolute;
        bottom: 3px;
        left: 50%;
        transform: translateX(-50%);
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background-color: #059669;
    }}
    [class*="st-key-cal_pending_"] button {{
        background-color: #ECFDF5 !important;
        border: 1.5px solid #F59E0B !important;
        color: #065F46 !important;
        font-weight: 700 !important;
    }}
    [class*="st-key-cal_pending_"] button::after {{
        content: "";
        position: absolute;
        bottom: 3px;
        left: 50%;
        transform: translateX(-50%);
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background-color: #F59E0B;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Guided, Friendly Booking Modal (Pre-fills Hall & Checks Conflicts Live!)
# ---------------------------------------------------------------------------
@st.dialog("Book a Campus Venue", width="large")
def open_booking_dialog(
    default_date,
    preselected_venue: str | None = None,
    default_start: time = time(10, 0),
    default_end: time = time(12, 0),
) -> None:
    venues_df = fetch_dataframe("SELECT name, block, capacity, built_in_av FROM venues ORDER BY id ASC")
    venue_names = venues_df["name"].tolist()
    venue_meta = {
        r["name"]: f"{r['name']} — {r['block']} (Seats {r['capacity']})"
        for _, r in venues_df.iterrows()
    }
    default_idx = venue_names.index(preselected_venue) if preselected_venue in venue_names else 0
    stock = get_equipment_stock()

    st.markdown("**1. Choose Venue & Time**")
    c1, c2 = st.columns([1.4, 1.0], gap="medium")
    with c1:
        chosen_venue = st.selectbox(
            "Campus Hall",
            options=venue_names,
            index=default_idx,
            format_func=lambda v: venue_meta[v],
        )
    with c2:
        b_date = st.date_input("Date", value=default_date)

    t1, t2 = st.columns(2, gap="medium")
    with t1:
        start_t = st.time_input("Start Time", value=default_start)
    with t2:
        end_t = st.time_input("End Time", value=default_end)

    # Instant friendly availability check
    b_date_str = b_date.strftime("%Y-%m-%d")
    s_str = start_t.strftime("%H:%M")
    e_str = end_t.strftime("%H:%M")
    avail_tv, avail_mic, avail_pa = stock["tv"], stock["mic"], stock["pa"]

    if start_t >= end_t:
        st.warning("Please pick an End Time that is after the Start Time.")
    else:
        slot = get_slot_availability(b_date_str, s_str, e_str)
        avail_tv, avail_mic, avail_pa = slot["avail_tv"], slot["avail_mic"], slot["avail_pa"]
        if chosen_venue in slot["occupied_venues"]:
            clash = slot["occupied_venues"][chosen_venue]
            st.error(
                f"**{chosen_venue} is already booked** from {clash['start_time']} to {clash['end_time']} "
                f"for *{clash['event_title']}*. Try another time slot or hall."
            )
        else:
            st.success(f"**{chosen_venue} is available** from {s_str} to {e_str}!")

    st.divider()
    st.markdown("**2. Event Details**")
    d1, d2 = st.columns(2, gap="medium")
    with d1:
        event_title = st.text_input("Event Name*", placeholder="e.g., MCA Tech Talk / Workshop")
    with d2:
        organizer = st.text_input("Your Name / Coordinator*", placeholder="e.g., Iwin Jose (2647126)")

    department = st.selectbox(
        "Department or Club",
        [
            "Dept. of Computer Science",
            "CSA (Centre for Social Action)",
            "CAPS (Centre for Academic & Professional Support)",
            "SWO (Student Welfare Office)",
            "Dept. of Commerce & Management",
            "Placement Cell",
        ],
    )

    st.divider()
    st.markdown("**3. Extra Movable AV Equipment** *(optional)*")
    e1, e2, e3 = st.columns(3, gap="medium")
    with e1:
        req_tv = st.number_input(f'65" Smart TVs ({avail_tv} free)', 0, stock["tv"], 0)
    with e2:
        req_mic = st.number_input(f"Wireless Mics ({avail_mic} free)", 0, stock["mic"], 0)
    with e3:
        req_pa = st.number_input(f"PA Systems ({avail_pa} free)", 0, stock["pa"], 0)

    st.write("")
    if st.button("Submit Booking Request", type="primary", width="stretch"):
        if not event_title.strip() or not organizer.strip():
            st.warning("Please fill in both the Event Name and Your Name.")
        else:
            is_ok, msg = check_conflicts_and_stock(
                chosen_venue, b_date_str, s_str, e_str, int(req_tv), int(req_mic), int(req_pa)
            )
            if is_ok:
                bid = add_booking(
                    event_title,
                    department,
                    organizer,
                    chosen_venue,
                    b_date_str,
                    s_str,
                    e_str,
                    int(req_tv),
                    int(req_mic),
                    int(req_pa),
                )
                st.toast(f"Booking #{bid} submitted for {chosen_venue}!", icon="✅")
                st.rerun()
            else:
                st.error(msg)


# ---------------------------------------------------------------------------
# Simple, Uncluttered Top Header with Highlighted Booking Calendar
# ---------------------------------------------------------------------------
selected_date_val = st.session_state["selected_date"]
date_str = selected_date_val.strftime("%Y-%m-%d")

sel_month_counts = get_monthly_booking_counts(selected_date_val.year, selected_date_val.month)
sel_day_total = sel_month_counts.get(date_str, {}).get("total", 0)
cal_btn_label = (
    f"📅 {selected_date_val.strftime('%d %b %Y')} · {sel_day_total} booked"
    if sel_day_total > 0
    else f"📅 {selected_date_val.strftime('%d %b %Y')} · Open"
)

h_left, h_date, h_cta = st.columns([3.0, 1.75, 1.2], vertical_alignment="center", gap="medium")
with h_left:
    st.markdown(
        """
        <div class="vp-brand">
            <div class="vp-brand-icon">🏛️</div>
            <div>
                <div class="vp-brand-name">Christ Venue Booking</div>
                <div class="vp-brand-sub">CHRIST University · Campus Hall &amp; AV Equipment Booking</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with h_date:
    with st.popover(cal_btn_label, width="stretch"):
        cy = st.session_state["cal_year"]
        cm = st.session_state["cal_month"]

        nav_prev, nav_lbl, nav_next, nav_today = st.columns([0.75, 2.4, 0.75, 1.15], gap="small")
        with nav_prev:
            if st.button("◀", key="cal_prev_m", width="stretch"):
                if cm == 1:
                    st.session_state["cal_year"] = cy - 1
                    st.session_state["cal_month"] = 12
                else:
                    st.session_state["cal_month"] = cm - 1
                st.rerun()
        with nav_lbl:
            st.markdown(
                f'<div class="vp-cal-month-title">{calendar.month_name[cm]} {cy}</div>',
                unsafe_allow_html=True,
            )
        with nav_next:
            if st.button("▶", key="cal_next_m", width="stretch"):
                if cm == 12:
                    st.session_state["cal_year"] = cy + 1
                    st.session_state["cal_month"] = 1
                else:
                    st.session_state["cal_month"] = cm + 1
                st.rerun()
        with nav_today:
            if st.button("Today", key="cal_go_today", width="stretch"):
                today_d = now_ist().date()
                st.session_state["selected_date"] = today_d
                st.session_state["cal_year"] = today_d.year
                st.session_state["cal_month"] = today_d.month
                st.rerun()

        st.markdown(
            '<div class="vp-cal-weekdays">'
            "<span>Mo</span><span>Tu</span><span>We</span><span>Th</span>"
            "<span>Fr</span><span>Sa</span><span>Su</span></div>",
            unsafe_allow_html=True,
        )

        month_counts = get_monthly_booking_counts(cy, cm)
        month_matrix = calendar.monthcalendar(cy, cm)

        for week in month_matrix:
            w_cols = st.columns(7, gap="small")
            for idx_d, day_num in enumerate(week):
                with w_cols[idx_d]:
                    if day_num == 0:
                        st.markdown("<div style='height:2.25rem;'></div>", unsafe_allow_html=True)
                    else:
                        d_obj = date(cy, cm, day_num)
                        d_iso = d_obj.strftime("%Y-%m-%d")
                        info = month_counts.get(d_iso)
                        is_sel = d_obj == selected_date_val

                        if info:
                            tip = f"{d_obj.strftime('%d %b %Y')}: {info['total']} booking(s)"
                            if info["pending"] > 0:
                                tip += f" ({info['pending']} pending approval)"
                        else:
                            tip = f"{d_obj.strftime('%d %b %Y')}: No bookings"

                        if is_sel:
                            btn_key = f"cal_sel_{d_iso}"
                            btn_type = "primary"
                        elif info and info["pending"] > 0:
                            btn_key = f"cal_pending_{d_iso}"
                            btn_type = "secondary"
                        elif info:
                            btn_key = f"cal_booked_{d_iso}"
                            btn_type = "secondary"
                        else:
                            btn_key = f"cal_open_{d_iso}"
                            btn_type = "secondary"

                        if st.button(
                            str(day_num),
                            key=btn_key,
                            type=btn_type,
                            help=tip,
                            width="stretch",
                        ):
                            st.session_state["selected_date"] = d_obj
                            st.rerun()

        st.markdown(
            f"""
            <div class="vp-cal-legend">
                <span class="vp-leg-item"><span class="vp-leg-swatch" style="background:#059669;"></span>Selected</span>
                <span class="vp-leg-item"><span class="vp-leg-swatch" style="background:#DCFCE7; border:1.5px solid #10B981;"></span>Booked</span>
                <span class="vp-leg-item"><span class="vp-leg-swatch" style="background:#ECFDF5; border:1.5px solid #F59E0B;"></span>Pending</span>
                <span><b>{len(month_counts)}</b> day(s) booked</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

with h_cta:
    if st.button("➕ Book a Venue", type="primary", width="stretch"):
        open_booking_dialog(st.session_state["selected_date"])

st.write("")

# ---------------------------------------------------------------------------
# 3 Simple, Clear Task-Based Tabs
# ---------------------------------------------------------------------------
pending_total = int(
    fetch_dataframe("SELECT COUNT(*) AS c FROM bookings WHERE status = 'Pending'").iloc[0]["c"]
)
approvals_label = f"📋 Approvals ({pending_total})" if pending_total > 0 else "📋 Approvals"

tab_halls, tab_approvals, tab_finder = st.tabs(
    [
        "🏛️ Halls & Today's Schedule",
        approvals_label,
        "🔍 Find a Slot & Analytics",
    ]
)


# ---------------------------------------------------------------------------
# TAB 1: HALLS & LIVE STATUS (Auto-Refreshes Every 3 Seconds)
# ---------------------------------------------------------------------------
@st.fragment(run_every="3s")
def render_live_halls_tab(target_date: str) -> None:
    now = now_ist()
    clock_display = now.strftime("%I:%M:%S %p IST")
    current_hm = now.strftime("%H:%M")
    is_today = target_date == now.strftime("%Y-%m-%d")

    bookings_df = fetch_dataframe(
        "SELECT * FROM bookings WHERE booking_date = ? ORDER BY start_time ASC",
        (target_date,),
    )
    venues_df = fetch_dataframe("SELECT * FROM venues ORDER BY id ASC")
    stock = get_equipment_stock()
    non_rejected = (
        bookings_df[bookings_df["status"] != "Rejected"] if not bookings_df.empty else pd.DataFrame()
    )

    if not non_rejected.empty and is_today:
        active_now = non_rejected[
            non_rejected["status"].isin(OCCUPANCY_STATUSES)
            & (non_rejected["start_time"] <= current_hm)
            & (non_rejected["end_time"] > current_hm)
        ]
    else:
        active_now = pd.DataFrame()

    used_tvs = int(active_now["smart_tv_qty"].sum()) if not active_now.empty else 0
    used_mics = int(active_now["mic_qty"].sum()) if not active_now.empty else 0
    pending_today = int((bookings_df["status"] == "Pending").sum()) if not bookings_df.empty else 0

    free_halls = len(venues_df) - len(active_now)
    free_tvs = max(0, stock["tv"] - used_tvs)
    free_mics = max(0, stock["mic"] - used_mics)

    # Top Live Strip
    top_l, top_r = st.columns([3, 1.4], vertical_alignment="center")
    with top_l:
        nice_date = datetime.strptime(target_date, "%Y-%m-%d").strftime("%A, %d %B %Y")
        st.markdown(
            f'<div class="vp-section-title">Live Campus Snapshot — {nice_date}</div>',
            unsafe_allow_html=True,
        )
    with top_r:
        st.markdown(
            f'<div style="text-align:right;"><span class="vp-live-pill">'
            f'<span class="vp-live-dot"></span>Live · {clock_display}</span></div>',
            unsafe_allow_html=True,
        )

    # 4 Simple, Easy-to-Read Summary Cards
    s1, s2, s3, s4 = st.columns(4, gap="medium")
    with s1:
        st.markdown(
            f"""
            <div class="vp-stat-card">
                <div class="vp-stat-label">Halls Available Now</div>
                <div class="vp-stat-value">{free_halls} <span style="font-size:1rem; color:{TEXT_SUB}; font-weight:500;">/ {len(venues_df)}</span></div>
                <div class="vp-stat-hint good">{len(active_now)} currently in use</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"""
            <div class="vp-stat-card">
                <div class="vp-stat-label">65" Smart TVs Ready</div>
                <div class="vp-stat-value">{free_tvs} <span style="font-size:1rem; color:{TEXT_SUB}; font-weight:500;">/ {stock['tv']}</span></div>
                <div class="vp-stat-hint">{used_tvs} deployed right now</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            f"""
            <div class="vp-stat-card">
                <div class="vp-stat-label">Wireless Mics Ready</div>
                <div class="vp-stat-value">{free_mics} <span style="font-size:1rem; color:{TEXT_SUB}; font-weight:500;">/ {stock['mic']}</span></div>
                <div class="vp-stat-hint">{used_mics} deployed right now</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s4:
        hint_cls = "warn" if pending_today > 0 else "good"
        hint_txt = "Needs coordinator review" if pending_today > 0 else "All requests reviewed"
        st.markdown(
            f"""
            <div class="vp-stat-card">
                <div class="vp-stat-label">Pending Requests</div>
                <div class="vp-stat-value">{pending_today}</div>
                <div class="vp-stat-hint {hint_cls}">{hint_txt}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(
        '<div class="vp-section-title">Campus Venues</div>'
        '<div class="vp-section-sub">Pick any hall below to reserve it instantly with automatic conflict protection.</div>',
        unsafe_allow_html=True,
    )

    # Spacious 3x2 Hall Cards with Direct "Book This Hall" Button
    v_records = venues_df.to_dict("records")
    for row_start in range(0, len(v_records), 3):
        cols = st.columns(3, gap="medium")
        for col_i, vr in enumerate(v_records[row_start : row_start + 3]):
            v_name = vr["name"]
            match = active_now[active_now["venue_name"] == v_name] if not active_now.empty else pd.DataFrame()
            with cols[col_i]:
                with st.container(key=f"hall_card_{vr['id']}"):
                    if not match.empty:
                        ev = match.iloc[0]
                        end_dt = datetime.strptime(f"{target_date} {ev['end_time']}", "%Y-%m-%d %H:%M")
                        mins_left = max(0, int((end_dt - now).total_seconds() // 60))
                        st.markdown(
                            f"""
                            <div class="vp-hall-header">
                                <div class="vp-hall-title">{html.escape(v_name)}</div>
                                <span class="vp-pill-busy">In Use · {mins_left}m left</span>
                            </div>
                            <div class="vp-hall-sub">{html.escape(vr['block'])} · Seats {vr['capacity']}</div>
                            <div class="vp-hall-info-box busy">
                                <div><strong>{html.escape(ev['event_title'])}</strong></div>
                                <div style="color:{TEXT_SUB}; margin-top:2px;">
                                    {ev['start_time']}–{ev['end_time']} · 📺 {int(ev['smart_tv_qty'])} TV · 🎤 {int(ev['mic_qty'])} Mic
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        next_line = "Open for bookings today"
                        if not non_rejected.empty:
                            up = non_rejected[
                                (non_rejected["venue_name"] == v_name)
                                & ((non_rejected["start_time"] > current_hm) if is_today else True)
                            ]
                            if not up.empty:
                                n0 = up.iloc[0]
                                next_line = f"Next: {n0['start_time']}–{n0['end_time']} ({n0['event_title']})"
                        st.markdown(
                            f"""
                            <div class="vp-hall-header">
                                <div class="vp-hall-title">{html.escape(v_name)}</div>
                                <span class="vp-pill-free">Available Now</span>
                            </div>
                            <div class="vp-hall-sub">{html.escape(vr['block'])} · Seats {vr['capacity']}</div>
                            <div class="vp-hall-info-box">
                                <div>{html.escape(vr['built_in_av'])}</div>
                                <div style="color:{TEXT_SUB}; margin-top:2px;">🗓️ {html.escape(next_line)}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    if st.button(f"Book {v_name}", key=f"book_btn_{vr['id']}", width="stretch"):
                        open_booking_dialog(st.session_state["selected_date"], preselected_venue=v_name)

    # Simple Today's Schedule Timeline Card
    st.write("")
    with st.container(key="timeline_card"):
        st.markdown(
            '<div class="vp-section-title" style="margin-top:0;">Today\'s Schedule Timeline</div>'
            '<div class="vp-section-sub">Hover over any booking block to see department and AV equipment details.</div>',
            unsafe_allow_html=True,
        )
        if non_rejected.empty:
            st.info("No bookings scheduled for this date yet. Click **➕ Book a Venue** above to add one.")
        else:
            plot_df = non_rejected.copy()
            plot_df["Start_DT"] = pd.to_datetime(plot_df["booking_date"] + " " + plot_df["start_time"])
            plot_df["End_DT"] = pd.to_datetime(plot_df["booking_date"] + " " + plot_df["end_time"])

            fig = px.timeline(
                plot_df,
                x_start="Start_DT",
                x_end="End_DT",
                y="venue_name",
                color="status",
                hover_data=["event_title", "department", "organizer", "smart_tv_qty", "mic_qty", "pa_system_qty"],
                color_discrete_map={
                    "Dispatched": "#1D4ED8",
                    "Approved": "#059669",
                    "Pending": "#F59E0B",
                    "Returned": "#94A3B8",
                },
            )
            fig.update_yaxes(autorange="reversed", title="")
            fig.update_xaxes(title="", showgrid=True, gridcolor="#F1F5F9")
            fig.update_layout(
                height=300,
                paper_bgcolor=CARD_BG,
                plot_bgcolor=CARD_BG,
                margin=dict(l=10, r=15, t=10, b=15),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


with tab_halls:
    render_live_halls_tab(date_str)


# ---------------------------------------------------------------------------
# TAB 2: SIMPLE COORDINATOR & IT APPROVALS
# ---------------------------------------------------------------------------
with tab_approvals:
    all_bookings = fetch_dataframe(
        "SELECT * FROM bookings ORDER BY booking_date DESC, start_time ASC"
    )

    st.markdown(
        '<div class="vp-section-title">Waiting for Approval</div>'
        '<div class="vp-section-sub">Review incoming booking requests and approve or decline in one click.</div>',
        unsafe_allow_html=True,
    )

    pending_df = all_bookings[all_bookings["status"] == "Pending"]
    if pending_df.empty:
        st.success("All caught up — no pending requests right now.")
    else:
        for _, row in pending_df.iterrows():
            c_info, c_yes, c_no = st.columns([4.2, 1, 1], vertical_alignment="center", gap="small")
            with c_info:
                st.markdown(
                    f"""
                    <div class="vp-req-card">
                        <div class="vp-req-title">
                            {html.escape(row['event_title'])}
                            <span class="vp-badge-pending">Pending</span>
                        </div>
                        <div class="vp-req-meta">
                            🏛️ <b>{html.escape(row['venue_name'])}</b> &nbsp;·&nbsp;
                            📅 {row['booking_date']} ({row['start_time']}–{row['end_time']}) &nbsp;·&nbsp;
                            👤 {html.escape(row['organizer'])} ({html.escape(row['department'])})<br/>
                            📺 {int(row['smart_tv_qty'])} Smart TVs &nbsp;·&nbsp;
                            🎤 {int(row['mic_qty'])} Mics &nbsp;·&nbsp;
                            🔊 {int(row['pa_system_qty'])} PA Systems
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_yes:
                if st.button("✅ Approve", key=f"ok_{row['id']}", type="primary", width="stretch"):
                    update_booking_status(int(row["id"]), "Approved")
                    st.toast(f"Approved: {row['event_title']}", icon="✅")
                    st.rerun()
            with c_no:
                if st.button("Decline", key=f"no_{row['id']}", width="stretch"):
                    update_booking_status(int(row["id"]), "Rejected")
                    st.toast(f"Declined: {row['event_title']}", icon="❌")
                    st.rerun()

    st.write("")
    st.markdown(
        '<div class="vp-section-title">Equipment Handover &amp; Returns</div>'
        '<div class="vp-section-sub">Track approved events as AV equipment is handed over and returned to the IT Store.</div>',
        unsafe_allow_html=True,
    )

    active_ops = all_bookings[all_bookings["status"].isin(["Approved", "Dispatched"])]
    if active_ops.empty:
        st.info("No active approved bookings awaiting AV handover.")
    else:
        for _, row in active_ops.iterrows():
            c_info, c_act, c_can = st.columns([4.2, 1.25, 0.85], vertical_alignment="center", gap="small")
            is_disp = row["status"] == "Dispatched"
            badge_html = (
                '<span class="vp-badge-dispatched">AV Dispatched</span>'
                if is_disp
                else '<span class="vp-badge-approved">Approved</span>'
            )
            with c_info:
                st.markdown(
                    f"""
                    <div class="vp-req-card">
                        <div class="vp-req-title">{html.escape(row['event_title'])}{badge_html}</div>
                        <div class="vp-req-meta">
                            🏛️ <b>{html.escape(row['venue_name'])}</b> &nbsp;·&nbsp;
                            📅 {row['booking_date']} ({row['start_time']}–{row['end_time']}) &nbsp;·&nbsp;
                            📺 {int(row['smart_tv_qty'])} TV · 🎤 {int(row['mic_qty'])} Mic · 🔊 {int(row['pa_system_qty'])} PA
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_act:
                if not is_disp:
                    if st.button("🚚 Hand Over AV", key=f"disp_{row['id']}", type="primary", width="stretch"):
                        update_booking_status(int(row["id"]), "Dispatched")
                        st.toast("Marked as AV Dispatched!", icon="🚚")
                        st.rerun()
                else:
                    if st.button("📦 Mark Returned", key=f"ret_{row['id']}", type="primary", width="stretch"):
                        update_booking_status(int(row["id"]), "Returned")
                        st.toast("Equipment marked Returned!", icon="📦")
                        st.rerun()
            with c_can:
                if st.button("Cancel", key=f"can_{row['id']}", width="stretch"):
                    update_booking_status(int(row["id"]), "Rejected")
                    st.rerun()

    st.write("")
    with st.expander("📄 View Complete Booking History & Download CSV"):
        st.dataframe(
            all_bookings[
                [
                    "id",
                    "event_title",
                    "venue_name",
                    "department",
                    "organizer",
                    "booking_date",
                    "start_time",
                    "end_time",
                    "smart_tv_qty",
                    "mic_qty",
                    "pa_system_qty",
                    "status",
                ]
            ],
            width="stretch",
            hide_index=True,
        )
        st.download_button(
            "⬇️ Download All Bookings (CSV)",
            data=all_bookings.to_csv(index=False).encode("utf-8"),
            file_name="bookings.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# TAB 3: FRIENDLY SLOT FINDER & SIMPLE ANALYTICS
# ---------------------------------------------------------------------------
with tab_finder:
    venues_df = fetch_dataframe("SELECT * FROM venues ORDER BY id ASC")
    stock = get_equipment_stock()
    day_df = fetch_dataframe(
        "SELECT * FROM bookings WHERE booking_date = ? AND status != 'Rejected'",
        (date_str,),
    )

    # Friendly Slot Finder
    with st.container(key="finder_card"):
        st.markdown(
            '<div class="vp-section-title" style="margin-top:0;">Find an Available Hall</div>'
            '<div class="vp-section-sub">Choose your preferred time and equipment — we\'ll instantly show which halls are open.</div>',
            unsafe_allow_html=True,
        )
        f1, f2, f3, f4 = st.columns([2.2, 1, 1, 1], gap="medium")
        with f1:
            time_win = st.slider(
                "Preferred Time Slot",
                min_value=time(8, 0),
                max_value=time(21, 0),
                value=(time(14, 0), time(16, 0)),
                step=timedelta(minutes=30),
                format="HH:mm",
            )
        with f2:
            need_tv = st.number_input('Smart TVs', 0, stock["tv"], 1, key="find_tv")
        with f3:
            need_mic = st.number_input("Wireless Mics", 0, stock["mic"], 2, key="find_mic")
        with f4:
            need_pa = st.number_input("PA Systems", 0, stock["pa"], 0, key="find_pa")

        s_win = time_win[0].strftime("%H:%M")
        e_win = time_win[1].strftime("%H:%M")
        if s_win >= e_win:
            st.warning("Please select an end time later than the start time.")
        else:
            slot = get_slot_availability(date_str, s_win, e_win)
            av_ok = (
                need_tv <= slot["avail_tv"]
                and need_mic <= slot["avail_mic"]
                and need_pa <= slot["avail_pa"]
            )
            if av_ok:
                st.success(
                    f"Equipment available for **{s_win}–{e_win}**: "
                    f"{slot['avail_tv']} Smart TVs · {slot['avail_mic']} Mics · {slot['avail_pa']} PA Systems free."
                )
            else:
                st.error(
                    f"Not enough movable equipment during **{s_win}–{e_win}** "
                    f"(Free: {slot['avail_tv']} TVs · {slot['avail_mic']} Mics · {slot['avail_pa']} PA)."
                )

            open_halls = [r["name"] for _, r in venues_df.iterrows() if r["name"] not in slot["occupied_venues"]]
            busy_halls = [r["name"] for _, r in venues_df.iterrows() if r["name"] in slot["occupied_venues"]]

            if open_halls:
                st.markdown("**Ready to Book:**")
                btn_cols = st.columns(min(3, len(open_halls)), gap="small")
                for idx_h, hname in enumerate(open_halls):
                    with btn_cols[idx_h % len(btn_cols)]:
                        if st.button(
                            f"✅ Book {hname} ({s_win}–{e_win})",
                            key=f"quick_find_{hname}",
                            width="stretch",
                        ):
                            open_booking_dialog(
                                st.session_state["selected_date"],
                                preselected_venue=hname,
                                default_start=time_win[0],
                                default_end=time_win[1],
                            )
            if busy_halls:
                st.caption("Already booked in this slot: " + ", ".join(busy_halls))

    st.write("")

    # 2 Clean, Simple Charts Side-by-Side
    ch1, ch2 = st.columns(2, gap="medium")
    with ch1:
        with st.container(key="chart_eq"):
            st.markdown(
                '<div class="vp-section-title" style="margin-top:0;">Movable AV Usage Today</div>'
                '<div class="vp-section-sub">Units reserved across all events vs. Central IT Store stock</div>',
                unsafe_allow_html=True,
            )
            booked_tv = int(day_df["smart_tv_qty"].sum()) if not day_df.empty else 0
            booked_mic = int(day_df["mic_qty"].sum()) if not day_df.empty else 0
            booked_pa = int(day_df["pa_system_qty"].sum()) if not day_df.empty else 0

            fig_eq = go.Figure(
                data=[
                    go.Bar(
                        name="Reserved Today",
                        x=['65" Smart TVs', "Wireless Mics", "PA Systems"],
                        y=[booked_tv, booked_mic, booked_pa],
                        marker_color=PRIMARY,
                    ),
                    go.Bar(
                        name="Total Store Stock",
                        x=['65" Smart TVs', "Wireless Mics", "PA Systems"],
                        y=[stock["tv"], stock["mic"], stock["pa"]],
                        marker_color="#CBD5E1",
                    ),
                ]
            )
            fig_eq.update_layout(
                barmode="group",
                height=265,
                paper_bgcolor=CARD_BG,
                plot_bgcolor=CARD_BG,
                margin=dict(l=10, r=10, t=10, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Units"),
            )
            st.plotly_chart(fig_eq, width="stretch", config={"displayModeBar": False})

    with ch2:
        with st.container(key="chart_hall"):
            st.markdown(
                '<div class="vp-section-title" style="margin-top:0;">Bookings by Venue</div>'
                '<div class="vp-section-sub">Number of active reservations per campus hall today</div>',
                unsafe_allow_html=True,
            )
            counts = [
                int((day_df["venue_name"] == vn).sum()) if not day_df.empty else 0
                for vn in venues_df["name"]
            ]
            fig_h = go.Figure(
                data=[
                    go.Bar(
                        y=venues_df["name"],
                        x=counts,
                        orientation="h",
                        marker_color="#0F172A",
                        text=counts,
                        textposition="outside",
                    )
                ]
            )
            fig_h.update_layout(
                height=265,
                paper_bgcolor=CARD_BG,
                plot_bgcolor=CARD_BG,
                margin=dict(l=10, r=24, t=10, b=20),
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", dtick=1, title="Bookings"),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_h, width="stretch", config={"displayModeBar": False})

    st.write("")
    with st.expander("⚙️ Demo & Evaluation Controls"):
        st.caption("Use these controls during a live demo or VIVA to simulate incoming requests or reset sample data.")
        d1, d2 = st.columns(2, gap="small")
        with d1:
            if st.button("⚡ Simulate Incoming Request", width="stretch"):
                ok, msg = simulate_incoming_request(date_str)
                if ok:
                    st.toast(msg, icon="⚡")
                    st.rerun()
                else:
                    st.warning(msg)
        with d2:
            if st.button("🔄 Reset Demo Data", width="stretch"):
                reset_demo_data()
                st.toast("Sample bookings reset for today!", icon="🔄")
                st.rerun()
