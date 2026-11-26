import random
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

IST = timezone(timedelta(hours=5, minutes=30))
DB_PATH = Path(__file__).resolve().parent / "christ_venues.db"


def now_ist() -> datetime:
    """Return current CHRIST University (IST, UTC+5:30) local time as naive datetime."""
    return datetime.now(IST).replace(tzinfo=None)

TV_ITEM_NAME = "65-inch Portable Smart TV (on Stand)"
MIC_ITEM_NAME = "Wireless UHF Collar & Hand Mics"
PA_ITEM_NAME = "Portable PA Sound System"

ACTIVE_HOLD_STATUSES = ("Approved", "Pending", "Dispatched")
OCCUPANCY_STATUSES = ("Approved", "Dispatched")

VENUES_SEED = [
    ("Room 105", "Central Block", 120, "Built-in Projector + Podium Mic"),
    ("Skyview", "Central Block (10th Floor)", 350, "Dual LED Wall + Surround Audio"),
    ("Main Auditorium", "Auditorium Block", 1200, "Stage Rig + Full Line Array"),
    ("Block II Seminar Hall", "Block II", 180, "Smart Board + Cordless Mics"),
    ("R&D Conference Room", "R&D Block", 60, "75-inch 4K Display + Video Conf"),
    ("Birds Park Open Stage", "Central Campus", 250, "Outdoor Power Points Only"),
]

