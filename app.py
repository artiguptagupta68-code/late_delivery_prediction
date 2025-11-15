import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime
import math
# Load Model
# -------------------------
MODEL_PATH = "late_delivery_predictor_model.pkl"

try:
    model_pipeline = joblib.load(MODEL_PATH)
except Exception as e:
    st.error(f"❌ Model could NOT be loaded!\nError: {e}")
    st.stop()

st.success("Model loaded successfully ✔")


# -------------------------
# API Keys (YOUR keys)
# -------------------------
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_KEY"
HERE_API_KEY = "YOUR_HERE_API_KEY"


# -------------------------
# Helper Functions
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = (
        np.sin((lat2 - lat1) / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    )
    return R * 2 * np.arcsin(np.sqrt(a))


def fetch_realtime_weather(lat, lon):
    if WEATHER_API_KEY == "YOUR_OPENWEATHERMAP_KEY":
        return 25.0, "Clear", 4.0

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        data = r.json()

        temp = data["main"]["temp"]
        weather_main = data["weather"][0]["main"]
        wind = data["wind"]["speed"]

        return temp, weather_main, wind

    except:
        return 25.0, "Clear", 4.0


def fetch_live_traffic_time(rest_lat, rest_lon, del_lat, del_lon):
    if HERE_API_KEY == "YOUR_HERE_API_KEY":
        return None, None

    try:
        url = "https://router.hereapi.com/v8/routes"
        params = {
            "transportMode": "car",
            "origin": f"{rest_lat},{rest_lon}",
            "destination": f"{del_lat},{del_lon}",
            "routingMode": "fast",
            "trafficMode": "realtime",
            "return": "summary",
            "apiKey": HERE_API_KEY,
        }
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        summary = data["routes"][0]["sections"][0]["summary"]

        return summary["duration"] / 60, summary["baseDuration"] / 60

    except:
        return None, None




# -------------------------
# Streamlit UI
# -------------------------
st.title("🚚 Late Delivery Prediction Dashboard")
st.markdown("Enter details to predict whether a delivery will be **late or on time**.")

col1, col2 = st.columns(2)

with col1:
    rest_lat = st.number_input("Restaurant Latitude", 28.50, 28.80, 28.60)
    rest_lon = st.number_input("Restaurant Longitude", 77.10, 77.40, 77.20)
    prep_time = st.slider("Preparation Time (min)", 5, 60, 20)
    rest_rating = st.slider("Restaurant Rating", 1.0, 5.0, 4.2)

with col2:
    del_lat = st.number_input("Delivery Latitude", 28.50, 28.80, 28.70)
    del_lon = st.number_input("Delivery Longitude", 77.10, 77.40, 77.25)
    del_rating = st.slider("Delivery Person Rating", 1.0, 5.0, 4.9)


if st.button("Predict Late Delivery 🚀"):

    distance = haversine(rest_lat, rest_lon, del_lat, del_lon)
    now = datetime.now()
    hr = now.hour
    sin_hr = math.sin(2 * math.pi * hr / 24)
    cos_hr = math.cos(2 * math.pi * hr / 24)

    temp, weather_main, wind = fetch_realtime_weather(del_lat, del_lon)

    t_live, t_base = fetch_live_traffic_time(rest_lat, rest_lon, del_lat, del_lon)

    # --- Fallback traffic simulation ---
    if t_live is None:
        if 17 <= hr <= 21:
            traffic_density = "Jam"
        elif 12 <= hr <= 14:
            traffic_density = "High"
        elif 8 <= hr <= 10:
            traffic_density = "Medium"
        else:
            traffic_density = "Low"
    else:
        ratio = t_live / t_base
        if ratio >= 1.5:
            traffic_density = "Jam"
        elif ratio >= 1.25:
            traffic_density = "High"
        elif ratio >= 1.05:
            traffic_density = "Medium"
        else:
            traffic_density = "Low"

    # --- Model Input ---
    input_df = pd.DataFrame({
        "delivery_distance_km": [distance],
        "preparation_time_min": [prep_time],
        "restaurant_rating": [rest_rating],
        "delivery_person_rating": [del_rating],
        "Road_Traffic_Density": [traffic_density],
        "Weather_Condition": [weather_main],
        "sin_hour": [sin_hr],
        "cos_hour": [cos_hr],
        "current_temp_c": [temp],
    })

    try:
        late_prob = model_pipeline.predict_proba(input_df)[0][1] * 100
        st.subheader(f"📊 Late Delivery Probability: **{late_prob:.2f}%**")

        if late_prob > 60:
            st.error("❗ High Risk of Being LATE")
        elif late_prob > 40:
            st.warning("⚠️ Medium Risk of Late")
        else:
            st.success("✅ Low Risk of Late Delivery")

    except Exception as e:
        st.error(f"Prediction Failed: {e}")

        import requests
def get_location_name(lat, lon):
    """
    Returns a human-readable location name from latitude and longitude.
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', f"{lat},{lon}")
        else:
            return f"{lat},{lon}"
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
        return f"{lat},{lon}"

import streamlit as st

# Inputs (keep these as numeric inputs for calculations)
rest_lat = st.number_input("Restaurant Latitude", value=28.60)
rest_lon = st.number_input("Restaurant Longitude", value=77.19)
del_lat = st.number_input("Delivery Latitude", value=28.70)
del_lon = st.number_input("Delivery Longitude", value=77.25)

# Convert lat/lon to readable locations
restaurant_location_name = get_location_name(rest_lat, rest_lon)
delivery_location_name = get_location_name(del_lat, del_lon)

# Show locations
st.write(f"Restaurant Location: {restaurant_location_name}")
st.write(f"Delivery Location: {delivery_location_name}")

