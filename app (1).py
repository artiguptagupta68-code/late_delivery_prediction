import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime
from math import radians, sin, cos, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * R

def get_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        weather = data["weather"][0]["main"]
        temp = data["main"]["temp"]
        if weather in ['Clear']:
            condition = "Clear"
        elif weather in ['Rain']:
            condition = "Rain"
        elif weather in ['Thunderstorm', 'Heavy Rain']:
            condition = "Heavy Rain"
        elif weather == "Snow":
            condition = "Snow"
        else:
            condition = "Fog"
        return condition, temp
    except:
        return "Clear", 25

def estimate_traffic(hour):
    if hour in [7, 8, 9, 17, 18, 19]:
        return "High"
    elif hour in [10, 11, 12, 16]:
        return "Moderate"
    else:
        return "Low"

@st.cache_resource
def load_model():
    return joblib.load("delivery_predictor_model.pkl")

model = load_model()

st.title("🚚 AI-Powered Late Delivery Prediction System")
st.write("This app predicts whether a delivery will be late using weather, traffic and geo-location.")

st.sidebar.header("Delivery Input Details")

city = st.sidebar.text_input("City", "Delhi")
api_key = st.sidebar.text_input("OpenWeatherMap API Key", "YOUR_API_KEY_HERE")

restaurant_lat = st.sidebar.number_input("Restaurant Latitude", value=28.6139)
restaurant_lon = st.sidebar.number_input("Restaurant Longitude", value=77.2090)

delivery_lat = st.sidebar.number_input("Delivery Latitude", value=28.7041)
delivery_lon = st.sidebar.number_input("Delivery Longitude", value=77.1025)

rest_rating = st.sidebar.slider("Restaurant Rating", 3.0, 5.0, 4.2)
restaurant_id = st.sidebar.selectbox("Restaurant Name", ["Pizza Palace", "Sushi Spot", "Burger Barn", "Vegan Vibes"])
cuisine_type = st.sidebar.selectbox("Cuisine Type", ["Italian", "Japanese", "American", "Healthy"])

weather_condition, temperature_c = get_weather(city, api_key)

hour_now = datetime.now().hour
traffic_intensity = estimate_traffic(hour_now)

distance_km = haversine_distance(restaurant_lat, restaurant_lon, delivery_lat, delivery_lon)
day_of_week = datetime.now().weekday()
is_weekend = 1 if day_of_week >= 5 else 0

input_data = pd.DataFrame([{
    "distance_km": distance_km,
    "rest_rating": rest_rating,
    "temperature_c": temperature_c,
    "restaurant_id": restaurant_id,
    "cuisine_type": cuisine_type,
    "weather_condition": weather_condition,
    "traffic_intensity": traffic_intensity,
    "hour_of_day": hour_now,
    "day_of_week": day_of_week,
    "is_weekend": is_weekend
}])

if st.button("Predict Delivery Status"):
    prediction = model.predict(input_data)[0]
    prob = model.predict_proba(input_data)[0][1]

    st.subheader("Prediction Result")
    if prediction == 1:
        st.error("⚠️ Delivery is likely to be LATE")
    else:
        st.success("✅ Delivery is likely to be ON TIME")

    st.write(f"Probability of being Late: {prob*100:.2f}%")

st.subheader("Live Conditions")
st.write(f"Weather: {weather_condition}")
st.write(f"Temperature: {temperature_c} °C")
st.write(f"Traffic: {traffic_intensity}")
st.write(f"Distance: {distance_km:.2f} km")
