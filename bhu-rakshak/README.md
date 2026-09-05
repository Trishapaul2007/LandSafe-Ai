# BhuRakshak — AI-Based Early Warning & Landslide Risk Monitoring System (NER)
### SIH26001

A working prototype: a FastAPI backend serving a landslide-risk ML model, plus a
browser dashboard showing live risk levels, an interactive map, and simulated alerts.

## What's included

```
bhu-rakshak/
├── backend/
│   ├── app.py                  # FastAPI app entry point
│   ├── routes/
│   │   ├── risk_score.py       # POST /predict
│   │   └── alerts.py           # GET /zones, GET /alerts
│   ├── services/
│   │   ├── ml_predict.py       # Loads/trains the risk model
│   │   └── sms_gateway.py      # Simulated SMS/alert dispatch
│   ├── models/                 # Put your trained .pkl files here (optional)
│   └── requirements.txt
└── frontend/
    ├── index.html              # Dashboard UI
    ├── style.css
    └── app.js                  # Calls the backend API, renders map + cards
```

## 1. Install VS Code (if you haven't)

Download from https://code.visualstudio.com — then **File > Open Folder** and pick
this `bhu-rakshak` folder. Install the "Python" extension when VS Code suggests it.

## 2. Run the backend

Open a terminal in VS Code (`` Ctrl+` ``) and run:

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

You should see something like:
```
[ml_predict] No trained model found — training a fallback model on synthetic data.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

That's expected the first time — it auto-trains a model on synthetic data so the API
works immediately. Visit **http://localhost:8000/docs** to see and test the API directly.

### Using your real trained model instead

If you trained a model in the Colab notebook (`BhuRakshak_Landslide_Risk_Prototype.ipynb`):
1. Download `landslide_risk_model.pkl` and `landslide_scaler.pkl` from Colab
2. Put both files in `backend/models/`
3. Restart `uvicorn` — it will load them instead of training a fallback

## 3. Open the dashboard

With the backend still running, just open `frontend/index.html` directly in your
browser (double-click it, or right-click → "Open with Live Server" if you have that
VS Code extension installed).

You should see:
- A map of NER with color-coded risk markers for sample zones
- Zone cards showing current readings and risk level
- A form to test the model with your own custom readings
- An alert log that fills in automatically when any zone is High/Critical risk

Click **"🔄 Refresh Readings"** to simulate a new sensor update round.

## Notes / honest limitations

- **Zone readings are simulated** (small random jitter each refresh) — there are no
  real IoT sensors or satellite feeds connected yet.
- **Alerts are simulated** — they're logged and shown in the dashboard, but no real
  SMS is sent. See the comment in `services/sms_gateway.py` for how to plug in Twilio.
- This is enough to **demo the full data flow** end-to-end (sensor reading → ML model
  → risk score → alert → dashboard), which is what matters for a hackathon prototype.
