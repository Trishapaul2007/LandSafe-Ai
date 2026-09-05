import random

from fastapi import APIRouter

from services.ml_predict import predict_risk
from services.sms_gateway import send_alert, get_alert_log

router = APIRouter()

# Sample monitored zones across NER, with base terrain readings.
# In production these would come from real IoT sensors + satellite feeds per zone,
# refreshed continuously instead of being hardcoded here.
MONITORED_ZONES = [
    {
        "id": "sohra",
        "name": "Sohra (Cherrapunji), Meghalaya",
        "lat": 25.2701,
        "lon": 91.7211,
        "base_reading": {
            "rainfall_mm": 190, "slope_angle": 46, "soil_moisture_pct": 88,
            "elevation_m": 1490, "distance_to_fault_km": 0.9,
            "prev_landslide_count": 3, "vegetation_cover_pct": 35,
        },
    },
    {
        "id": "aizawl",
        "name": "Aizawl, Mizoram",
        "lat": 23.7271,
        "lon": 92.7176,
        "base_reading": {
            "rainfall_mm": 90, "slope_angle": 34, "soil_moisture_pct": 55,
            "elevation_m": 1130, "distance_to_fault_km": 3.5,
            "prev_landslide_count": 1, "vegetation_cover_pct": 50,
        },
    },
    {
        "id": "imphal",
        "name": "Imphal Hills, Manipur",
        "lat": 24.8170,
        "lon": 93.9368,
        "base_reading": {
            "rainfall_mm": 38, "slope_angle": 19, "soil_moisture_pct": 30,
            "elevation_m": 780, "distance_to_fault_km": 6.0,
            "prev_landslide_count": 0, "vegetation_cover_pct": 70,
        },
    },
    {
        "id": "guwahati_hills",
        "name": "Guwahati Hills, Assam",
        "lat": 26.1445,
        "lon": 91.7362,
        "base_reading": {
            "rainfall_mm": 70, "slope_angle": 28, "soil_moisture_pct": 48,
            "elevation_m": 250, "distance_to_fault_km": 4.2,
            "prev_landslide_count": 1, "vegetation_cover_pct": 55,
        },
    },
]


def _jitter(value: float, pct: float = 0.08) -> float:
    """Adds small random variation so repeated calls look like live sensor updates."""
    return round(value * (1 + random.uniform(-pct, pct)), 2)


@router.get("/zones")
def get_zones_with_risk():
    """
    Returns every monitored zone with a freshly computed risk score.
    Base readings are jittered slightly each call to simulate live sensor updates.
    Automatically logs a simulated alert for any zone at High/Critical risk.
    """
    results = []
    for zone in MONITORED_ZONES:
        reading = {k: _jitter(v) if isinstance(v, float) else v for k, v in zone["base_reading"].items()}
        prob, level = predict_risk(**reading)

        if level in ("High", "Critical"):
            send_alert(zone["name"], level, prob)

        results.append({
            "id": zone["id"],
            "name": zone["name"],
            "lat": zone["lat"],
            "lon": zone["lon"],
            "reading": reading,
            "risk_probability": prob,
            "risk_level": level,
        })
    return {"zones": results}


@router.get("/alerts")
def get_alerts():
    """Returns the alert log generated so far this session (most recent first)."""
    return {"alerts": get_alert_log()}
