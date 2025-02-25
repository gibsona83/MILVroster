import streamlit as st
import pandas as pd
import os
import re
import requests
from io import StringIO

# ✅ Must be the first Streamlit command!
st.set_page_config(page_title="MILV Provider Directory", page_icon="🏥", layout="wide")

# Load CSV file from GitHub raw URL
GITHUB_FILE_URL = "https://raw.githubusercontent.com/gibsona83/MILVroster/main/MILVProvider.csv"

# ✅ Load Data Function
@st.cache_data(ttl=600)
def load_data():
    try:
        response = requests.get(GITHUB_FILE_URL, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# ✅ Load data from GitHub
df = load_data()

# ✅ Ensure Data Is Loaded
if df is None or df.empty:
    st.error("Failed to load data. Please check the GitHub source.")
    st.stop()

# ✅ Fix NaN Values
df = df.fillna("")

# ✅ Ensure Required Columns Exist
required_columns = ['MILV Radiologist/Extender', 'Employment Type', 'Subspecialty']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# ✅ UI Styling
st.markdown(
    """
    <style>
        .stApp {
            background-color: #f5f7fa;
            color: #002F6C;
        }
        .stTextInput, .stMultiSelect, .stDownloadButton {
            background-color: #ffffff !important;
            color: #002F6C !important;
        }
        h1 {
            color: #002F6C;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("MILV Provider Directory")

# ✅ Search & Filter Options
search_name = st.text_input("Search by Provider Name", "")

# ✅ Get Unique Employment Type List
employment_type_options = sorted(df['Employment Type'].dropna().unique())
employment_type = st.multiselect("Filter by Employment Type", options=employment_type_options)

# ✅ Get Unique Subspecialty List
subspecialty_options = sorted(set(
    sub for subs in df['Subspecialty'] for sub in subs.split(', ')
))
subspecialty = st.multiselect("Filter by Subspecialty", options=subspecialty_options)

# ✅ Apply Filters
filtered_df = df.copy()

if search_name:
    filtered_df = filtered_df[
        filtered_df['MILV Radiologist/Extender'].str.contains(search_name, case=False, na=False)
    ]

if employment_type:
    filtered_df = filtered_df[filtered_df['Employment Type'].isin(employment_type)]

if subspecialty:
    filtered_df = filtered_df[
        filtered_df['Subspecialty'].apply(lambda x: any(sub in x for sub in subspecialty))
    ]

# ✅ Display Filtered Data
st.write(f"Showing {len(filtered_df)} of {len(df)} providers")

if len(filtered_df) > 0:
    st.data_editor(filtered_df, use_container_width=True, height=500)
else:
    st.warning("No matching providers found.")

# ✅ Download Button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Filtered Data", csv, "filtered_providers.csv", "text/csv")
