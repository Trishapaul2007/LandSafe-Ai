"""
sms_gateway.py
--------------
Simulated alert dispatch. Logs alerts to the console instead of sending real SMS,
so the backend runs with zero external accounts/keys needed for a demo.

To send REAL SMS in production, sign up for Twilio (or similar) and replace the
body of send_alert() with something like:

    from twilio.rest import Client
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=message, from_=TWILIO_NUMBER, to=to_number)
"""

from datetime import datetime

# In-memory log of alerts sent this session (demo purposes only — use a real DB in production)
alert_log = []


def send_alert(location_name: str, risk_level: str, risk_prob: float) -> dict:
    """Simulates sending an SMS/app alert for a High or Critical risk zone."""
    message = (
        f"[ALERT - {risk_level.upper()} RISK] {location_name}: "
        f"landslide risk probability {risk_prob * 100:.0f}%. "
        f"Follow local disaster authority guidance and avoid the area."
    )
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "location": location_name,
        "risk_level": risk_level,
        "risk_probability": risk_prob,
        "message": message,
    }
    alert_log.append(entry)
    print(f"📡 SMS/App Alert Sent -> {message}")
    return entry


def get_alert_log():
    """Returns all alerts sent this session, most recent first."""
    return list(reversed(alert_log))
