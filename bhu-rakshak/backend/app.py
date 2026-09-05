"""
app.py
------
BhuRakshak backend — AI-based Early Warning & Landslide Risk Monitoring System (NER)
SIH26001

Run with:
    uvicorn app:app --reload --port 8000

Then open:
    http://localhost:8000/docs   -> interactive API docs (Swagger UI)
    frontend/index.html          -> the dashboard (open directly in your browser)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import risk_score, alerts

app = FastAPI(
    title="BhuRakshak API",
    description="AI-based Early Warning & Landslide Risk Monitoring System for NER",
    version="1.0.0",
)

# Allow the frontend (opened as a local file or a different port) to call this API.
# For a real deployment, restrict allow_origins to your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_score.router, tags=["Risk Prediction"])
app.include_router(alerts.router, tags=["Zones & Alerts"])


@app.get("/")
def health_check():
    return {"status": "ok", "service": "BhuRakshak API", "docs": "/docs"}
