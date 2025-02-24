import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="MILV Physician Roster", page_icon="🏥", layout="wide")

GITHUB_FILE_URL = "https://raw.githubusercontent.com/gibsona83/MILVroster/main/MILV%20-%20Provider%20Worksheet.xlsx"

@st.cache_data(ttl=600)  # Cache expires every 10 minutes
def load_data():
    try:
        st.write("Loading data from GitHub...")  # Debug message
        df = pd.read_excel(GITHUB_FILE_URL, sheet_name='Providers', engine='openpyxl')
        st.write("Data loaded successfully!")  # Debug message
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is None or df.empty:
    st.error("Failed to load data. Please check the GitHub source.")
    st.stop()
