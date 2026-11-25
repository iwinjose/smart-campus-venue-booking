# 🚀 Free Hosting & Deployment Guide — VenuePulse

This guide walks you through hosting **VenuePulse – Real-Time Campus Venue & AV Equipment Allocation Dashboard** completely **for free** (no credit card required).

All required deployment files are already configured in this repository:

| File | Purpose |
| :--- | :--- |
| `app.py` | Main Streamlit entry point (`@st.fragment(run_every="3s")` live dashboard) |
| `database.py` | Zero-config SQLite3 database with automatic daily IST seeding |
| `requirements.txt` | Python package dependencies (`streamlit`, `plotly`, `pandas`) |
| `.streamlit/config.toml` | Custom emerald-and-white theme & headless server settings |
| `.python-version` | Pins Python `3.11` for cloud build environments |
| `Dockerfile` & `.dockerignore` | Ready-to-run container for Hugging Face Spaces / Render / Fly.io |
| `render.yaml` | One-click Blueprint configuration for Render.com Free Web Service |
| `.gitignore` | Prevents committing `.venv/`, cache files, and local `.db` files |

---

## Step 0: Push Your Project to GitHub (Required for All Platforms)

1. Go to [github.com/new](https://github.com/new) and create a **public** repository named `smart-campus-venue-booking` (do **not** initialize with a README).
2. Open PowerShell in your project folder (`smart-campus-venue-booking`) and run:

```powershell
git init
git add .
git commit -m "Deploy-ready VenuePulse CHRIST Campus Dashboard"
git branch -M main
git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/smart-campus-venue-booking.git
git push -u origin main
```

> **Note:** Replace `<YOUR-GITHUB-USERNAME>` with your actual GitHub username.

---

## Option 1: Streamlit Community Cloud (Recommended & Best for CIA 3)

**Cost:** 100% Free forever · **Credit Card:** Not required · **Setup Time:** ~2 minutes

1. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with your **GitHub** account.
2. Click **Create app** → **Yup, I have an app** (Deploy a public app from GitHub).
3. Fill in the deployment form:
   - **Repository:** `<YOUR-GITHUB-USERNAME>/smart-campus-venue-booking`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** e.g., `christ-venuepulse.streamlit.app`
4. Click **Advanced settings** → ensure **Python version** is set to **3.11** (matches `.python-version`).
5. Click **Deploy!**

Within 1–2 minutes, your app will be live at `https://<your-app-name>.streamlit.app`.

### Auto-Updates
Any future `git push` to `main` automatically rebuilds and updates your live Streamlit Cloud app.

---

## Option 2: Hugging Face Spaces (Free Backup — Generous 16 GB RAM)

**Cost:** 100% Free · **Credit Card:** Not required · **Uses:** Included `Dockerfile`

1. Create a free account at **[huggingface.co](https://huggingface.co)**.
2. Click **+ New** → **Space**.
3. Configure your Space:
   - **Space name:** `venuepulse-christ`
   - **SDK:** Choose **Docker** → **Blank**
   - **Hardware:** `CPU basic (2 vCPU · 16 GB RAM) — Free`
   - **Visibility:** Public
4. In your Space's `README.md` YAML frontmatter, set `app_port: 8501`:
   ```yaml
   ---
   title: VenuePulse CHRIST Campus
   emoji: 🏛️
   colorFrom: green
   colorTo: gray
   sdk: docker
   app_port: 8501
   ---
   ```
5. Push this repo to your Hugging Face Space Git remote (or upload `app.py`, `database.py`, `requirements.txt`, `Dockerfile`, `.dockerignore`, and `.streamlit/config.toml` directly via **Files → Add file**).
6. Hugging Face automatically builds the `Dockerfile` and serves your live URL.

---

## Option 3: Render.com Free Web Service (One-Click Blueprint)

**Cost:** Free tier · **Uses:** Included `render.yaml`

1. Sign in at **[dashboard.render.com](https://dashboard.render.com)** with GitHub.
2. Click **New +** → **Blueprint**.
3. Connect your `smart-campus-venue-booking` GitHub repository.
4. Render automatically reads `render.yaml`, installs `requirements.txt`, and launches Streamlit bound to `$PORT`.
5. Click **Apply** and wait ~2 minutes for your `https://venuepulse-christ-campus.onrender.com` URL.

> **Free Tier Note:** Render's free tier spins down after 15 minutes of inactivity and takes ~30–50 seconds to wake on the first visit. For instant live evaluations, **Option 1 (Streamlit Community Cloud)** is fastest.

---

## ⚙️ Cloud Features Built Into VenuePulse

- **Automatic IST Timezone Sync (`UTC+5:30`):** Cloud servers run in UTC, so `database.py` and `app.py` use `now_ist()` to guarantee the live clock, operations date, and active hall countdown timers always reflect **CHRIST University (Bengaluru)** local time.
- **Zero-Config Daily Auto-Seeding:** Whenever the app boots or rolls over to a new day, `init_db()` automatically seeds fresh live sample events for *today's date* if none exist, ensuring evaluators always see active live telemetry immediately.
- **SQLite Ephemeral Storage Note:** Free cloud containers reset local disk files (`christ_venues.db`) after reboots/redeploys. All live bookings made during a session persist across clicks and refreshes, and you can export the full booking ledger anytime using the **⬇️ Export CSV** button.

---

## ✅ Pre-Submission Verification Checklist

- [ ] Code pushed cleanly to a **public** GitHub repository (`.venv/` and `*.db` excluded by `.gitignore`).
- [ ] Live app opens without errors on Streamlit Community Cloud.
- [ ] Test **➕ Quick Book** modal (try booking `Skyview` at `14:30–16:00` to verify live conflict blocking).
- [ ] Test **✅ Approve** inside **Pending IT Approvals** and watch the top 4-stage progress ring update live.
- [ ] Test **Interactive Gantt & What-If** sliders.
- [ ] Submit both the **GitHub repository URL** and **Streamlit Cloud live URL**.
