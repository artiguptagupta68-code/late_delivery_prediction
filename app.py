
import streamlit as st
import pandas as pd
import numpy as np
import joblib
from math import sin, cos, pi

# Load model
model_pipeline = joblib.load("late_delivery_predictor_model.pkl")

st.set_page_config(page_title="Food Delivery Delay Predictor", layout="centered")
st.title("🚚 Food Delivery Delay Predictor")

st.markdown("Simulate a new delivery scenario:")

prep_time = st.slider("Preparation Time (min)", 5, 60, 20)
restaurant_rating = st.slider("Restaurant Rating", 3.0, 5.0, 4.0)
delivery_person_rating = st.slider("Delivery Person Rating", 4.0, 5.0, 4.5)
delivery_distance_km = st.slider("Delivery Distance (km)", 0.1, 40.0, 5.0)
order_hour = st.slider("Order Hour (0-23)", 0, 23, 12)
traffic_density = st.selectbox("Traffic Density", ["Low", "Medium", "High", "Jam"])
weather_condition = st.selectbox("Weather Condition", ["Clear", "Rainy", "Foggy", "Stormy"])
current_temp_c = st.slider("Current Temperature (°C)", 10, 40, 25)

sin_hour = sin(2 * pi * order_hour / 24)
cos_hour = cos(2 * pi * order_hour / 24)

input_df = pd.DataFrame({
    'delivery_distance_km': [delivery_distance_km],
    'preparation_time_min': [prep_time],
    'restaurant_rating': [restaurant_rating],
    'delivery_person_rating': [delivery_person_rating],
    'Road_Traffic_Density': [traffic_density],
    'Weather_Condition': [weather_condition],
    'sin_hour': [sin_hour],
    'cos_hour': [cos_hour],
    'current_temp_c': [current_temp_c]
})

if st.button("Predict Delay"):
    proba = model_pipeline.predict_proba(input_df)[0][1] * 100
    if proba > 60:
        st.error(f"❌ High risk of late delivery ({proba:.2f}%)")
    elif proba > 40:
        st.warning(f"⚠ Moderate risk of late delivery ({proba:.2f}%)")
    else:
        st.success(f"✅ Low risk of late delivery ({proba:.2f}%)")
