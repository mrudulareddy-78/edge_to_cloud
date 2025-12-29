import json
import streamlit as st

st.set_page_config(page_title="Industrial Defect Dashboard")
st.title("📊 Industrial Defect Monitoring Dashboard")

LOG_FILE = "cloud_log.json"
ALERT_FILE = "alerts.log"

def get_latest_event():
    try:
        with open(LOG_FILE) as f:
            lines = f.readlines()
            return json.loads(lines[-1]) if lines else None
    except:
        return None

def get_alert_count():
    try:
        with open(ALERT_FILE) as f:
            return len(f.readlines())
    except:
        return 0

data = get_latest_event()

if data is None:
    st.info("Waiting for edge data...")
else:
    st.metric("Device ID", data["device_id"])
    st.metric("Defect Type", data["defect"])
    st.metric("Severity", data["severity"])
    st.metric("Confidence", round(data["confidence"], 3))
    st.metric("Total Alerts", get_alert_count())
    st.text(f"Processed at: {data['processed_at']}")
