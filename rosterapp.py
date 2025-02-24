import streamlit as st
import pandas as pd
import os

# ✅ Must be the first Streamlit command!
st.set_page_config(page_title="MILV Physician Roster", page_icon="🏥", layout="wide")

# Load Excel file from GitHub raw URL
file_url = "https://raw.githubusercontent.com/gibsona83/MILVroster/main/MILV%20-%20Provider%20Worksheet.xlsx"

# Function to load data
@st.cache_data
def load_data():
    df = pd.read_excel(file_url, sheet_name='Providers', engine='openpyxl')
    return df

# Load the data
df = load_data()

# Ensure cleaned categories are correctly reflected in dropdowns
employment_type_options = sorted(df['Employment Type'].dropna().unique())
subspecialty_options = sorted(df['Subspecialty'].dropna().unique())

# Load and display the logo
logo_path = "milv.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=300)

# Updated UI Styling for better readability
st.markdown("""
    <style>
        .stApp {
            background-color: #f5f7fa;
            color: #002F6C;
        }
        .stTextInput, .stMultiSelect, .stDownloadButton, .stDataFrame {
            background-color: #ffffff !important;
            color: #002F6C !important;
        }
        h1 {
            color: #002F6C;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("MILV Physician Roster")

# Search and Filter Options
search_name = st.text_input("Search by Provider Name", "")
employment_type = st.multiselect("Filter by Employment Type", options=employment_type_options)
subspecialty = st.multiselect("Filter by Subspecialty", options=subspecialty_options)

# Filtering Logic
filtered_df = df.copy()
if search_name:
    filtered_df = filtered_df[filtered_df['MILV Radiologist/Extender'].str.contains(search_name, case=False, na=False)]
if employment_type:
    filtered_df = filtered_df[filtered_df['Employment Type'].isin(employment_type)]
if subspecialty:
    filtered_df = filtered_df[filtered_df['Subspecialty'].isin(subspecialty)]

# Display Data
st.write(f"Showing {len(filtered_df)} of {len(df)} providers")
st.dataframe(filtered_df)

# Download Button
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Filtered Data", csv, "filtered_providers.csv", "text/csv")
