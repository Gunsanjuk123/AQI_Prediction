import streamlit as st
import pandas as pd
import pickle

# Load the trained model
with open('aqi_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# CSS for styling
st.markdown(
    """
    <style>
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f9f9f9;
    }
    .main-title {
        text-align: center;
        font-size: 36px;
        color: red;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .sub-title {
        text-align: center;
        font-size: 18px;
        color: #555555;
        margin-bottom: 30px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin: 10px 0;
    }
    .card-header {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .alert {
        padding: 15px;
        font-size: 18px;
        text-align: center;
        border-radius: 5px;
        margin-top: 20px;
    }
    .progress-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 15px 0;
    }
    .progress-bar-fill {
        height: 100%;
        transition: width 0.3s ease;
    }
    .suffocate-alert {
        color: #ffffff;
        background-color: #c0392b;
        font-weight: bold;
        padding: 10px;
        text-align: center;
        border-radius: 5px;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Header
st.markdown('<div class="main-title">AQI Prediction Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Monitor real-time air quality predictions</div>', unsafe_allow_html=True)

# Sidebar Inputs
st.header("Input Parameters")
aqi_categories = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']

# Create equally spaced columns for input fields
col1, col2, col3 = st.columns(3)

with col1:
    CO_AQI_Value = st.slider("CO AQI Value", 300.0, 1000.0, 350.0, step=10.0)

with col2:
    Ozone_AQI_Value = st.slider("Ozone AQI Value", 0.0, 500.0, 50.0, step=0.1)

with col3:
    Ozone_AQI_Category = st.selectbox("Ozone AQI Category", aqi_categories)

col4, col5, col6 = st.columns(3)

with col4:
    NO2_AQI_Value = st.slider("NO2 AQI Value", 0.0, 500.0, 50.0, step=0.1)

with col5:
    PM25_AQI_Value = st.slider("PM10 AQI Value", 0.0, 500.0, 50.0, step=0.1)

# Convert Categories to Numeric Indices
def category_to_numeric(category, categories):
    return categories.index(category)

# Live Prediction
input_data = pd.DataFrame({
    'CO AQI Value': [CO_AQI_Value],
    'Ozone AQI Value': [Ozone_AQI_Value],
    'Ozone AQI Category': [category_to_numeric(Ozone_AQI_Category, aqi_categories)],
    'NO2 AQI Value': [NO2_AQI_Value],
    'PM2.5 AQI Value': [PM25_AQI_Value],
})

# Define AQI thresholds and alert messages
def get_alert(aqi_value):
    if aqi_value <= 50:
        return "Good", "Good Air Quality: Predicted AQI Value is {:.2f}".format(aqi_value), "#2ecc71"
    elif aqi_value <= 100:
        return "Moderate", "Moderate Air Quality: Predicted AQI Value is {:.2f}".format(aqi_value), "#f1c40f"
    elif aqi_value <= 200:
        return "Poor", "Poor Air Quality: Predicted AQI Value is {:.2f}".format(aqi_value), "#e67e22"
    elif aqi_value <= 300:
        return "Unhealthy", "Unhealthy Air Quality: Predicted AQI Value is {:.2f}".format(aqi_value), "#e74c3c"
    elif aqi_value <= 400:
        return "Severe", "Severe Air Quality: Predicted AQI Value is {:.2f}".format(aqi_value), "#8e44ad"
    else:
        return "Hazardous", "Hazardous Air Quality: Predicted AQI Value is {:.2f}".format(aqi_value), "#c0392b"

# Prediction and Alert
prediction = model.predict(input_data)[0]
alert_category, alert_message, alert_color = get_alert(prediction)

# Display Results
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card-header">Prediction Result</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="alert" style="background-color: {alert_color}; color: #ffffff; border-radius: 5px; padding: 15px; text-align: center; font-size: 18px; font-weight: bold;">'
        f'{alert_message}</div>',
        unsafe_allow_html=True,
    )

with col2:
    progress_percentage = min(prediction / 510 * 100, 100)  # Scale AQI (max 510+)
    st.markdown(
        f"""
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width: {progress_percentage}%; background-color: {alert_color};"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Separate column for suffocation alert, shown only for "Unhealthy" or worse
if prediction >= 200:
    suffocation_message = "Warning: The air quality is unhealthy and may cause suffocation risks!"
    st.markdown(
        f'<div class="suffocate-alert">{suffocation_message}</div>',
        unsafe_allow_html=True,
    )
