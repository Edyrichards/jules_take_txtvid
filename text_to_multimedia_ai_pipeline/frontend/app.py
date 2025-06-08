import streamlit as st
import requests

st.title("Text-to-Multimedia AI Pipeline")

st.header("Backend Status")

backend_url = "http://localhost:8000/health"  # Assuming backend runs on port 8000

try:
    response = requests.get(backend_url)
    if response.status_code == 200:
        status = response.json().get("status", "unknown")
        st.success(f"Backend is {status}!")
    else:
        st.error(f"Backend returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    st.error("Failed to connect to the backend. Ensure it's running.")
except Exception as e:
    st.error(f"An error occurred: {e}")