EQUIPMENT_SEED = [
    (TV_ITEM_NAME, "Display", 8),
    (MIC_ITEM_NAME, "Audio", 15),
    (PA_ITEM_NAME, "Audio", 5),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _safe_live_window(now: datetime) -> tuple[str, str]:
    """Return a same-day (start_hm, end_hm) window containing `now` without midnight wrap."""
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = now.replace(hour=23, minute=59, second=0, microsecond=0)

    start_dt = max(day_start, now - timedelta(minutes=30))
    end_dt = min(day_end, now + timedelta(minutes=60))

    if end_dt <= start_dt:
        start_dt = max(day_start, day_end - timedelta(minutes=60))
        end_dt = day_end

    return start_dt.strftime("%H:%M"), end_dt.strftime("%H:%M")


def _seed_sample_bookings(cur: sqlite3.Cursor) -> None:
    now = now_ist()
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    plus3_str = (now + timedelta(days=3)).strftime("%Y-%m-%d")
    plus5_str = (now + timedelta(days=5)).strftime("%Y-%m-%d")
    created_ts = now.strftime("%Y-%m-%d %H:%M:%S")
    live_start, live_end = _safe_live_window(now)

    sample_bookings = [
        (
            "GATEWAYS 2026 Core Committee Briefing",
            "Dept. of Computer Science",
            "Iwin Jose (2647126)",
            "Room 105",
            today_str,
            live_start,
            live_end,
            2,
            3,
            1,
            "Dispatched",
            created_ts,
        ),
        (
            "24° Shift Hackathon Tech Dry-Run",
            "Dept. of Computer Science",
            "Hackathon Organizers",
            "Skyview",
            today_str,
            "14:00",
            "17:00",
            4,
            4,
            1,
            "Approved",
            created_ts,
        ),
        (
            "Guest Lecture: Cloud Native Security",
            "Dept. of Computer Science",
            "Faculty Coordinator",
            "Block II Seminar Hall",
            today_str,
            "11:00",
            "13:00",
            1,
            2,
            0,
            "Pending",
            created_ts,
        ),
        (
            "Placement Pre-Talk: Cloud & AI Engineering",
            "Placement Cell",
            "Placement Officer",
            "Main Auditorium",
            today_str,
            "09:30",
            "11:30",
            1,
            4,
            2,
            "Approved",
            created_ts,
        ),
        (
            "CSA Orientation & Volunteer Meet",
            "CSA (Centre for Social Action)",
            "CSA Student Lead",
            "Birds Park Open Stage",
            today_str,
            "16:30",
            "18:30",
            0,
            3,
            1,
            "Pending",
            created_ts,
        ),
        (
            "MCA AI & Cloud Mini-Symposium",
            "Dept. of Computer Science",
            "Faculty Coordinator",
            "Skyview",
            tomorrow_str,
            "10:00",
            "13:00",
            3,
            4,
            1,
            "Approved",
            created_ts,
        ),
        (
            "SWO Inter-Department Debate Prelims",
            "SWO (Student Welfare Office)",
            "SWO Cultural Team",
            "Room 105",
            plus3_str,
            "14:00",
            "16:30",
            1,
            3,
            1,
            "Pending",
            created_ts,
        ),
        (
            "GATEWAYS 2026 Inauguration Rehearsal",
            "Dept. of Computer Science",
            "Iwin Jose (2647126)",
            "Main Auditorium",
            plus5_str,
            "11:00",
            "14:00",
            4,
            6,
            2,
            "Approved",
            created_ts,
        ),
    ]

    cur.executemany(
        """
        INSERT INTO bookings (
            event_title, department, organizer, venue_name, booking_date,
            start_time, end_time, smart_tv_qty, mic_qty, pa_system_qty, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        sample_bookings,
    )


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS venues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            block TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            built_in_av TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            total_stock INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_title TEXT NOT NULL,
            department TEXT NOT NULL,
            organizer TEXT NOT NULL,
            venue_name TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            smart_tv_qty INTEGER DEFAULT 0,
            mic_qty INTEGER DEFAULT 0,
            pa_system_qty INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute("SELECT COUNT(*) FROM venues")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO venues (name, block, capacity, built_in_av) VALUES (?, ?, ?, ?)",
            VENUES_SEED,
        )

    cur.execute("SELECT COUNT(*) FROM equipment")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO equipment (item_name, category, total_stock) VALUES (?, ?, ?)",
            EQUIPMENT_SEED,
        )

    today_str = now_ist().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM bookings WHERE booking_date = ?", (today_str,))
    if cur.fetchone()[0] == 0:
        _seed_sample_bookings(cur)

    conn.commit()
    conn.close()


def reset_demo_data() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM bookings")
    cur.execute("DELETE FROM sqlite_sequence WHERE name = 'bookings'")
    _seed_sample_bookings(cur)
    conn.commit()
    conn.close()


def get_equipment_stock() -> dict[str, int]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT item_name, total_stock FROM equipment").fetchall()
    conn.close()
    stock_map = {row["item_name"]: int(row["total_stock"]) for row in rows}
    return {
        "tv": stock_map.get(TV_ITEM_NAME, 8),
        "mic": stock_map.get(MIC_ITEM_NAME, 15),
        "pa": stock_map.get(PA_ITEM_NAME, 5),
    }


def get_slot_availability(booking_date: str, start_time: str, end_time: str) -> dict:
    """Return remaining movable equipment stock and occupied venues for a given time window."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM bookings
        WHERE booking_date = ?
          AND status IN ('Approved', 'Pending', 'Dispatched')
          AND (? < end_time AND ? > start_time)
        """,
        (booking_date, start_time, end_time),
    )
    overlapping = cur.fetchall()
    conn.close()

    totals = get_equipment_stock()
    used_tv = sum(int(row["smart_tv_qty"]) for row in overlapping)
    used_mic = sum(int(row["mic_qty"]) for row in overlapping)
    used_pa = sum(int(row["pa_system_qty"]) for row in overlapping)

    return {
        "overlapping_rows": overlapping,
        "occupied_venues": {row["venue_name"]: row for row in overlapping},
        "avail_tv": max(0, totals["tv"] - used_tv),
        "avail_mic": max(0, totals["mic"] - used_mic),
        "avail_pa": max(0, totals["pa"] - used_pa),
        "total_tv": totals["tv"],
        "total_mic": totals["mic"],
        "total_pa": totals["pa"],
    }


def check_conflicts_and_stock(
    venue_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    req_tv: int,
    req_mic: int,
    req_pa: int,
) -> tuple[bool, str]:
    """
    Validates:
    1. Time ordering: NewStart < NewEnd
    2. Venue double-booking using interval overlap: (NewStart < ExistingEnd) AND (NewEnd > ExistingStart)
    3. Movable equipment pool availability during the exact requested time window.
    """
    if start_time >= end_time:
        return False, "Invalid Time Window: End time must be strictly after Start time."

    slot = get_slot_availability(booking_date, start_time, end_time)

    if venue_name in slot["occupied_venues"]:
        existing = slot["occupied_venues"][venue_name]
        return (
            False,
            f"Venue Clash: '{venue_name}' is already reserved for '{existing['event_title']}' "
            f"({existing['start_time']}–{existing['end_time']}, status: {existing['status']}).",
        )

    if req_tv > slot["avail_tv"]:
        return (
            False,
            f"Equipment Shortage: Only {slot['avail_tv']} of {slot['total_tv']} Smart TV(s) "
            f"available between {start_time} and {end_time}.",
        )
    if req_mic > slot["avail_mic"]:
        return (
            False,
            f"Equipment Shortage: Only {slot['avail_mic']} of {slot['total_mic']} Wireless Mic(s) "
            f"available between {start_time} and {end_time}.",
        )
    if req_pa > slot["avail_pa"]:
        return (
            False,
            f"Equipment Shortage: Only {slot['avail_pa']} of {slot['total_pa']} PA System(s) "
            f"available between {start_time} and {end_time}.",
        )

    return True, "Slot and movable AV equipment verified available!"


def add_booking(
    event_title: str,
    department: str,
    organizer: str,
    venue_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    tv_qty: int,
    mic_qty: int,
    pa_qty: int,
    status: str = "Pending",
) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bookings (
            event_title, department, organizer, venue_name, booking_date,
            start_time, end_time, smart_tv_qty, mic_qty, pa_system_qty, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_title.strip(),
            department,
            organizer.strip(),
            venue_name,
            booking_date,
            start_time,
            end_time,
            int(tv_qty),
            int(mic_qty),
            int(pa_qty),
            status,
            now_ist().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    booking_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(booking_id)


def update_booking_status(booking_id: int, new_status: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, int(booking_id)))
    conn.commit()
    conn.close()


def simulate_incoming_request(target_date: str) -> tuple[bool, str]:
    """Generate and insert a realistic non-conflicting incoming booking request for live demos."""
    templates = [
        ("MCA Project Review Panel", "Dept. of Computer Science", "Dr. Faculty Panel"),
        ("CAPS Technical Writing Workshop", "CAPS (Centre for Academic & Professional Support)", "CAPS Mentor Team"),
        ("SWO Fest Stage Coordination", "SWO (Student Welfare Office)", "SWO Student Council"),
        ("FinTech Case Study Pitch", "Dept. of Commerce & Management", "Commerce Association"),
        ("AI Research Colloquium", "Dept. of Computer Science", "R&D Research Cell"),
        ("Mock Interview Drive", "Placement Cell", "Student Placement Reps"),
    ]
    candidate_slots = [
        ("08:00", "09:30"),
        ("09:00", "11:00"),
        ("10:00", "12:00"),
        ("12:00", "13:30"),
        ("13:30", "15:00"),
        ("15:00", "16:30"),
        ("17:00", "19:00"),
        ("18:30", "20:00"),
    ]
    venue_names = [v[0] for v in VENUES_SEED]
    random.shuffle(venue_names)
    random.shuffle(candidate_slots)
    random.shuffle(templates)

    for s_time, e_time in candidate_slots:
        for venue in venue_names:
            slot = get_slot_availability(target_date, s_time, e_time)
            if venue in slot["occupied_venues"]:
                continue
            req_tv = min(random.randint(0, 2), slot["avail_tv"])
            req_mic = min(random.randint(1, 3), slot["avail_mic"])
            req_pa = min(random.randint(0, 1), slot["avail_pa"])
            title, dept, org = templates[0]
            booking_id = add_booking(
                title,
                dept,
                org,
                venue,
                target_date,
                s_time,
                e_time,
                req_tv,
                req_mic,
                req_pa,
                status="Pending",
            )
            return True, f"Simulated Request #{booking_id}: '{title}' for {venue} ({s_time}–{e_time})."

    return False, "All campus venues are fully booked across standard slots for this date."


def get_monthly_booking_counts(year: int, month: int) -> dict[str, dict[str, int]]:
    """Return per-date booking summary {'total', 'pending', 'confirmed'} for a given YYYY-MM."""
    prefix = f"{year:04d}-{month:02d}-%"
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT booking_date,
               COUNT(*) AS total,
               SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending,
               SUM(CASE WHEN status IN ('Approved', 'Dispatched', 'Returned') THEN 1 ELSE 0 END) AS confirmed
        FROM bookings
        WHERE booking_date LIKE ? AND status != 'Rejected'
        GROUP BY booking_date
        """,
        (prefix,),
    ).fetchall()
    conn.close()
    return {
        r["booking_date"]: {
            "total": int(r["total"]),
            "pending": int(r["pending"] or 0),
            "confirmed": int(r["confirmed"] or 0),
        }
        for r in rows
    }


def fetch_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df
